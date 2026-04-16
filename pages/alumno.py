import streamlit as st
from datetime import datetime, date, time
from supabase_client import get_supabase
from utils.auth import logout
from utils.styles import render_header, section_title, badge


def _sb():
    return get_supabase()


@st.cache_data(ttl=30, show_spinner=False)
def fetch_disponibilidad():
    return (
        _sb().table("disponibilidad")
        .select("id_disponibilidad, lugar, profesor(id_profesor, nombre_completo)")
        .eq("activo", True)
        .execute().data or []
    )


@st.cache_data(ttl=30, show_spinner=False)
def fetch_materias():
    return _sb().table("materia").select("id_materia, nombre_materia, clave_materia").execute().data or []


@st.cache_data(ttl=20, show_spinner=False)
def fetch_mis_tutorias(id_alumno: int):
    return (
        _sb().table("tutoria")
        .select(
            "id_tutoria, horario, estado,"
            "profesor(nombre_completo),"
            "materia(nombre_materia),"
            "registro_asistencia(asistio_alumno, calificacion_tutoria, notas_docente)"
        )
        .eq("id_alumno", id_alumno)
        .order("horario", desc=True)
        .execute().data or []
    )


def fetch_profesores():
    return _sb().table("profesor").select("id_profesor, nombre_completo").eq("activo", True).execute().data or []


def agendar_tutoria(id_alumno, id_profesor, id_materia, horario_dt):
    resp = _sb().table("tutoria").insert({
        "id_alumno":   id_alumno,
        "id_profesor": id_profesor,
        "id_materia":  id_materia,
        "horario":     horario_dt.isoformat(),
        "estado":      "programada",
    }).execute()
    return resp.data


def cancelar_tutoria(id_tutoria: int):
    _sb().table("tutoria").update({"estado": "cancelada"}).eq("id_tutoria", id_tutoria).execute()
    fetch_mis_tutorias.clear()


