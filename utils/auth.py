import bcrypt
import streamlit as st
from supabase_client import get_supabase


def _check_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


def login_alumno(numero_control: str, password: str):
    sb = get_supabase()
    resp = (
        sb.table("alumno")
        .select("*")
        .eq("numero_control", numero_control.strip())
        .eq("activo", True)
        .execute()
    )
    if not resp.data:
        return None
    alumno = resp.data[0]
    return alumno if _check_password(password, alumno["password_hash"]) else None


def login_docente(identificador: str, password: str):
    sb = get_supabase()
    query = sb.table("profesor").select("*").eq("activo", True)
    if identificador.strip().isdigit():
        query = query.eq("id_profesor", int(identificador.strip()))
    else:
        query = query.ilike("nombre_completo", f"%{identificador.strip()}%")
    resp = query.execute()
    if not resp.data:
        return None
    docente = resp.data[0]
    return docente if _check_password(password, docente["password_hash"]) else None


def logout():
    st.session_state["authenticated"] = False
    st.session_state["role"]      = None
    st.session_state["user_id"]   = None
    st.session_state["user_name"] = ""
    st.session_state["page"]      = "login"
