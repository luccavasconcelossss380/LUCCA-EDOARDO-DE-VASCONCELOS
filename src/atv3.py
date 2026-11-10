import numpy as np
import streamlit as st
from src.componentes import abertura, baixar
from src.processamento import ampliar, padrao

abertura(3, "Estrela geométrica")
controles, preview = st.columns([1, 1.5], gap="large")
with controles:
    k = st.slider("k", 1, 20, 4, key="padrao_k")
    y, x = np.indices((64, 64))
    imagem = padrao(x, y, k).astype(np.uint8)
    baixar(imagem, "atv3-estrela.png", "baixar_padrao")
with preview:
    st.image(ampliar(imagem, 6), caption="64 × 64 pixels", width=448)
