"""Relatório com evidências reais anexadas pelo aluno, sem simular prints."""
from io import BytesIO
from datetime import date
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from PIL import Image, ImageOps

PASSOS = [
    ("uv", "uv --version", "Versão do gerenciador de projetos e dependências."),
    ("Python 3 12", "uv python install 3.12\nuv python list --only-installed", "Python 3.12 instalado e disponível pelo uv."),
    ("Git", 'git --version\ngit config --global user.name "Seu Nome"\ngit config --global user.email "seu@email.com"\ngit config --global init.defaultBranch main', "Git instalado e configurado com a identificação do aluno."),
    ("Conta no GitHub", "https://github.com/", "Perfil da conta com e-mail confirmado."),
    ("Visual Studio Code", "code --version\ncode --list-extensions", "Editor com as extensões Microsoft Python e Jupyter."),
    ("Projeto laboratorio cg", "uv init --python 3.12 laboratorio-cg\ncd laboratorio-cg", "Estrutura inicial da pasta do projeto."),
    ("Bibliotecas", "uv add streamlit numpy opencv-python-headless matplotlib pillow\nuv tree --depth 1", "Dependências declaradas em pyproject.toml e travadas em uv.lock."),
    ("Primeiro app Streamlit", "uv run streamlit run app.py", "App executando no navegador com nome, imagem e controle de tamanho."),
    ("Primeiro commit", 'git status\ngit add app.py src imagens .streamlit pyproject.toml uv.lock .python-version\ngit commit -m "Adiciona laboratorio de computacao grafica"\ngit log --oneline -1', "Histórico do repositório da atividade, com o primeiro commit."),
    ("Publicação no GitHub", "git remote add origin URL_DO_REPOSITORIO_DA_DISCIPLINA\ngit branch -M main\ngit push -u origin main", "Repositório da disciplina mostrando os arquivos publicados."),
]


def gerar_relatorio(nome, turma, repositorio, evidencias, observacoes, conclusao, data=None):
    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Inches(8.27), Inches(11.69)
    section.top_margin = section.bottom_margin = Inches(0.8)
    section.left_margin = section.right_margin = Inches(0.85)
    for estilo in ("Normal", "Title", "Heading 1", "Heading 2"):
        doc.styles[estilo].font.name = "Calibri"
        doc.styles[estilo].font.color.rgb = RGBColor(0, 0, 0)
    doc.styles["Normal"].font.size = Pt(11)
    doc.styles["Normal"].paragraph_format.space_after = Pt(8)
    doc.styles["Title"].font.size = Pt(28)
    doc.styles["Heading 1"].font.size = Pt(19)
    doc.add_paragraph("Relatório de instalação do laboratório de Computação Gráfica", "Title")
    doc.add_heading("1 Identificação e objetivo", 1)
    doc.add_paragraph(f"Aluno: {nome}\nTurma: {turma or 'A preencher'}\nData: {(data or date.today()).strftime('%d/%m/%Y')}")
    doc.add_paragraph(f"Repositório: {repositorio or 'A preencher'}")
    doc.add_paragraph("Este relatório reúne os comandos e as evidências do ambiente utilizado nas atividades de Computação Gráfica. Cada etapa possui um espaço para o print correspondente e sua legenda.")
    doc.add_paragraph(f"Evidências anexadas: {len(evidencias)} de 10.")
    for i, (titulo, comandos, legenda) in enumerate(PASSOS):
        doc.add_page_break()
        doc.add_heading(f"{i + 2} {titulo}", 1)
        doc.add_paragraph(legenda)
        doc.add_paragraph("Comandos e endereço de referência", "Heading 2")
        p = doc.add_paragraph()
        run = p.add_run(comandos)
        run.font.name, run.font.size = "Consolas", Pt(9)
        if i in evidencias:
            with Image.open(BytesIO(evidencias[i])) as fonte:
                im = ImageOps.exif_transpose(fonte).convert("RGB")
                imagem = BytesIO()
                im.save(imagem, format="PNG")
                imagem.seek(0)
                largura = min(6.3, 4.1 * im.width / im.height)
                doc.add_picture(imagem, width=Inches(largura))
            doc.add_paragraph(f"Figura {i + 1} - {legenda}", "Caption")
        else:
            doc.add_paragraph(f"Print {i + 1}: anexar a evidência desta etapa.")
        if observacoes.get(i):
            doc.add_paragraph(observacoes[i])
    doc.add_page_break()
    doc.add_heading("12 Conclusão", 1)
    doc.add_paragraph(conclusao or "Preencher com os resultados observados e as dificuldades encontradas durante a instalação.")
    doc.add_paragraph("Referência: Encontro 02 - Lab 0, Prof. Eron Ponce Pereira, material da disciplina.")
    saida = BytesIO()
    doc.save(saida)
    return saida.getvalue()
