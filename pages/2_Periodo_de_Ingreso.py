import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import cargar_datos, cargar_ingreso

st.set_page_config(page_title="Período de Ingreso - CDIA", page_icon="📅", layout="wide")
st.title("📅 Análisis por Período de Ingreso")

df = cargar_datos()
df_ing = cargar_ingreso()

# --- Filters ---
col1, col2, col3, col4 = st.columns(4)

anios = sorted(df_ing["anio"].unique(), reverse=True)
with col1:
    anio_sel = st.selectbox("Año de ingreso", ["Todos"] + [str(a) for a in anios])

paos_disponibles = (
    sorted(df_ing["pao"].unique())
    if anio_sel == "Todos"
    else sorted(df_ing[df_ing["anio"] == int(anio_sel)]["pao"].unique())
)
with col2:
    pao_sel = st.selectbox("Período de ingreso", ["Todos"] + [str(p) for p in paos_disponibles])

# Get student names for the selected cohort
df_ing_f = df_ing.copy()
if anio_sel != "Todos":
    df_ing_f = df_ing_f[df_ing_f["anio"] == int(anio_sel)]
if pao_sel != "Todos":
    df_ing_f = df_ing_f[df_ing_f["pao"] == int(pao_sel)]

nombres_cohorte = set(df_ing_f["nombre"].unique())

st.markdown("---")
st.metric("Estudiantes en la cohorte", len(nombres_cohorte))

# Build registros for the cohort
registros = []
for _, row in df.iterrows():
    for nombre in row["estudiantes"].split(","):
        nombre = nombre.strip().upper()
        if nombre and nombre in nombres_cohorte:
            registros.append({
                "Estudiante": nombre,
                "Materia": row["nombre_materia"],
                "Código": row["codigo_materia"],
                "Nivel": row["nivel_materia"],
                "Período de Registro": row["periodo_label"],
            })

if not registros:
    st.info("No hay registros para la cohorte seleccionada.")
    st.stop()

df_reg = pd.DataFrame(registros)

niveles = sorted(df_reg["Nivel"].unique())
with col3:
    nivel_sel = st.selectbox("Nivel", ["Todos"] + niveles)

materias_disponibles = (
    sorted(df_reg["Materia"].unique())
    if nivel_sel == "Todos"
    else sorted(df_reg[df_reg["Nivel"] == nivel_sel]["Materia"].unique())
)
with col4:
    materia_sel = st.selectbox("Materia", ["Todas"] + materias_disponibles)

if nivel_sel != "Todos":
    df_reg = df_reg[df_reg["Nivel"] == nivel_sel]
if materia_sel != "Todas":
    df_reg = df_reg[df_reg["Materia"] == materia_sel]

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Registros por Materia")
    por_materia = df_reg.groupby("Materia").size().reset_index(name="Registros")
    por_materia = por_materia.sort_values("Registros", ascending=False)

    fig1 = px.bar(
        por_materia, x="Materia", y="Registros",
        color="Registros", color_continuous_scale=[[0, "#80cbc4"], [1, "#00695c"]],
        text_auto=True,
    )
    fig1.update_layout(
        xaxis={"categoryorder": "total descending", "tickangle": -45},
        coloraxis_showscale=False,
        yaxis=dict(rangemode="tozero"),
    )
    fig1.add_hline(y=por_materia["Registros"].mean(), line_dash="dash", line_color="orange")
    fig1.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=f"Media: {por_materia["Registros"].mean():.1f}", line=dict(color="orange", dash="dash"), showlegend=True))
    fig1.add_hline(y=por_materia["Registros"].median(), line_dash="dot", line_color="red")
    fig1.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=f"Mediana: {por_materia["Registros"].median():.1f}", line=dict(color="red", dash="dot"), showlegend=True))
    st.plotly_chart(fig1, width="stretch")

with col_b:
    st.subheader("Registros por Nivel")
    por_nivel = df_reg.groupby("Nivel").size().reset_index(name="Registros")
    fig2 = px.bar(
        por_nivel, x="Nivel", y="Registros",
        color="Registros", color_continuous_scale=[[0, "#a8d5a2"], [1, "#1a6b2f"]],
        text_auto=True,
    )
    fig2.update_layout(coloraxis_showscale=False, yaxis=dict(rangemode="tozero"))
    fig2.add_hline(y=por_nivel["Registros"].mean(), line_dash="dash", line_color="orange")
    fig2.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=f"Media: {por_nivel["Registros"].mean():.1f}", line=dict(color="orange", dash="dash"), showlegend=True))
    fig2.add_hline(y=por_nivel["Registros"].median(), line_dash="dot", line_color="red")
    fig2.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=f"Mediana: {por_nivel["Registros"].median():.1f}", line=dict(color="red", dash="dot"), showlegend=True))
    st.plotly_chart(fig2, width="stretch")

st.subheader("Datos")
st.dataframe(
    df_reg.sort_values(["Estudiante", "Nivel", "Materia"]),
    width="stretch",
    hide_index=True,
)