import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import cargar_materias_pendientes, cargar_penalidad_referencia

st.set_page_config(page_title="Materias Pendientes - CDIA", page_icon="📌", layout="wide")
st.title("📌 Materias Pendientes")
st.caption("Análisis de la Penalidad de las materias aún no cursadas, por estado de penalidad, modalidad, nivel, materia y estudiante")

NIVELES_ORDEN = ["100-I", "100-II", "200-I", "200-II", "300-I"]

df = cargar_materias_pendientes()

# --- Estado de penalidad: rangos (terciles) del total general de penalidad por estudiante ---
resumen_full = (
    df.groupby(["matricula", "nombre", "modalidad"])["penalidad"]
    .agg(penalidad_total="sum", pendientes="count")
    .reset_index()
)
t1 = resumen_full["penalidad_total"].quantile(1 / 3)
t2 = resumen_full["penalidad_total"].quantile(2 / 3)

def clasificar(p):
    if p <= t1:
        return "Bajo"
    if p <= t2:
        return "Medio"
    return "Alto"

resumen_full["estado_penalidad"] = resumen_full["penalidad_total"].apply(clasificar)
df = df.merge(resumen_full[["nombre", "estado_penalidad"]], on="nombre", how="left")

# --- Filters ---
col1, col2, col3 = st.columns(3)
with col1:
    niveles_disp = [n for n in NIVELES_ORDEN if n in df["nivel"].unique()]
    nivel_sel = st.multiselect("Nivel", niveles_disp, default=niveles_disp)
with col2:
    modalidades = sorted(df["modalidad"].unique())
    modalidad_sel = st.multiselect("Modalidad", modalidades, default=modalidades)
with col3:
    estado_sel = st.multiselect("Estado de Penalidad", ["Bajo", "Medio", "Alto"], default=["Bajo", "Medio", "Alto"])

df_f = df[df["nivel"].isin(nivel_sel) & df["modalidad"].isin(modalidad_sel) & df["estado_penalidad"].isin(estado_sel)]
resumen_f = (
    df_f.groupby(["matricula", "nombre", "modalidad", "estado_penalidad"])["penalidad"]
    .agg(penalidad_total="sum", pendientes="count")
    .reset_index()
)

st.markdown("---")

with st.expander("¿Cómo se calcula la Penalidad?"):
    st.markdown(
        "La **Penalidad** de una materia pendiente depende únicamente del **Nivel** de la malla al que "
        "pertenece, no del estudiante: indica cuántos períodos de atraso implica no haberla cursado todavía, "
        "tomando como referencia el ritmo estándar del plan de estudios en el período actual. Un valor "
        "**negativo** significa que ese nivel aún no debería cursarse (no genera atraso); un valor "
        "**positivo** indica que ya debería haberse completado hace esa cantidad de períodos. "
        "La Penalidad Total de un estudiante es la suma de la penalidad de todas sus materias pendientes."
    )
    tabla_ref = cargar_penalidad_referencia().rename(columns={"nivel": "Nivel", "penalidad": "Penalidad"})
    st.dataframe(tabla_ref, width="stretch", hide_index=True)

st.subheader("Indicadores de Penalidad por Modalidad")
cols_ind = st.columns(len(modalidad_sel)) if modalidad_sel else []
for col, mod in zip(cols_ind, modalidad_sel):
    sub = df_f[df_f["modalidad"] == mod]
    with col:
        st.markdown(f"**{mod.capitalize()}**")
        st.metric("Estudiantes", sub["nombre"].nunique())
        st.metric("Penalidad total", int(sub["penalidad"].sum()) if len(sub) else 0)

st.markdown("---")

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Estudiantes", resumen_f["matricula"].nunique())
col_m2.metric("Materias pendientes", len(df_f))
col_m3.metric("Penalidad total", int(df_f["penalidad"].sum()) if len(df_f) else 0)

st.subheader("Por Estado de Penalidad")
st.caption(f"Rangos según terciles del total general de penalidad por estudiante: Bajo ≤ {t1:.0f} · Medio ≤ {t2:.0f} · Alto > {t2:.0f}")
col_a, col_b = st.columns(2)
with col_a:
    conteo_estado = df_f.groupby(["estado_penalidad", "modalidad"]).size().reset_index(name="Total de Penalidad")
    fig1 = px.bar(
        conteo_estado, x="estado_penalidad", y="Total de Penalidad", color="modalidad", barmode="group",
        color_discrete_map={"en línea": "#1565c0", "híbrida": "#ef6c00"},
        text="Total de Penalidad",
        category_orders={"estado_penalidad": ["Bajo", "Medio", "Alto"]},
        labels={"estado_penalidad": "Estado de Penalidad", "modalidad": "Modalidad"},
    )
    fig1.update_layout(yaxis=dict(rangemode="tozero"), legend_title_text="")
    st.plotly_chart(fig1, width="stretch")
