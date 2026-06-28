import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import cargar_migrados

st.set_page_config(page_title="Estudiantes Homologados - CDIA", page_icon="🔄", layout="wide")
st.title("🔄 Análisis por Estudiantes Homologados")

df = cargar_migrados()

# --- Filters ---
col1, col2 = st.columns(2)

anios = sorted(df["anio"].unique())
with col1:
    anio_sel = st.selectbox("Año de ingreso", ["Todos"] + [str(a) for a in anios])

paos_disponibles = (
    sorted(df["pao"].unique())
    if anio_sel == "Todos"
    else sorted(df[df["anio"] == int(anio_sel)]["pao"].unique())
)
with col2:
    pao_sel = st.selectbox("Período de ingreso", ["Todos"] + [str(p) for p in paos_disponibles])

df_f = df.copy()
if anio_sel != "Todos":
    df_f = df_f[df_f["anio"] == int(anio_sel)]
if pao_sel != "Todos":
    df_f = df_f[df_f["pao"] == int(pao_sel)]

st.markdown("---")
st.metric("Estudiantes homologados", len(df_f))

col_a, col_b = st.columns(2)

with col_a:
        st.subheader("Homologados por Período de Ingreso")
        df_f["periodo_label"] = df_f["anio"].astype(str) + " - P" + df_f["pao"].astype(str)
        por_periodo = df_f.groupby("periodo_label").size().reset_index(name="Estudiantes")
        fig1 = px.bar(
            por_periodo, x="periodo_label", y="Estudiantes",
            color="Estudiantes", color_continuous_scale=[[0, "#80cbc4"], [1, "#00695c"]],
            text="Estudiantes",
            labels={"periodo_label": "Período de Ingreso"},
        )
        fig1.update_layout(coloraxis_showscale=False, yaxis=dict(rangemode="tozero"),
                           xaxis={"categoryorder": "category ascending"})
        fig1.add_hline(y=por_periodo["Estudiantes"].mean(), line_dash="dash", line_color="orange")
        fig1.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=f"Media: {por_periodo['Estudiantes'].mean():.1f}", line=dict(color="orange", dash="dash"), showlegend=True))
        fig1.add_hline(y=por_periodo["Estudiantes"].median(), line_dash="dot", line_color="red")
        fig1.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=f"Mediana: {por_periodo['Estudiantes'].median():.1f}", line=dict(color="red", dash="dot"), showlegend=True))
        st.plotly_chart(fig1, width="stretch")

with col_b:
    st.subheader("Distribución de Promedios")
    fig2 = px.histogram(
        df_f, x="promedio", nbins=20,
        color_discrete_sequence=["#00695c"],
        labels={"promedio": "Promedio", "count": "Estudiantes"},
    )
    fig2.update_layout(yaxis_title="Estudiantes", yaxis=dict(rangemode="tozero"))
    fig2.add_vline(x=df_f["promedio"].mean(), line_dash="dash", line_color="orange")
    fig2.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=f"Media: {df_f['promedio'].mean():.2f}", line=dict(color="orange", dash="dash"), showlegend=True))
    fig2.add_vline(x=df_f["promedio"].median(), line_dash="dot", line_color="red")
    fig2.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=f"Mediana: {df_f['promedio'].median():.2f}", line=dict(color="red", dash="dot"), showlegend=True))
    st.plotly_chart(fig2, width="stretch")

st.subheader("Distribución de Promedios (Violin)")
fig3 = px.violin(
    df_f, y="promedio", box=True, points="all",
    color_discrete_sequence=["#00695c"],
    labels={"promedio": "Promedio"},
)
fig3.update_layout(yaxis=dict(rangemode="tozero"))
st.plotly_chart(fig3, width="stretch")

st.subheader("Datos")
tabla = df_f[["matricula", "nombre", "anio", "pao", "promedio"]].copy()
tabla.columns = ["Matrícula", "Nombre", "Año", "Período", "Promedio"]
st.dataframe(tabla.sort_values(["Año", "Período", "Nombre"]), width="stretch", hide_index=True)