def _fmt(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return iso or "—"


def render():
    if not st.session_state.get("authenticated") or st.session_state.get("role") != "alumno":
        st.session_state["page"] = "login"
        st.rerun()

    id_alumno = st.session_state["user_id"]
    user_name = st.session_state["user_name"]

    render_header("Tutorías Académicas", "Alumno", user_name)

    _, col_logout = st.columns([9, 1])
    with col_logout:
        if st.button("Salir 🚪", key="logout_a"):
            logout()
            st.rerun()

    # ── Stats ────────────────────────────────────────────────────
    tutorias    = fetch_mis_tutorias(id_alumno)
    programadas = sum(1 for t in tutorias if t["estado"] == "programada")
    completadas = sum(1 for t in tutorias if t["estado"] == "completada")
    canceladas  = sum(1 for t in tutorias if t["estado"] == "cancelada")

    for col, num, lbl, color in zip(
        st.columns(4),
        [len(tutorias), programadas, completadas, canceladas],
        ["Total tutorías", "Programadas", "Completadas", "Canceladas"],
        ["#1e3a5f", "#2c7da0", "#15803d", "#b91c1c"],
    ):
        with col:
            st.markdown(
                f'<div class="stat-box"><div class="stat-num" style="color:{color};">{num}</div>'
                f'<div class="stat-lbl">{lbl}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1.05, 1], gap="large")

    # ── Columna izquierda ────────────────────────────────────────
    with col_left:

        # Disponibilidad
        st.markdown('<div class="tutoria-card">', unsafe_allow_html=True)
        section_title("📅 Disponibilidad de tutores")
        disponibilidad = fetch_disponibilidad()
        if not disponibilidad:
            st.info("No hay horarios disponibles en este momento.")
        else:
            for slot in disponibilidad:
                prof  = slot.get("profesor") or {}
                lugar = slot.get("lugar") or "Sin especificar"
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;align-items:center;'
                    f'padding:10px 0;border-bottom:1px solid #f1f5f9;">'
                    f'<div><strong style="color:#1e3a5f;">👨‍🏫 {prof.get("nombre_completo","—")}</strong>'
                    f'<br><small style="color:#64748b;">📍 {lugar}</small></div>'
                    f'<span class="badge-disponible">Disponible</span></div>',
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

        # Agendar
        st.markdown('<div class="tutoria-card">', unsafe_allow_html=True)
        section_title("➕ Agendar nueva sesión")

        profesores = fetch_profesores()
        materias   = fetch_materias()

        if profesores and materias:
            prof_map = {p["nombre_completo"]: p["id_profesor"] for p in profesores}
            mat_map  = {f"{m['clave_materia']} — {m['nombre_materia']}": m["id_materia"] for m in materias}

            sel_prof = st.selectbox("Docente tutor", list(prof_map.keys()), key="ag_prof")
            sel_mat  = st.selectbox("Materia",        list(mat_map.keys()),  key="ag_mat")
            col_d, col_t = st.columns(2)
            with col_d:
                fecha = st.date_input("Fecha", min_value=date.today(), key="ag_fecha")
            with col_t:
                hora = st.time_input("Hora", value=time(9, 0), step=1800, key="ag_hora")

            if st.button("📌 Solicitar tutoría", type="primary", use_container_width=True):
                horario_dt = datetime.combine(fecha, hora)
                if horario_dt < datetime.now():
                    st.error("No puedes agendar en una fecha/hora pasada.")
                else:
                    try:
                        if agendar_tutoria(id_alumno, prof_map[sel_prof], mat_map[sel_mat], horario_dt):
                            st.success(f"✅ Tutoría agendada para el {horario_dt.strftime('%d/%m/%Y a las %H:%M')}.")
                            fetch_mis_tutorias.clear()
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.warning("No hay docentes o materias registradas.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Columna derecha ──────────────────────────────────────────
    with col_right:

        # Sesiones programadas
        st.markdown('<div class="tutoria-card">', unsafe_allow_html=True)
        section_title("🗓️ Mis sesiones programadas")
        prox = [t for t in tutorias if t["estado"] == "programada"]
        if not prox:
            st.info("No tienes tutorías programadas.")
        else:
            for t in prox[:5]:
                prof_n = (t.get("profesor") or {}).get("nombre_completo", "—")
                mat_n  = (t.get("materia") or {}).get("nombre_materia", "—")
                ci, cb = st.columns([3, 1])
                with ci:
                    st.markdown(
                        f"<strong>📖 {mat_n}</strong><br>"
                        f"<small>👨‍🏫 {prof_n} · 🕐 {_fmt(t['horario'])}</small>",
                        unsafe_allow_html=True,
                    )
                with cb:
                    if st.button("Cancelar", key=f"cancel_{t['id_tutoria']}"):
                        cancelar_tutoria(t["id_tutoria"])
                        st.rerun()
                st.divider()
        st.markdown("</div>", unsafe_allow_html=True)

        # Historial
        st.markdown('<div class="tutoria-card">', unsafe_allow_html=True)
        section_title("📋 Historial académico")
        hist = [t for t in tutorias if t["estado"] in ("completada", "cancelada")]
        if not hist:
            st.info("Aún no tienes sesiones en el historial.")
        else:
            rows = ""
            for t in hist:
                prof_n = (t.get("profesor") or {}).get("nombre_completo", "—")
                mat_n  = (t.get("materia") or {}).get("nombre_materia", "—")
                reg    = t.get("registro_asistencia")
                calif  = str(reg[0].get("calificacion_tutoria") or "—") if reg else "—"
                rows += (
                    f"<tr><td>{_fmt(t['horario'])}</td><td>{mat_n}</td><td>{prof_n}</td>"
                    f"<td style='text-align:center'>{calif}</td>"
                    f"<td>{badge(t['estado'].capitalize(), t['estado'])}</td></tr>"
                )
            st.markdown(
                f"<table class='hist-table'><thead><tr>"
                f"<th>Fecha</th><th>Materia</th><th>Docente</th>"
                f"<th style='text-align:center'>Calif.</th><th>Estado</th>"
                f"</tr></thead><tbody>{rows}</tbody></table>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
