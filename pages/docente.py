import streamlit as st
from datetime import datetime
from supabase_client import get_supabase
from utils.auth import logout
from utils.styles import render_header, section_title, badge


def _sb():
    return get_supabase()


@st.cache_data(ttl=20, show_spinner=False)
def fetch_mi_disponibilidad(id_profesor: int):
    return (
        _sb().table("disponibilidad")
        .select("*")
        .eq("id_profesor", id_profesor)
        .order("id_disponibilidad", desc=True)
        .execute().data or []
    )


@st.cache_data(ttl=20, show_spinner=False)
def fetch_mis_sesiones(id_profesor: int):
    return (
        _sb().table("tutoria")
        .select(
            "id_tutoria, horario, estado,"
            "alumno(nombre_completo, numero_control, semestre, grupo),"
            "materia(nombre_materia),"
            "registro_asistencia(id_registro, asistio_alumno, calificacion_tutoria, notas_docente)"
        )
        .eq("id_profesor", id_profesor)
        .order("horario", desc=False)
        .execute().data or []
    )


def agregar_disponibilidad(id_profesor: int, lugar: str):
    _sb().table("disponibilidad").insert(
        {"id_profesor": id_profesor, "lugar": lugar, "activo": True}
    ).execute()
    fetch_mi_disponibilidad.clear()


def desactivar_disponibilidad(id_disponibilidad: int):
    _sb().table("disponibilidad").update({"activo": False}).eq("id_disponibilidad", id_disponibilidad).execute()
    fetch_mi_disponibilidad.clear()


def cerrar_sesion(id_tutoria: int, asistio: bool, notas: str, calificacion: int):
    existing = (
        _sb().table("registro_asistencia")
        .select("id_registro").eq("id_tutoria", id_tutoria).execute()
    )
    payload = {
        "id_tutoria":           id_tutoria,
        "fecha":                datetime.now().isoformat(),
        "asistio_alumno":       asistio,
        "notas_docente":        notas,
        "calificacion_tutoria": calificacion,
    }
    if existing.data:
        _sb().table("registro_asistencia").update(payload).eq("id_tutoria", id_tutoria).execute()
    else:
        _sb().table("registro_asistencia").insert(payload).execute()
    _sb().table("tutoria").update({"estado": "completada"}).eq("id_tutoria", id_tutoria).execute()
    fetch_mis_sesiones.clear()


