import hashlib
import warnings
import numpy as np
import streamlit as st
from PIL import Image, UnidentifiedImageError
from src.componentes import RAIZ, abertura, baixar
from src.processamento import demonstracao, editar_rgb, ler_foto, separar_canais, tons_cinza


def restaurar_ajustes():
    for chave, valor in (("foto_r", 100), ("foto_g", 100), ("foto_b", 100), ("foto_brilho", 0), ("foto_modo", "RGB")):
        st.session_state[chave] = valor


abertura(4, "Cor e canais")
foto_local = RAIZ / "imagens" / "foto.jpg"
with st.expander("Trocar foto"):
    upload = st.file_uploader("Foto", type=["jpg", "jpeg", "png", "webp"], key="upload_foto")
    if upload is not None:
        dados = upload.getvalue()
        assinatura = hashlib.sha256(dados).hexdigest()
        if assinatura != st.session_state.get("assinatura_foto"):
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("error", Image.DecompressionBombWarning)
                    nova = ler_foto(dados)
                st.session_state["foto_rgb"] = nova
                st.session_state["nome_foto_rgb"] = upload.name
                st.session_state["assinatura_foto"] = assinatura
            except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
                st.error("Não foi possível abrir essa imagem.")

    if "foto_rgb" in st.session_state and st.button("Salvar foto no projeto"):
        foto_local.parent.mkdir(exist_ok=True)
        temporaria = foto_local.with_suffix(".tmp")
        Image.fromarray(st.session_state["foto_rgb"]).save(temporaria, format="JPEG", quality=95)
        temporaria.replace(foto_local)
        st.session_state["foto_rgb"] = ler_foto(foto_local.read_bytes())
        st.success("Foto salva.")

if "foto_rgb" in st.session_state:
    original = st.session_state["foto_rgb"]
elif foto_local.exists():
    try:
        original = ler_foto(foto_local.read_bytes())
    except (OSError, ValueError, Image.DecompressionBombError):
        original = demonstracao()
        st.info("Foto indisponível. Exibindo demonstração.")
else:
    original = demonstracao()
    st.info("Envie uma foto. Exibindo demonstração.")

st.header("1. Foto")
for chave, valor in (("foto_r", 100), ("foto_g", 100), ("foto_b", 100), ("foto_brilho", 0), ("foto_modo", "RGB")):
    if chave not in st.session_state:
        st.session_state[chave] = valor
c1, c2, c3, c4 = st.columns(4)
r = c1.slider("Vermelho (%)", 0, 200, key="foto_r")
g = c2.slider("Verde (%)", 0, 200, key="foto_g")
b = c3.slider("Azul (%)", 0, 200, key="foto_b")
brilho = c4.slider("Brilho", -100, 100, key="foto_brilho")
modo = st.radio("Visualização", ["RGB", "BGR", "Cinza médio", "Cinza ponderado"], horizontal=True, key="foto_modo")
img = editar_rgb(original, r, g, b, brilho)
media, ponderada = tons_cinza(img)
resultado = {"RGB": img, "BGR": img[:, :, ::-1], "Cinza médio": media, "Cinza ponderado": ponderada}[modo]
col1, col2 = st.columns(2, gap="large")
col1.image(original, caption="Original", width="stretch")
col2.image(resultado, caption="Resultado", width="stretch")
botao1, botao2 = st.columns(2)
with botao1:
    st.button("Restaurar ajustes", on_click=restaurar_ajustes)
with botao2:
    baixar(resultado, "atv4-foto-editada.png", "baixar_editada")
st.caption(f"{original.shape[1]} × {original.shape[0]} pixels · 3 canais")
if original.shape[0] > 100 and original.shape[1] > 100:
    st.caption(f"Pixel (100, 100) · RGB {tuple(int(v) for v in img[100, 100])}")

st.header("2. Canais")
col1, col2 = st.columns(2, gap="large")
for i, (nome, separado) in enumerate(zip(("R", "G", "B"), separar_canais(img))):
    col1.image(img[:, :, i], caption=nome, width="stretch")
    col2.image(separado, caption=f"Só {nome}", width="stretch")

st.header("3. Cubo e BGR")
col1, col2 = st.columns(2, gap="large")
with col1:
    cores = (("Amarelo", (255, 255, 0)), ("Ciano", (0, 255, 255)),
             ("Magenta", (255, 0, 255)), ("Branco", (255, 255, 255)))
    for coluna, (nome, cor) in zip(st.columns(4), cores):
        coluna.image(np.full((80, 80, 3), cor, dtype=np.uint8), caption=nome, width="stretch")
        coluna.caption(str(cor))
col2.image(img, channels="BGR", caption="BGR", width="stretch")

st.header("4. Tons de cinza")
col1, col2 = st.columns(2, gap="large")
col1.image(media, caption="Média simples", width="stretch")
col2.image(ponderada, caption="Média ponderada", width="stretch")
