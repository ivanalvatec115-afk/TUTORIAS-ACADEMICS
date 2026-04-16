"""
seed_demo.py
────────────
Corre este script UNA sola vez para insertar datos de demostración.

Uso:
    SUPABASE_URL=https://xxx.supabase.co SUPABASE_KEY=eyJ... python seed_demo.py

Credenciales creadas:
    Alumnos   → número de control  /  contraseña: alumno123
    Docentes  → nombre (parcial)   /  contraseña: docente123
"""

import os, sys, bcrypt
from supabase import create_client

URL = os.environ.get("SUPABASE_URL", "")
KEY = os.environ.get("SUPABASE_KEY", "")

if not URL or not KEY:
    print("Falta SUPABASE_URL o SUPABASE_KEY como variable de entorno.")
    sys.exit(1)

sb = create_client(URL, KEY)

def h(p): return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()

materias = [
    ("SC-401", "Ingeniería de Software"),
    ("SC-301", "Base de Datos"),
    ("SC-201", "Programación Orientada a Objetos"),
    ("SC-501", "Redes de Computadoras"),
    ("SC-601", "Sistemas Operativos"),
]
for clave, nombre in materias:
    try:
        sb.table("materia").upsert({"clave_materia": clave, "nombre_materia": nombre}, on_conflict="clave_materia").execute()
        print(f"  ✅ Materia: {nombre}")
    except Exception as e:
        print(f"  ⚠️  {nombre}: {e}")

docentes = ["Juan José Robles Conde", "Laura Sánchez Torres", "Carlos Ramírez Herrera"]
pwd_doc  = h("docente123")
for nombre in docentes:
    try:
        sb.table("profesor").insert({"nombre_completo": nombre, "password_hash": pwd_doc, "activo": True}).execute()
        print(f"  ✅ Docente: {nombre}")
    except Exception as e:
        print(f"  ⚠️  {nombre}: {e}")

alumnos = [
    ("23660408", "Alejandro Morales Peña",               6, "6SA"),
    ("23660149", "Ivan Alvarado",                         6, "6SA"),
    ("23660154", "Pedro Espitia Samaniego",               6, "6SA"),
    ("23660167", "Francisco Bernardo Rodríguez Alvarado", 6, "6SA"),
]
pwd_alu = h("alumno123")
for nc, nombre, sem, grp in alumnos:
    try:
        sb.table("alumno").upsert(
            {"numero_control": nc, "nombre_completo": nombre, "password_hash": pwd_alu,
             "semestre": sem, "grupo": grp, "activo": True},
            on_conflict="numero_control"
        ).execute()
        print(f"  ✅ Alumno: {nombre} ({nc})")
    except Exception as e:
        print(f"  ⚠️  {nc}: {e}")

print("\n✅ Seed completado.")
print("   Alumnos  → número de control + alumno123")
print("   Docentes → nombre parcial    + docente123")
