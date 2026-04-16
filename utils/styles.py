import streamlit as st


def inject_global_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

        .stApp { background: linear-gradient(135deg, #f0f4ff 0%, #e6edf7 100%) !important; }

        #MainMenu, footer, header { visibility: hidden; }
        .block-container { padding-top: 1.5rem !important; }

        /* Tarjetas */
        .tutoria-card {
            background: white;
            border-radius: 24px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            border: 1px solid #e9eef3;
            margin-bottom: 1.2rem;
        }

        /* Header de dashboard */
        .dash-header {
            background: white;
            border-radius: 20px;
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        .dash-header .badge-role {
            background: #eef2ff;
            color: #1e3a5f;
            padding: 4px 12px;
            border-radius: 30px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-left: 10px;
        }
        .user-chip {
            background: #eef2ff;
            color: #1e3a5f;
            padding: 6px 16px;
            border-radius: 40px;
            font-size: 0.85rem;
            font-weight: 500;
        }

        /* Botones */
        div.stButton > button {
            border-radius: 40px !important;
            font-weight: 600 !important;
            transition: 0.2s;
        }
        div.stButton > button[kind="primary"] {
            background: #2c7da0 !important;
            border: none !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background: #1f5e7a !important;
            transform: translateY(-1px);
        }
        div.stButton > button[kind="secondary"] {
            background: white !important;
            border: 1px solid #cbd5e1 !important;
            color: #1e2a3a !important;
        }

        /* Inputs */
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div:first-child {
            border-radius: 16px !important;
        }

        /* Badges */
        .badge-programada { background:#dbeafe; color:#1d4ed8; padding:3px 10px; border-radius:50px; font-size:0.75rem; font-weight:600; }
        .badge-completada { background:#dcfce7; color:#15803d; padding:3px 10px; border-radius:50px; font-size:0.75rem; font-weight:600; }
        .badge-cancelada  { background:#fee2e2; color:#b91c1c; padding:3px 10px; border-radius:50px; font-size:0.75rem; font-weight:600; }
        .badge-disponible { background:#e6f7ec; color:#2b7e3a; padding:3px 10px; border-radius:50px; font-size:0.75rem; font-weight:600; }

        /* Título de sección */
        .section-title {
            font-size: 1rem;
            font-weight: 700;
            color: #0f2b3d;
            border-left: 4px solid #2c7da0;
            padding-left: 10px;
            margin-bottom: 1rem;
        }

        /* Tabla historial */
        table.hist-table { width: 100%; border-collapse: collapse; }
        table.hist-table th {
            text-align: left; font-size: 0.8rem; color: #64748b;
            padding: 6px 4px; border-bottom: 2px solid #e2e8f0;
        }
        table.hist-table td {
            font-size: 0.85rem; padding: 9px 4px;
            border-bottom: 1px solid #f1f5f9;
        }

        /* Stat boxes */
        .stat-box {
            background: white;
            border-radius: 20px;
            padding: 1.2rem 1.5rem;
            text-align: center;
            border: 1px solid #e9eef3;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        }
        .stat-box .stat-num { font-size: 2rem; font-weight: 700; color: #1e3a5f; }
        .stat-box .stat-lbl { font-size: 0.78rem; color: #64748b; margin-top: 4px; }

        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str):
    st.markdown(f'<p class="section-title">{text}</p>', unsafe_allow_html=True)


def badge(text: str, estado: str) -> str:
    cls = {
        "programada": "badge-programada",
        "completada": "badge-completada",
        "cancelada":  "badge-cancelada",
        "disponible": "badge-disponible",
    }.get(estado.lower(), "badge-programada")
    return f'<span class="{cls}">{text}</span>'


def render_header(title: str, role_label: str, user_name: str):
    st.markdown(
        f"""
        <div class="dash-header">
            <div>
                <span style="font-size:1.4rem;">🎓</span>
                <span style="font-size:1.25rem; font-weight:700; color:#1e3a5f; margin-left:8px;">{title}</span>
                <span class="badge-role">{role_label}</span>
            </div>
            <span class="user-chip">👤 {user_name}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
