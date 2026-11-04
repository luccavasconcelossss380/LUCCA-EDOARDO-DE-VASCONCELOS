"""Uma entrada, quatro atividades, o mesmo laboratório."""
import streamlit as st

st.set_page_config(page_title="Computação Gráfica · Lucca", page_icon="◧", layout="wide")
st.markdown("""<style>
.block-container {max-width:1250px; padding-top:2.6rem; padding-bottom:4rem;}
h1 {letter-spacing:-.045em; font-weight:750 !important;}
h2 {letter-spacing:-.025em;}
[data-testid="stSidebar"] {border-right:1px solid #e0e5ed;}
[data-testid="stMetric"] {background:#fff; border:1px solid #e0e5ed;
 border-radius:12px; padding:15px;}
[data-testid="stImage"] img {border-radius:7px;}
.eyebrow {font-size:.75rem; letter-spacing:.16em; color:#53709b; font-weight:700;}
.intro {color:#5e6a7c; font-size:1.06rem; max-width:760px; margin-bottom:1.6rem;}
.brand {font-weight:800; font-size:1.35rem; letter-spacing:-.04em;}
.brand small {font-size:.7rem; letter-spacing:.14em; color:#62718a;}
</style>""", unsafe_allow_html=True)
with st.sidebar:
    st.markdown('<div class="brand">Computação Gráfica</div>', unsafe_allow_html=True)

paginas = [
    st.Page("src/atv1.py", title="Atv 1 · Primeiro app", icon=":material/apps:", default=True),
    st.Page("src/atv2.py", title="Atv 2 · Matriz e bandeira", icon=":material/grid_on:"),
    st.Page("src/atv3.py", title="Atv 3 · Padrões", icon=":material/texture:"),
    st.Page("src/atv4.py", title="Atv 4 · Cor e canais", icon=":material/palette:"),
]
pagina = st.navigation(paginas)
st.markdown("**Lucca Edoardo de Vasconcelos**")
pagina.run()
