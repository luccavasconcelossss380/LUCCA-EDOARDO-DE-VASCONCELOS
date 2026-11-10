import streamlit as st
from src.componentes import abertura, baixar
from src.processamento import ampliar, criar_bandeira, hex_rgb


def restaurar_cores():
    for nome, valor in (("Azul", "#002B7F"), ("Amarelo", "#FCD116"), ("Vermelho", "#CE1126")):
        st.session_state[f"bandeira_{nome}"] = valor


abertura(2, "Bandeira da Romênia")
controles, resultado = st.columns([1, 1.5], gap="large")
with controles:
    altura = st.slider("Altura em pixels", 6, 30, 12, step=2)
    largura = altura * 3 // 2
    cores = []
    for nome, padrao in (("Azul", "#002B7F"), ("Amarelo", "#FCD116"), ("Vermelho", "#CE1126")):
        chave = f"bandeira_{nome}"
        if chave not in st.session_state:
            st.session_state[chave] = padrao
        cor = st.color_picker(nome, key=chave)
        cores.append(hex_rgb(cor))
        st.caption(f"RGB {cores[-1]}")
    st.button("Restaurar cores da bandeira", on_click=restaurar_cores)
with resultado:
    bandeira = criar_bandeira(altura, largura, cores)
    st.image(ampliar(bandeira), caption=f"{altura} × {largura} pixels", width="stretch")
    if len(set(cores)) < 3:
        st.info("Escolha três cores diferentes.")
    baixar(bandeira, "atv2-bandeira.png", "baixar_bandeira")
