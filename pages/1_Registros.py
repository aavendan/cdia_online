import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import cargar_datos

st.set_page_config(page_title="Resumen - CDIA", page_icon="📊", layout="wide")
st.title("📊 Análisis de Registros")

df = cargar_datos()

# KPIs
total_registros = df["cantidad_estudiantes"].sum()
total_materias = df["nombre_materia"].nunique()
total_periodos = df["periodo_label"].nunique()

# Count unique students
todos_estudiantes = set()
for lista in df["estudiantes"].dropna():
    for nombre in lista.split(","):
        todos_estudiantes.add(nombre.strip())
total_estudiantes_unicos = len(todos_estudiantes)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de registros", total_registros)
col2.metric("Estudiantes únicos registrados", total_estudiantes_unicos)
col3.metric("Materias únicas con registros", total_materias)
col4.metric("Períodos de ingreso", total_periodos)

st.markdown("---")

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Registros por período de ingreso")
    por_periodo = df.groupby("periodo_label")["cantidad_estudiantes"].sum().reset_index()
    por_periodo.columns = ["Período", "Registros"]
    fig1 = px.bar(por_periodo, x="Período", y="Registros", color="Registros",
                  color_continuous_scale=[[0, "#b6d5a2"], [1, "#5c6b1a"]], text_auto=True,
                  labels={"Período": "Período de Ingreso"})
    fig1.update_layout(showlegend=False, coloraxis_showscale=False)
    fig1.add_hline(y=por_periodo["Registros"].mean(), line_dash="dash", line_color="orange", annotation_text="Media", annotation_position="top right")
    fig1.add_hline(y=por_periodo["Registros"].median(), line_dash="dot", line_color="red", annotation_text="Mediana", annotation_position="bottom right")
    st.plotly_chart(fig1, width="stretch")

with col_b:
    st.subheader("Registros por nivel de materias")
    por_nivel = df.groupby("nivel_materia")["cantidad_estudiantes"].sum().reset_index()
    por_nivel.columns = ["Nivel", "Registros"]
    fig2 = px.bar(por_nivel, x="Nivel", y="Registros", color="Registros",
                  color_continuous_scale=[[0, "#a8d5a2"], [1, "#1a6b2f"]], text_auto=True,
                  labels={"Nivel": "Nivel de Materia"})
    fig2.update_layout(showlegend=False, coloraxis_showscale=False)
    fig2.add_hline(y=por_nivel["Registros"].mean(), line_dash="dash", line_color="orange", annotation_text="Media", annotation_position="top right")
    fig2.add_hline(y=por_nivel["Registros"].median(), line_dash="dot", line_color="red", annotation_text="Mediana", annotation_position="bottom right")
    st.plotly_chart(fig2, width="stretch")

st.subheader("Top 10 materias con más registros")
por_materia = df.groupby("nombre_materia")["cantidad_estudiantes"].sum().reset_index()
por_materia.columns = ["Materia", "Registros"]
por_materia = por_materia.sort_values("Registros", ascending=False).head(10)
fig3 = px.bar(por_materia, x="Registros", y="Materia", orientation="h",
              color="Registros", color_continuous_scale=[[0, "#809acb"], [1, "#090069"]], text_auto=True)
fig3.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
fig3.add_vline(x=por_materia["Registros"].mean(), line_dash="dash", line_color="orange", annotation_text="Media", annotation_position="top right")
fig3.add_vline(x=por_materia["Registros"].median(), line_dash="dot", line_color="red", annotation_text="Mediana", annotation_position="bottom right")
st.plotly_chart(fig3, width="stretch")
