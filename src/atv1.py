import numpy as np
import streamlit as st
from src.componentes import abertura, baixar
from src.processamento import ampliar

abertura(1, "Imagem como matriz")
esquerda, direita = st.columns([1, 1.4], gap="large")
with esquerda:
    n = st.slider("Tamanho", 2, 64, 8, key="tamanho_inicial")
    modo = st.radio("Preenchimento", ["Cinza uniforme · 128", "Valores aleatórios"], key="modo_inicial")
    imagem = (np.full((n, n), 128, dtype=np.uint8) if modo.startswith("Cinza")
              else np.random.default_rng(42).integers(0, 256, (n, n), dtype=np.uint8))
    baixar(imagem, "atv1-pixels.png", "baixar_primeiro")
with direita:
    st.image(ampliar(imagem, max(1, 320 // n)), caption=f"{n} × {n} pixels", width=360)
st.dataframe(imagem, width="stretch")
