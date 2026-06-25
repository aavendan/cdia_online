import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import cargar_datos, cargar_ingreso

st.set_page_config(page_title="Sin Registro - CDIA", page_icon="🔍", layout="wide")
st.title("🔍 Estudiantes Sin Registro")

df = cargar_datos()
df_ing = cargar_ingreso()

# Nombres únicos en datos.xlsx
nombres_registrados = set()
for lista in df["estudiantes"].dropna():
    for nombre in lista.split(","):
        n = nombre.strip().upper()
        if n:
            nombres_registrados.add(n)

# Estudiantes de ingreso que no aparecen en datos.xlsx
df_sin = df_ing[~df_ing["nombre"].isin(nombres_registrados)].copy()

# --- Filters ---
col1, col2 = st.columns(2)

anios = sorted(df_sin["anio"].unique(), reverse=True)
with col1:
    anio_sel = st.selectbox("Año de ingreso", ["Todos"] + [str(a) for a in anios])

paos_disponibles = (
    sorted(df_sin["pao"].unique())
    if anio_sel == "Todos"
    else sorted(df_sin[df_sin["anio"] == int(anio_sel)]["pao"].unique())
)
with col2:
    pao_sel = st.selectbox("Período de ingreso", ["Todos"] + [str(p) for p in paos_disponibles])

df_view = df_sin.copy()
if anio_sel != "Todos":
    df_view = df_view[df_view["anio"] == int(anio_sel)]
if pao_sel != "Todos":
    df_view = df_view[df_view["pao"] == int(pao_sel)]

st.markdown("---")
st.metric("Estudiantes sin registro", len(df_view))

tabla = df_view[["matricula", "nombre", "anio", "pao", "promedio"]].copy()
tabla.columns = ["Matrícula", "Nombre", "Año", "Período", "Promedio"]
st.dataframe(tabla.sort_values("Nombre"), width="stretch", hide_index=True)
