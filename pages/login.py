import streamlit as st
from utils.auth import login_alumno, login_docente


def render():
    _, center, _ = st.columns([1, 2.6, 1])

    with center:
        st.markdown(
            """
            <div style="
                background:#1e3a5f;
                border-radius:24px 24px 0 0;
                padding:2.2rem 2.5rem 1.8rem;
                color:white;
                text-align:center;
            ">
                <div style="font-size:3rem; margin-bottom:.6rem;">🎓</div>
                <h1 style="font-size:1.9rem; font-weight:700; margin:0 0 .6rem;">TutorIA</h1>
                <p style="opacity:.88; font-size:.95rem; line-height:1.6; margin:0;">
                    Plataforma centralizada de Tutorías Académicas<br>
                    <em>Instituto Tecnológico de Matehuala</em>
                </p>
                <div style="margin-top:1rem; font-size:.83rem; opacity:.75;">
                    ✅ Trazabilidad de requisitos &nbsp;·&nbsp;
                    📅 Calendario interactivo &nbsp;·&nbsp;
                    📊 Reportes académicos
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="
                background:white;
                border-radius:0 0 24px 24px;
                padding:2rem 2.5rem 2.2rem;
                border:1px solid #e2e8f0;
                border-top:none;
                box-shadow:0 12px 30px rgba(0,0,0,.10);
            ">
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<h2 style='color:#1e2a3a;font-size:1.5rem;margin-bottom:.25rem;'>Acceder</h2>"
            "<p style='color:#5b6e8c;font-size:.9rem;margin-bottom:1.2rem;'>Selecciona tu rol e ingresa tus credenciales</p>",
            unsafe_allow_html=True,
        )

        role = st.selectbox(
            "Rol de usuario",
            options=["alumno", "docente"],
            format_func=lambda x: "🎒 Alumno" if x == "alumno" else "🏫 Docente / Tutor",
            key="login_role",
        )

        if role == "alumno":
            identifier = st.text_input("Número de control", placeholder="Ej. 23660408", key="login_id")
        else:
            identifier = st.text_input("Nombre o ID de docente", placeholder="Ej. Juan Robles  ó  1", key="login_id")

        password = st.text_input("Contraseña", type="password", placeholder="••••••••", key="login_pass")

        if st.button("Ingresar →", type="primary", use_container_width=True):
            if not identifier or not password:
                st.error("Completa todos los campos.")
            else:
                with st.spinner("Verificando…"):
                    user = login_alumno(identifier, password) if role == "alumno" else login_docente(identifier, password)

                if user:
                    st.session_state["authenticated"] = True
                    st.session_state["role"]      = role
                    st.session_state["user_id"]   = user.get("id_alumno") or user.get("id_profesor")
                    st.session_state["user_name"] = user["nombre_completo"]
                    st.session_state["page"]      = role
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas.")

        st.markdown(
            "<p style='font-size:.75rem;color:#94a3b8;text-align:center;margin-top:.8rem;'>"
            "💡 Contraseñas demo: alumnos → <code>alumno123</code> · docentes → <code>docente123</code>"
            "</p>",
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)
