from datetime import datetime
from importlib.metadata import version, PackageNotFoundError
from io import BytesIO
from pathlib import Path
import platform
import shutil
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED
from zoneinfo import ZoneInfo
import streamlit as st
from src.componentes import RAIZ
from src.processamento import ler_foto, png
from src.relatorio import PASSOS, gerar_relatorio


def executar(comando):
    try:
        resultado = subprocess.run(comando, cwd=RAIZ, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=12,
                                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return (resultado.stdout or resultado.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as erro:
        return f"Não verificado: {erro}"


def coletar_ambiente():
    dados = {"Python em execução": platform.python_version(), "Pasta do projeto": str(RAIZ)}
    for nome, args in (("uv", ["--version"]), ("Git", ["--version"]), ("VS Code", ["--version"])):
        exe = shutil.which({"Git": "git", "VS Code": "code"}.get(nome, nome))
        # No Windows, code costuma ser .cmd. Não passamos conteúdo do usuário ao shell.
        if exe and Path(exe).suffix.lower() not in (".cmd", ".bat"):
            dados[nome] = executar([exe, *args]).splitlines()[0]
        elif exe:
            dados[nome] = f"Executável encontrado: {exe}"
        else:
            dados[nome] = "Não encontrado no PATH"
    for biblioteca in ("streamlit", "numpy", "opencv-python-headless", "matplotlib", "pillow", "python-docx"):
        try:
            dados[biblioteca] = version(biblioteca)
        except PackageNotFoundError:
            dados[biblioteca] = "Não instalada"
    git = shutil.which("git")
    if git:
        dados["Nome no Git"] = executar([git, "config", "user.name"]) or "Não configurado"
        dados["Raiz do Git"] = executar([git, "rev-parse", "--show-toplevel"])
    return dados


def pacote_projeto():
    memoria = BytesIO()
    with ZipFile(memoria, "w", ZIP_DEFLATED) as pacote:
        arquivos = [RAIZ / nome for nome in ("app.py", "main.py", "pyproject.toml", "uv.lock", ".python-version", ".gitignore")]
        for pasta in ("src", ".streamlit", "imagens", "tests"):
            arquivos.extend(p for p in (RAIZ / pasta).rglob("*") if p.is_file() and "__pycache__" not in p.parts)
        for arquivo in arquivos:
            if arquivo.is_file():
                pacote.write(arquivo, "laboratorio-cg/" + arquivo.relative_to(RAIZ).as_posix())
    return memoria.getvalue()


def exibir_ambiente():
    st.subheader("Ambiente de trabalho")
    st.write("Python 3.12, dependências no uv e um arquivo por atividade em src/. O menu mantém tudo no mesmo app.")
    if st.button("Verificar ferramentas e bibliotecas"):
        with st.spinner("Conferindo versões locais…"):
            st.session_state["diagnostico_cg"] = coletar_ambiente()
    if "diagnostico_cg" in st.session_state:
        dados = st.session_state["diagnostico_cg"]
        st.dataframe({"Item": list(dados), "Resultado observado": list(dados.values())}, hide_index=True, width="stretch")
        if dados.get("Raiz do Git", "").replace("\\", "/").casefold() != RAIZ.as_posix().casefold():
            st.info("Esta pasta não tem um repositório Git independente. Para publicar apenas o laboratório, baixe o ZIP abaixo e extraia em uma pasta separada antes de iniciar o Git.")
    with st.expander("Comandos para preparar e executar"):
        st.code("uv python install 3.12\nuv sync\nuv run streamlit run app.py", language="powershell")
        st.caption("Para uma cópia existente do projeto. O uv.lock fixa as versões utilizadas.")
        st.code("code --install-extension ms-python.python\ncode --install-extension ms-toolsai.jupyter", language="powershell")
    st.download_button("Baixar projeto completo em ZIP", pacote_projeto(), "laboratorio-cg.zip", "application/zip")
    st.divider()
    st.subheader("Relatório de instalação · 12 tópicos e 10 prints")
    st.caption("Preencha seus dados e anexe os prints reais. O gerador inclui legendas e comandos como texto no Word. O modelo institucional citado nos slides não foi fornecido.")
    col1, col2 = st.columns(2)
    nome = col1.text_input("Nome do aluno", "Luca", key="rel_nome")
    turma = col2.text_input("Turma", key="rel_turma")
    repo = st.text_input("Link do repositório da disciplina", placeholder="https://github.com/organizacao/laboratorio-cg-usuario", key="rel_repo")
    evidencias, observacoes = {}, {}
    for i, (titulo, comandos, legenda) in enumerate(PASSOS):
        with st.expander(f"Print {i + 1} · {titulo}"):
            st.write(legenda)
            st.code(comandos, language="text")
            arquivo = st.file_uploader(f"Print {i + 1}", type=["png", "jpg", "jpeg"], key=f"print_{i}")
            if arquivo:
                try:
                    normalizada = ler_foto(arquivo.getvalue())
                    evidencias[i] = png(normalizada)
                    st.image(normalizada, width=500)
                except (OSError, ValueError) as erro:
                    st.error(f"Não foi possível ler o print: {erro}")
            observacoes[i] = st.text_area("Observação ou legenda complementar", key=f"observacao_{i}")
    conclusao = st.text_area("Conclusão do relatório", placeholder="Descreva o que funcionou e eventuais dificuldades.", key="rel_conclusao")
    st.progress(len(evidencias) / 10, text=f"{len(evidencias)} de 10 prints anexados")
    completo = len(evidencias) == 10 and bool(nome.strip() and turma.strip() and repo.strip() and conclusao.strip())
    if st.button("Preparar relatório Word"):
        dados = gerar_relatorio(nome, turma, repo, evidencias, observacoes, conclusao,
                               data=datetime.now(ZoneInfo("America/Sao_Paulo")).date())
        st.download_button("Baixar relatório.docx" if completo else "Baixar rascunho.docx", dados,
                           "relatorio-instalacao.docx" if completo else "rascunho-instalacao.docx",
                           "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        if not completo:
            st.caption("Rascunho: confira os dados, a conclusão e os 10 prints antes de entregar.")
    with st.expander("Registro e publicação das atividades"):
        st.write("Use um repositório próprio para o laboratório, no owner e com o nome pedidos pela disciplina. Configure o Git com seu nome e e-mail antes do primeiro commit.")
        st.code('git init\ngit add .\ngit commit -m "Adiciona atividades 1 a 4 de computacao grafica"\n'
                'git remote add origin URL_DO_REPOSITORIO_DA_DISCIPLINA\ngit branch -M main\ngit push -u origin main\ngit log --oneline -1', language="powershell")
        st.caption("Execute esses comandos apenas na cópia independente. Na atividade 3, registre a fórmula escolhida na mensagem do commit e informe o hash no formulário. Confira se imagens/foto.jpg está no repositório.")
