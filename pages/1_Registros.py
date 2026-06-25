import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    fig1.update_layout(coloraxis_showscale=False)
    fig1.add_hline(y=por_periodo["Registros"].mean(), line_dash="dash", line_color="orange")
    fig1.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=f"Media: {por_periodo["Registros"].mean():.1f}", line=dict(color="orange", dash="dash"), showlegend=True))
    fig1.add_hline(y=por_periodo["Registros"].median(), line_dash="dot", line_color="red")
    fig1.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=f"Mediana: {por_periodo["Registros"].median():.1f}", line=dict(color="red", dash="dot"), showlegend=True))
    st.plotly_chart(fig1, width="stretch")

    periodo_max = por_periodo.loc[por_periodo["Registros"].idxmax(), "Período"]
    val_max = int(por_periodo["Registros"].max())
    periodo_min = por_periodo.loc[por_periodo["Registros"].idxmin(), "Período"]
    val_min = int(por_periodo["Registros"].min())
    media = por_periodo["Registros"].mean()
    mediana = por_periodo["Registros"].median()
    sobre_promedio = (por_periodo["Registros"] >= media).sum()
    total_p = len(por_periodo)

    if media > mediana * 1.1:
        tendencia = (
            f"Aunque en promedio hay {media:.0f} registros por período, "
            f"más de la mitad de los períodos tienen menos de {mediana:.0f} registros. "
            f"Esto significa que uno o pocos períodos concentran una gran parte de la actividad."
        )
    elif mediana > media * 1.1:
        tendencia = (
            f"La mayoría de los períodos tiene una participación alta: "
            f"más de la mitad supera los {mediana:.0f} registros, "
            f"con un promedio de {media:.0f} registros por período."
        )
    else:
        tendencia = (
            f"La participación es bastante pareja entre períodos: "
            f"el promedio es de {media:.0f} registros y la mitad de los períodos "
            f"está cerca de ese valor ({mediana:.0f} registros)."
        )

    st.info(
        f"* Los estudiantes que ingresaron en el **{periodo_max}** aparecen en la mayor (**{val_max}**) cantidad de registros. \n"
        f"* Los estudiantes que ingresaron en el **{periodo_min}** aparecen en la menor (**{val_min}**) cantidad de registros. \n"
        # f"* {tendencia} \n"
        f"* En total, **{sobre_promedio} de {total_p} períodos** igualan o superan el promedio."
    )

with col_b:
    st.subheader("Registros por nivel de materias")
    por_nivel = df.groupby("nivel_materia")["cantidad_estudiantes"].sum().reset_index()
    por_nivel.columns = ["Nivel", "Registros"]
    fig2 = px.bar(por_nivel, x="Nivel", y="Registros", color="Registros",
                  color_continuous_scale=[[0, "#a8d5a2"], [1, "#1a6b2f"]], text_auto=True,
                  labels={"Nivel": "Nivel de Materia"})
    fig2.update_layout(coloraxis_showscale=False)
    fig2.add_hline(y=por_nivel["Registros"].mean(), line_dash="dash", line_color="orange")
    fig2.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=f"Media: {por_nivel["Registros"].mean():.1f}", line=dict(color="orange", dash="dash"), showlegend=True))
    fig2.add_hline(y=por_nivel["Registros"].median(), line_dash="dot", line_color="red")
    fig2.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=f"Mediana: {por_nivel["Registros"].median():.1f}", line=dict(color="red", dash="dot"), showlegend=True))
    st.plotly_chart(fig2, width="stretch")

    nivel_max = por_nivel.loc[por_nivel["Registros"].idxmax(), "Nivel"]
    val_max_n = int(por_nivel["Registros"].max())
    nivel_min = por_nivel.loc[por_nivel["Registros"].idxmin(), "Nivel"]
    val_min_n = int(por_nivel["Registros"].min())
    media_n = por_nivel["Registros"].mean()
    mediana_n = por_nivel["Registros"].median()
    total_n = len(por_nivel)
    sobre_prom_n = (por_nivel["Registros"] >= media_n).sum()
    pct_max_n = int(val_max_n / por_nivel["Registros"].sum() * 100)

    if media_n > mediana_n * 1.1:
        tendencia_n = (
            f"La carga no está repartida de forma pareja: "
            f"unos pocos niveles concentran la mayor parte de los registros, "
            f"mientras que otros tienen una participación notablemente menor."
        )
    else:
        tendencia_n = (
            f"La participación entre niveles es relativamente equilibrada, "
            f"aunque siempre hay diferencias naturales entre unos y otros."
        )

    st.info(
        f"* En el nivel **{nivel_max}** tiene la mayor (**{val_max_n}**) cantidad de registros. \n"
        f"* En el nivel **{nivel_min}** tiene la menor (**{val_min_n}**) cantidad de registros. \n"
        #f"* {tendencia_n} \n"
        f"* En total, **{sobre_prom_n} de {total_n} niveles** igualan o superan el promedio."
    )

st.subheader("Las 10 materias con más registros")
por_materia = df.groupby("nombre_materia")["cantidad_estudiantes"].sum().reset_index()
por_materia.columns = ["Materia", "Registros"]
por_materia = por_materia.sort_values("Registros", ascending=False).head(10)
fig3 = px.bar(por_materia, x="Registros", y="Materia", orientation="h",
              color="Registros", color_continuous_scale=[[0, "#809acb"], [1, "#090069"]], text_auto=True)
fig3.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
fig3.add_vline(x=por_materia["Registros"].mean(), line_dash="dash", line_color="orange")
fig3.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=f"Media: {por_materia["Registros"].mean():.1f}", line=dict(color="orange", dash="dash"), showlegend=True))
fig3.add_vline(x=por_materia["Registros"].median(), line_dash="dot", line_color="red")
fig3.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=f"Mediana: {por_materia["Registros"].median():.1f}", line=dict(color="red", dash="dot"), showlegend=True))
st.plotly_chart(fig3, width="stretch")
