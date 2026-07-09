import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import cargar_historial_academico

st.set_page_config(page_title="Avance en la Malla - CDIA", page_icon="🧭", layout="wide")
st.title("🧭 Avance en la Malla")
st.caption("Análisis comparativo de la Penalidad (adelanto/atraso respecto a la malla) entre modalidades")

df = cargar_historial_academico()

# --- Filters ---
col1, col2 = st.columns(2)
with col1:
    niveles = sorted(df["nivel"].unique())
    nivel_sel = st.selectbox("Nivel", ["Todos"] + niveles)
with col2:
    modalidades = sorted(df["modalidad"].unique())
    modalidad_sel = st.multiselect("Modalidad", modalidades, default=modalidades)

df_f = df.copy()
if nivel_sel != "Todos":
    df_f = df_f[df_f["nivel"] == nivel_sel]
df_f = df_f[df_f["modalidad"].isin(modalidad_sel)]

st.markdown("---")

# --- Resumen por estudiante ---
resumen_est = (
    df_f.groupby(["matricula", "nombre", "modalidad"])["penalidad"]
    .agg(penalidad_promedio="mean", penalidad_mediana="median", materias="count")
    .reset_index()
)

def clasificar(p):
    if p < 0:
        return "Adelantado"
    if p == 0:
        return "Al día"
    return "Atrasado"

resumen_est["estado"] = resumen_est["penalidad_promedio"].apply(clasificar)

# --- Métricas por modalidad ---
col_m1, col_m2, col_m3 = st.columns(3)
for col, mod in zip([col_m1, col_m2], modalidades if len(modalidades) <= 2 else modalidades[:2]):
    sub = resumen_est[resumen_est["modalidad"] == mod]
    col.metric(f"Penalidad promedio · {mod}", f"{sub['penalidad_promedio'].mean():.2f}" if len(sub) else "—",
               help=f"{len(sub)} estudiantes")
col_m3.metric("Total estudiantes", resumen_est["matricula"].nunique())

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Distribución de Penalidad por Modalidad (por materia)")
    fig1 = px.box(
        df_f, x="modalidad", y="penalidad", color="modalidad",
        color_discrete_map={"en línea": "#1565c0", "híbrida": "#ef6c00"},
        points="all",
        labels={"modalidad": "Modalidad", "penalidad": "Penalidad"},
    )
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, width="stretch")

with col_b:
    st.subheader("Penalidad Promedio por Estudiante y Modalidad")
    fig2 = px.violin(
        resumen_est, x="modalidad", y="penalidad_promedio", color="modalidad",
        color_discrete_map={"en línea": "#1565c0", "híbrida": "#ef6c00"},
        box=True, points="all",
        labels={"modalidad": "Modalidad", "penalidad_promedio": "Penalidad Promedio"},
    )
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, width="stretch")

st.subheader("Estado de Avance por Modalidad")
por_estado = (
    resumen_est.groupby(["modalidad", "estado"]).size().reset_index(name="Estudiantes")
)
total_por_mod = resumen_est.groupby("modalidad").size().to_dict()
por_estado["Porcentaje"] = por_estado.apply(lambda r: 100 * r["Estudiantes"] / total_por_mod[r["modalidad"]], axis=1)
fig3 = px.bar(
    por_estado, x="modalidad", y="Porcentaje", color="estado", barmode="stack",
    color_discrete_map={"Adelantado": "#2e7d32", "Al día": "#1565c0", "Atrasado": "#b71c1c"},
    text=por_estado["Estudiantes"],
    category_orders={"estado": ["Adelantado", "Al día", "Atrasado"]},
    labels={"modalidad": "Modalidad", "Porcentaje": "% Estudiantes"},
)
fig3.update_layout(legend_title_text="")
st.plotly_chart(fig3, width="stretch")

st.subheader("Penalidad Promedio a lo Largo del Tiempo, por Modalidad")
evolucion = (
    df_f.groupby(["anio_termino", "modalidad"])["penalidad"]
    .mean()
    .reset_index()
    .sort_values("anio_termino")
)
fig4 = px.line(
    evolucion, x="anio_termino", y="penalidad", color="modalidad", markers=True,
    color_discrete_map={"en línea": "#1565c0", "híbrida": "#ef6c00"},
    category_orders={"anio_termino": sorted(evolucion["anio_termino"].unique())},
    labels={"anio_termino": "Período", "penalidad": "Penalidad Promedio", "modalidad": "Modalidad"},
)
fig4.update_xaxes(type="category")
fig4.add_hline(y=0, line_dash="dash", line_color="gray")
st.plotly_chart(fig4, width="stretch")

st.markdown("---")
st.subheader("Detalle por Estudiante")
estudiante_sel = st.selectbox("Seleccionar estudiante", ["Ninguno"] + sorted(resumen_est["nombre"].unique()))

if estudiante_sel != "Ninguno":
    fila = resumen_est[resumen_est["nombre"] == estudiante_sel].iloc[0]
    col_i1, col_i2, col_i3, col_i4 = st.columns(4)
    col_i1.metric("Modalidad", fila["modalidad"])
    col_i2.metric("Penalidad promedio", f"{fila['penalidad_promedio']:.2f}")
    col_i3.metric("Materias", int(fila["materias"]))
    col_i4.metric("Estado", fila["estado"])

    historial_est = df_f[df_f["nombre"] == estudiante_sel].sort_values(["anio_termino", "nivel"])
    fig5 = px.bar(
        historial_est, x="anio_termino", y="penalidad", color="nivel",
        category_orders={"anio_termino": sorted(historial_est["anio_termino"].unique())},
        labels={"anio_termino": "Período", "penalidad": "Penalidad", "nivel": "Nivel"},
    )
    fig5.update_xaxes(type="category")
    fig5.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig5, width="stretch")

    tabla_est = historial_est[["anio_termino", "codigo", "materia", "no_vez", "estado", "nivel", "penalidad"]].copy()
    tabla_est.columns = ["Período", "Código", "Materia", "No. Vez", "Estado", "Nivel", "Penalidad"]
    st.dataframe(tabla_est, width="stretch", hide_index=True)

st.markdown("---")
st.subheader("Datos por Estudiante")
tabla = resumen_est[["matricula", "nombre", "modalidad", "materias", "penalidad_promedio", "penalidad_mediana", "estado"]].copy()
tabla.columns = ["Matrícula", "Nombre", "Modalidad", "Materias", "Penalidad Promedio", "Penalidad Mediana", "Estado"]
tabla[["Penalidad Promedio", "Penalidad Mediana"]] = tabla[["Penalidad Promedio", "Penalidad Mediana"]].round(2)
st.dataframe(tabla.sort_values(["Modalidad", "Nombre"]), width="stretch", hide_index=True)
