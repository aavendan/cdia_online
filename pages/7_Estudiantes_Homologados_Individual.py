import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import cargar_migrados

st.set_page_config(page_title="Homologados Individual - CDIA", page_icon="🔎", layout="wide")
st.title("🔎 Estudiantes Homologados - Individual")

df = cargar_migrados()

df_f = df.copy()

st.markdown("---")

estudiante_sel = st.selectbox("Seleccionar estudiante", ["Ninguno"] + sorted(df_f["nombre"].unique()))

df_scatter = df_f.copy()
df_scatter = df_scatter.sort_values("promedio").reset_index(drop=True)
df_scatter["color"] = df_scatter["nombre"].apply(
    lambda n: n if n == estudiante_sel else "Estudiante"
)

t1 = df_scatter["promedio"].quantile(1/3)
t2 = df_scatter["promedio"].quantile(2/3)
y_max = df_scatter["promedio"].max() * 1.05

fig = px.scatter(
    df_scatter, x=df_scatter.index, y="promedio",
    color="color",
    color_discrete_map={estudiante_sel: "#e65100", "Estudiante": "#00695c"},
    category_orders={"color": ["Estudiante", estudiante_sel]},
    hover_data={"nombre": True, "promedio": True, "color": False},
    labels={"x": "Estudiante (ordenado por promedio)", "promedio": "Promedio"},
    size_max=12,
)
fig.add_hrect(y0=0, y1=t1, fillcolor="rgba(255,200,200,0.2)", line_width=0, annotation_text="Bajo", annotation_position="top left")
fig.add_hrect(y0=t1, y1=t2, fillcolor="rgba(255,255,180,0.2)", line_width=0, annotation_text="Medio", annotation_position="top left")
fig.add_hrect(y0=t2, y1=y_max, fillcolor="rgba(180,255,180,0.2)", line_width=0, annotation_text="Alto", annotation_position="top left")
fig.add_hline(y=t1, line_dash="dash", line_color="gray", line_width=1)
fig.add_hline(y=t2, line_dash="dash", line_color="gray", line_width=1)
fig.update_traces(marker=dict(size=8))
if estudiante_sel != "Ninguno":
    fila = df_scatter[df_scatter["nombre"] == estudiante_sel]
    if not fila.empty:
        fig.update_traces(marker=dict(size=14), selector=dict(name=estudiante_sel))
        r = df_f[df_f["nombre"] == estudiante_sel].iloc[0]
        st.markdown(
            f"**Matrícula:** {r['matricula']} &nbsp;|&nbsp; "
            f"**Ingreso:** {r['anio']} - P{r['pao']} &nbsp;|&nbsp; "
            f"**Promedio:** {r['promedio']:.2f}"
        )
fig.update_layout(xaxis=dict(showticklabels=False), yaxis=dict(rangemode="tozero"), legend_title_text="")
st.plotly_chart(fig, width="stretch")

st.subheader("Resumen por Año y Período de Ingreso")
resumen = (
    df_f.groupby(["anio", "pao"])["promedio"]
    .agg(Estudiantes="count", Promedio_Min="min", Promedio_Medio="mean", Promedio_Max="max")
    .reset_index()
)
resumen.columns = ["Año", "Período", "Estudiantes", "Mínimo", "Promedio", "Máximo"]
resumen[["Mínimo", "Promedio", "Máximo"]] = resumen[["Mínimo", "Promedio", "Máximo"]].round(2)
st.dataframe(resumen.sort_values(["Año", "Período"]), width="stretch", hide_index=True)
