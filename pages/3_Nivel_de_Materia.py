import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import cargar_datos

st.set_page_config(page_title="Nivel de Materia - CDIA", page_icon="📚", layout="wide")
st.title("📚 Análisis por Nivel de Materia")

df = cargar_datos()

niveles = sorted(df["nivel_materia"].unique())
nivel_sel = st.selectbox("Seleccione un nivel:", ["Todos"] + niveles)

if nivel_sel != "Todos":
    df_filtrado = df[df["nivel_materia"] == nivel_sel]
else:
    df_filtrado = df.copy()

st.markdown("---")

col1, col2, col3 = st.columns(3)
col1.metric("Total registros", int(df_filtrado["cantidad_estudiantes"].sum()))
col2.metric("Materias en este nivel", df_filtrado["nombre_materia"].nunique())
col3.metric("Períodos involucrados", df_filtrado["periodo_label"].nunique())

todos_periodos = sorted(df["periodo_label"].unique())

st.subheader("Registros por Materia y Período de Ingreso")
pivot = df_filtrado.pivot_table(
    index="nombre_materia", columns="periodo_label",
    values="cantidad_estudiantes", aggfunc="sum", fill_value=0
)
pivot = pivot.reindex(columns=todos_periodos, fill_value=0)
fig = px.imshow(
    pivot,
    text_auto=True,
    color_continuous_scale="Blues",
    aspect="auto",
    labels=dict(x="Período de Ingreso", y="Materia", color="Registros")
)
fig.update_layout(coloraxis_showscale=True)
st.plotly_chart(fig, width="stretch")

st.subheader("Registros por Período de Ingreso")
evolucion = df_filtrado.groupby("periodo_label")["cantidad_estudiantes"].sum().reset_index()
evolucion.columns = ["Período", "Registros"]
evolucion = (
    pd.DataFrame({"Período": todos_periodos})
    .merge(evolucion, on="Período", how="left")
    .fillna(0)
)
evolucion["Registros"] = evolucion["Registros"].astype(int)
fig2 = px.bar(evolucion, x="Período", y="Registros",
              color_discrete_sequence=["#1f77b4"],
              labels={"Período": "Período de Ingreso"})
fig2.update_layout(yaxis=dict(rangemode="tozero"))
st.plotly_chart(fig2, width="stretch")

st.subheader("Datos")
tabla = df_filtrado[["nivel_materia", "codigo_materia", "nombre_materia", "periodo_label", "cantidad_estudiantes"]].copy()
tabla.columns = ["Nivel", "Código", "Materia", "Período", "Estudiantes"]
st.dataframe(tabla.sort_values(["Materia", "Período"]), width="stretch", hide_index=True)
