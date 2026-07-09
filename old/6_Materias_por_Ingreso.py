import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import cargar_datos, cargar_ingreso

st.set_page_config(page_title="Materias por Ingreso - CDIA", page_icon="🗓️", layout="wide")
st.title("🗓️ Materias por Año y Período de Ingreso")

df = cargar_datos()
df_ing = cargar_ingreso()

# --- Filters ---
col1, col2 = st.columns(2)

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

# Filter ingreso to get student names for the selected cohort
df_ing_f = df_ing.copy()
if anio_sel != "Todos":
    df_ing_f = df_ing_f[df_ing_f["anio"] == int(anio_sel)]
if pao_sel != "Todos":
    df_ing_f = df_ing_f[df_ing_f["pao"] == int(pao_sel)]

nombres_cohorte = set(df_ing_f["nombre"].unique())

st.markdown("---")
st.metric("Estudiantes en la cohorte", len(nombres_cohorte))

# Build per-student inscriptions from datos.xlsx
registros = []
for _, row in df.iterrows():
    for nombre in row["estudiantes"].split(","):
        nombre = nombre.strip().upper()
        if nombre and nombre in nombres_cohorte:
            registros.append({
                "Estudiante": nombre,
                "Materia": row["nombre_materia"],
                "Período": row["periodo_label"],
            })

if not registros:
    st.info("No hay registros para la cohorte seleccionada.")
    st.stop()

df_reg = pd.DataFrame(registros)

# All axes for the heatmap
todos_estudiantes = sorted(nombres_cohorte)
todas_materias = sorted(df["nombre_materia"].unique())

# Pivot: rows = materias, columns = estudiantes, value = count of registros
pivot = df_reg.groupby(["Materia", "Estudiante"]).size().reset_index(name="Registros")
pivot = pivot.pivot(index="Materia", columns="Estudiante", values="Registros")
pivot = pivot.reindex(index=todas_materias, columns=todos_estudiantes, fill_value=0).fillna(0).astype(int)

st.subheader("Heatmap: materias × estudiantes")
fig = px.imshow(
    pivot,
    text_auto=True,
    color_continuous_scale=[[0, "#f0f4ff"], [0.01, "#80cbc4"], [1, "#00695c"]],
    aspect="auto",
    labels=dict(x="Estudiante", y="Materia", color="Registros"),
)
fig.update_layout(
    coloraxis_showscale=False,
    xaxis=dict(tickangle=45),
)
st.plotly_chart(fig, width="stretch")
