import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import cargar_datos, cargar_ingreso

st.set_page_config(page_title="Estudiantes Sin Registros - CDIA", page_icon="❌", layout="wide")
st.title("❌ Estudiantes Sin Registros")

df_reg = cargar_datos()
df_ing = cargar_ingreso()

# Nombres que aparecen en registros.xlsx
nombres_con_registro = set()
for nombres_str in df_reg["estudiantes"].dropna():
    for nombre in nombres_str.split(","):
        nombre = nombre.strip().upper()
        if nombre:
            nombres_con_registro.add(nombre)

# Estudiantes ADMISIONES sin ningún registro
df_sin = df_ing[~df_ing["nombre"].isin(nombres_con_registro)].copy()

# --- Filters ---
col1, col2 = st.columns(2)

anios = sorted(df_sin["anio"].unique())
with col1:
    anio_sel = st.selectbox("Año de ingreso", ["Todos"] + [str(a) for a in anios])

paos_disponibles = (
    sorted(df_sin["pao"].unique())
    if anio_sel == "Todos"
    else sorted(df_sin[df_sin["anio"] == int(anio_sel)]["pao"].unique())
)
with col2:
    pao_sel = st.selectbox("Período de ingreso", ["Todos"] + [str(p) for p in paos_disponibles])

df_f = df_sin.copy()
if anio_sel != "Todos":
    df_f = df_f[df_f["anio"] == int(anio_sel)]
if pao_sel != "Todos":
    df_f = df_f[df_f["pao"] == int(pao_sel)]

st.markdown("---")
st.metric("Estudiantes sin registros", len(df_f))

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Sin Registros por Período de Ingreso")
    df_f["periodo_label"] = df_f["anio"].astype(str) + " - P" + df_f["pao"].astype(str)
    por_periodo = df_f.groupby("periodo_label").size().reset_index(name="Estudiantes")
    fig1 = px.bar(
        por_periodo, x="periodo_label", y="Estudiantes",
        color="Estudiantes", color_continuous_scale=[[0, "#ef9a9a"], [1, "#b71c1c"]],
        text="Estudiantes",
        labels={"periodo_label": "Período de Ingreso"},
    )
    fig1.update_layout(coloraxis_showscale=False, yaxis=dict(rangemode="tozero"),
                       xaxis={"categoryorder": "category ascending"})
    st.plotly_chart(fig1, width="stretch")

with col_b:
    st.subheader("Distribución de Promedios")
    fig2 = px.histogram(
        df_f, x="promedio", nbins=20,
        color_discrete_sequence=["#b71c1c"],
        labels={"promedio": "Promedio", "count": "Estudiantes"},
    )
    fig2.update_layout(yaxis_title="Estudiantes", yaxis=dict(rangemode="tozero"))
    st.plotly_chart(fig2, width="stretch")

st.subheader("Datos")
tabla = df_f[["matricula", "nombre", "anio", "pao", "promedio"]].copy()
tabla.columns = ["Matrícula", "Nombre", "Año", "Período", "Promedio"]
st.dataframe(tabla.sort_values(["Año", "Período", "Nombre"]), width="stretch", hide_index=True)
