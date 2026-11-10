from pathlib import Path
import streamlit as st
from src.processamento import png

RAIZ = Path(__file__).resolve().parents[1]


def abertura(numero, titulo):
    st.title(f"Atividade {numero} · {titulo}")


def baixar(imagem, nome, key):
    st.download_button("Baixar PNG", data=png(imagem), file_name=nome, mime="image/png", key=key)