def _fmt(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return iso or "—"


def render():
    if not st.session_state.get("authenticated") or st.session_state.get("role") != "docente":
        st.session_state["page"] = "login"
        st.rerun()

    id_profesor = st.session_state["user_id"]
    user_name   = st.session_state["user_name"]

    render_header("Tutorías Académicas", "Docente Tutor", user_name)

    _, col_logout = st.columns([9, 1])
    with col_logout:
        if st.button("Salir 🚪", key="logout_d"):
            logout()
            st.rerun()

    # ── Stats ────────────────────────────────────────────────────
    sesiones    = fetch_mis_sesiones(id_profesor)
    disponib    = fetch_mi_disponibilidad(id_profesor)
    slots_act   = sum(1 for d in disponib if d["activo"])
    programadas = sum(1 for s in sesiones if s["estado"] == "programada")
    completadas = sum(1 for s in sesiones if s["estado"] == "completada")
    canceladas  = sum(1 for s in sesiones if s["estado"] == "cancelada")

    for col, num, lbl, color in zip(
        st.columns(5),
        [slots_act, len(sesiones), programadas, completadas, canceladas],
        ["Slots activos", "Total sesiones", "Programadas", "Completadas", "Canceladas"],
        ["#2c7da0", "#1e3a5f", "#2c7da0", "#15803d", "#b91c1c"],
    ):
        with col:
            st.markdown(
                f'<div class="stat-box"><div class="stat-num" style="color:{color};">{num}</div>'
                f'<div class="stat-lbl">{lbl}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1, 1.1], gap="large")

    # ── Columna izquierda ────────────────────────────────────────
    with col_left:

        # Disponibilidad
        st.markdown('<div class="tutoria-card">', unsafe_allow_html=True)
        section_title("🕐 Gestionar disponibilidad")

        lugar_input = st.text_input(
            "Lugar de la tutoría",
            placeholder="Ej. Cubículo 3, Lab. Cómputo, Sala A…",
            key="disp_lugar",
        )
        if st.button("＋ Agregar disponibilidad", type="primary", use_container_width=True):
            if not lugar_input.strip():
                st.error("Indica el lugar de la tutoría.")
            else:
                agregar_disponibilidad(id_profesor, lugar_input.strip())
                st.success("✅ Disponibilidad registrada.")
                st.rerun()

        for slot in disponib:
            activo = slot["activo"]
            lugar  = slot.get("lugar") or "Sin lugar"
            estado_b = '<span class="badge-disponible">Activo</span>' if activo else '<span class="badge-cancelada">Inactivo</span>'
            cs, cd = st.columns([4, 1])
            with cs:
                st.markdown(f"<span style='font-size:.9rem;'>📍 {lugar}</span> {estado_b}", unsafe_allow_html=True)
            with cd:
                if activo and st.button("🗑️", key=f"del_{slot['id_disponibilidad']}"):
                    desactivar_disponibilidad(slot["id_disponibilidad"])
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Cerrar sesión
        st.markdown('<div class="tutoria-card">', unsafe_allow_html=True)
        section_title("✏️ Cerrar sesión / Registrar asistencia")

        pendientes = [s for s in sesiones if s["estado"] == "programada"]
        if not pendientes:
            st.info("No hay sesiones pendientes de cerrar.")
        else:
            opciones = {
                f"{(s.get('alumno') or {}).get('nombre_completo','?')} — "
                f"{_fmt(s['horario'])} — "
                f"{(s.get('materia') or {}).get('nombre_materia','?')}": s["id_tutoria"]
                for s in pendientes
            }
            sel_label = st.selectbox("Seleccionar sesión", list(opciones.keys()))
            sel_id    = opciones[sel_label]
            asistio   = st.radio("¿El alumno asistió?", ["Sí", "No"], horizontal=True)
            calif     = st.slider("Calificación (0–10)", 0, 10, 8)
            notas_txt = st.text_area("Notas del docente", placeholder="Temas vistos, observaciones…", height=90)

            if st.button("✅ Guardar y cerrar sesión", type="primary", use_container_width=True):
                cerrar_sesion(sel_id, asistio == "Sí", notas_txt, calif)
                st.success("🎉 Sesión cerrada y guardada en historial.")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Columna derecha ──────────────────────────────────────────
    with col_right:

        # Sesiones programadas
        st.markdown('<div class="tutoria-card">', unsafe_allow_html=True)
        section_title("📅 Sesiones programadas")
        prox = [s for s in sesiones if s["estado"] == "programada"]
        if not prox:
            st.info("No tienes sesiones programadas.")
        else:
            for s in prox[:8]:
                al  = s.get("alumno") or {}
                mat = s.get("materia") or {}
                grupo = f"Sem {al.get('semestre','?')} · {al.get('grupo','?')}"
                st.markdown(
                    f'<div style="padding:10px 0;border-bottom:1px solid #f1f5f9;">'
                    f'<strong style="color:#1e3a5f;">🎒 {al.get("nombre_completo","—")}</strong>'
                    f'<span style="font-size:.75rem;color:#64748b;margin-left:6px;">{grupo}</span><br>'
                    f'<small>📖 {mat.get("nombre_materia","—")} · 🕐 {_fmt(s["horario"])}</small>'
                    f'<span class="badge-programada" style="float:right;">Programada</span></div>',
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

        # Historial
        st.markdown('<div class="tutoria-card">', unsafe_allow_html=True)
        section_title("📋 Historial de sesiones")
        hist = [s for s in sesiones if s["estado"] in ("completada", "cancelada")]
        if not hist:
            st.info("No hay sesiones en el historial aún.")
        else:
            rows = ""
            for s in hist[:15]:
                al  = s.get("alumno") or {}
                mat = s.get("materia") or {}
                reg = s.get("registro_asistencia")
                asistio_v = "✅" if (reg and reg[0].get("asistio_alumno")) else "❌"
                calif_v   = str(reg[0].get("calificacion_tutoria") or "—") if reg else "—"
                rows += (
                    f"<tr><td>{_fmt(s['horario'])}</td>"
                    f"<td>{al.get('nombre_completo','—')}</td>"
                    f"<td>{mat.get('nombre_materia','—')}</td>"
                    f"<td style='text-align:center'>{asistio_v}</td>"
                    f"<td style='text-align:center'>{calif_v}</td>"
                    f"<td>{badge(s['estado'].capitalize(), s['estado'])}</td></tr>"
                )
            st.markdown(
                f"<table class='hist-table'><thead><tr>"
                f"<th>Fecha</th><th>Alumno</th><th>Materia</th>"
                f"<th style='text-align:center'>Asistió</th>"
                f"<th style='text-align:center'>Calif.</th><th>Estado</th>"
                f"</tr></thead><tbody>{rows}</tbody></table>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
