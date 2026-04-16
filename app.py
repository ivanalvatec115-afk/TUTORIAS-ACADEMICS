import streamlit as st
from utils.styles import inject_global_css
from pages import login, alumno, docente

st.set_page_config(
    page_title="TutorIA — Tutorías Académicas",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_css()

defaults = {
    "authenticated": False,
    "role": None,
    "user_id": None,
    "user_name": "",
    "page": "login",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def main():
    page = st.session_state["page"]
    if page == "login":
        login.render()
    elif page == "alumno":
        alumno.render()
    elif page == "docente":
        docente.render()
    else:
        st.session_state["page"] = "login"
        st.rerun()

if __name__ == "__main__":
    main()
