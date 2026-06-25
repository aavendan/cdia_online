import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import cargar_datos

st.set_page_config(page_title="Materia - CDIA", page_icon="📖", layout="wide")
st.title("📖 Análisis por Materia")

df = cargar_datos()

materias = sorted(df["nombre_materia"].unique())
materia_sel = st.selectbox("Seleccione una materia:", materias)

df_mat = df[df["nombre_materia"] == materia_sel]

st.markdown("---")

info = df_mat.iloc[0]
col1, col2, col3 = st.columns(3)
col1.info(f"**Código:** {info['codigo_materia']}")
col2.info(f"**Nivel:** {info['nivel_materia']}")
col3.info(f"**Total inscripciones:** {int(df_mat['cantidad_estudiantes'].sum())}")

st.subheader("Registros por Período de Ingreso")
todos_periodos = sorted(df["periodo_label"].unique())
por_periodo = df_mat.groupby("periodo_label")["cantidad_estudiantes"].sum().reset_index()
por_periodo.columns = ["Período", "Registros"]
por_periodo = (
    pd.DataFrame({"Período": todos_periodos})
    .merge(por_periodo, on="Período", how="left")
    .fillna(0)
)
por_periodo["Registros"] = por_periodo["Registros"].astype(int)
fig = px.bar(por_periodo, x="Período", y="Registros",
             color="Registros", color_continuous_scale=[[0, "#80cbc4"], [1, "#00695c"]],
             text_auto=True)
fig.update_layout(coloraxis_showscale=False, yaxis=dict(rangemode="tozero"))
st.plotly_chart(fig, width="stretch")

st.subheader("Estudiantes registrados por Período de Ingreso")
for _, row in df_mat.sort_values("periodo_label").iterrows():
    with st.expander(f"📅 {row['periodo_label']}  —  {int(row['cantidad_estudiantes'])} estudiante(s)"):
        nombres = [n.strip() for n in row["estudiantes"].split(",")]
        for nombre in sorted(nombres):
            st.write(f"• {nombre}")