with col_b:
    fig2 = px.violin(
        resumen_f, x="estado_penalidad", y="penalidad_total", color="modalidad", violinmode="group",
        color_discrete_map={"en línea": "#1565c0", "híbrida": "#ef6c00"},
        box=True, points="all",
        category_orders={"estado_penalidad": ["Bajo", "Medio", "Alto"]},
        labels={"estado_penalidad": "Estado de Penalidad", "penalidad_total": "Penalidad Total", "modalidad": "Modalidad"},
    )
    fig2.update_layout(legend_title_text="")
    st.plotly_chart(fig2, width="stretch")

st.subheader("Por Modalidad")
col_c, col_d = st.columns(2)
with col_c:
    fig3 = px.box(
        df_f, x="modalidad", y="penalidad", color="modalidad",
        color_discrete_map={"en línea": "#1565c0", "híbrida": "#ef6c00"},
        points="all",
        labels={"modalidad": "Modalidad", "penalidad": "Penalidad"},
    )
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, width="stretch")
with col_d:
    por_modalidad = df_f.groupby("modalidad").agg(
        Estudiantes=("nombre", "nunique"), Penalidad_Total=("penalidad", "sum")
    ).reset_index()
    fig4 = px.bar(
        por_modalidad, x="modalidad", y="Penalidad_Total", color="modalidad",
        color_discrete_map={"en línea": "#1565c0", "híbrida": "#ef6c00"},
        text="Penalidad_Total",
        labels={"modalidad": "Modalidad", "Penalidad_Total": "Penalidad Total"},
    )
    fig4.update_layout(showlegend=False, yaxis=dict(rangemode="tozero"))
    st.plotly_chart(fig4, width="stretch")

st.subheader("Por Nivel")
por_nivel = df_f.groupby(["nivel", "modalidad"]).agg(
    Total_de_Penalidad=("penalidad", "count"), Penalidad_Total=("penalidad", "sum")
).reset_index()
col_e, col_f = st.columns(2)
with col_e:
    fig5 = px.bar(
        por_nivel, x="nivel", y="Total_de_Penalidad", color="modalidad", barmode="group",
        color_discrete_map={"en línea": "#1565c0", "híbrida": "#ef6c00"},
        text="Total_de_Penalidad",
        category_orders={"nivel": niveles_disp},
        labels={"nivel": "Nivel", "Total_de_Penalidad": "Total de Penalidad", "modalidad": "Modalidad"},
    )
    fig5.update_layout(yaxis=dict(rangemode="tozero"), legend_title_text="")
    st.plotly_chart(fig5, width="stretch")
with col_f:
    fig5b = px.bar(
        por_nivel, x="nivel", y="Penalidad_Total", color="modalidad", barmode="group",
        color_discrete_map={"en línea": "#1565c0", "híbrida": "#ef6c00"},
        text="Penalidad_Total",
        category_orders={"nivel": niveles_disp},
        labels={"nivel": "Nivel", "Penalidad_Total": "Penalidad Total", "modalidad": "Modalidad"},
    )
    fig5b.update_layout(yaxis=dict(rangemode="tozero"), legend_title_text="")
    st.plotly_chart(fig5b, width="stretch")

st.subheader("Por Materia")
por_materia = df_f.groupby(["materia", "nivel"]).size().reset_index(name="Total de Penalidad")
por_materia = por_materia.sort_values("Total de Penalidad", ascending=True)
fig6 = px.bar(
    por_materia, x="Total de Penalidad", y="materia", color="nivel", orientation="h",
    category_orders={"nivel": niveles_disp, "materia": por_materia["materia"].tolist()[::-1]},
    labels={"materia": "Materia", "nivel": "Nivel"},
)
fig6.update_layout(height=600, legend_title_text="Nivel")
st.plotly_chart(fig6, width="stretch")

st.markdown("---")
st.subheader("Detalle por Nombre")
estudiante_sel = st.selectbox("Seleccionar estudiante", ["Ninguno"] + sorted(resumen_f["nombre"].unique()))

if estudiante_sel != "Ninguno":
    fila = resumen_full[resumen_full["nombre"] == estudiante_sel].iloc[0]
    col_i1, col_i2, col_i3, col_i4 = st.columns(4)
    col_i1.metric("Modalidad", fila["modalidad"])
    col_i2.metric("Materias Pendientes", int(fila["pendientes"]))
    col_i3.metric("Penalidad Total", int(fila["penalidad_total"]))
    col_i4.metric("Estado de Penalidad", fila["estado_penalidad"])

    detalle_est = df[df["nombre"] == estudiante_sel].sort_values("nivel")
    tabla_est = detalle_est[["materia", "nivel", "penalidad"]].copy()
    tabla_est.columns = ["Materia", "Nivel", "Penalidad"]
    st.dataframe(tabla_est, width="stretch", hide_index=True)

st.markdown("---")
st.subheader("Datos por Estudiante")
tabla = resumen_full[["matricula", "nombre", "modalidad", "pendientes", "penalidad_total", "estado_penalidad"]].copy()
tabla.columns = ["Matrícula", "Nombre", "Modalidad", "Materias Pendientes", "Penalidad Total", "Estado de Penalidad"]
st.dataframe(tabla.sort_values(["Estado de Penalidad", "Nombre"]), width="stretch", hide_index=True)
