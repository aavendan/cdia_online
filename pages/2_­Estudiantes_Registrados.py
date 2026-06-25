import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import cargar_datos, cargar_ingreso

st.set_page_config(page_title="Estudiantes - CDIA", page_icon="👤", layout="wide")
st.title("👤 Análisis por Estudiantes Registrados")

df = cargar_datos()
df_ing = cargar_ingreso()

# Build per-student inscriptions table
registros = []
for _, row in df.iterrows():
    for nombre in row["estudiantes"].split(","):
        nombre = nombre.strip().upper()
        if nombre:
            registros.append({
                "Estudiante": nombre,
                "Materia": row["nombre_materia"],
                "Código": row["codigo_materia"],
                "Nivel": row["nivel_materia"],
                "Período": row["periodo_label"],
            })

df_est = pd.DataFrame(registros)

# --- Filters ---
col1, col2, col3 = st.columns([1, 1, 2])

anios = sorted(df_ing["anio"].unique())
with col1:
    anio_sel = st.selectbox("Año de ingreso", ["Todos"] + [str(a) for a in anios])

paos_disponibles = (
    sorted(df_ing["pao"].unique())
    if anio_sel == "Todos"
    else sorted(df_ing[df_ing["anio"] == int(anio_sel)]["pao"].unique())
)
with col2:
    pao_sel = st.selectbox("Período de ingreso", ["Todos"] + [str(p) for p in paos_disponibles])

# Filter ingreso table to get matching student names
df_ing_f = df_ing.copy()
if anio_sel != "Todos":
    df_ing_f = df_ing_f[df_ing_f["anio"] == int(anio_sel)]
if pao_sel != "Todos":
    df_ing_f = df_ing_f[df_ing_f["pao"] == int(pao_sel)]

nombres_en_tabla = set(df_est["Estudiante"].unique())
nombres_filtrados = sorted(df_ing_f[df_ing_f["nombre"].isin(nombres_en_tabla)]["nombre"].unique())

with col3:
    estudiante_sel = st.selectbox(
        "Estudiante",
        ["Todos"] + nombres_filtrados,
    )

st.markdown("---")

# Apply filters to inscriptions table
df_view = df_est.copy()
if nombres_filtrados:
    df_view = df_view[df_view["Estudiante"].isin(nombres_filtrados)]
if estudiante_sel != "Todos":
    df_view = df_view[df_view["Estudiante"] == estudiante_sel]

estudiantes_unicos = sorted(df_view["Estudiante"].unique())
st.metric("Estudiantes encontrados", len(estudiantes_unicos))


# Detail view when a specific student is selected
if estudiante_sel != "Todos":
    datos = df_view[df_view["Estudiante"] == estudiante_sel]
    info = df_ing_f[df_ing_f["nombre"] == estudiante_sel]
    if not info.empty:
        r = info.iloc[0]
        st.markdown(
            f"**Matrícula:** {r['matricula']} &nbsp;|&nbsp; "
            f"**Ingreso:** {r['anio']} - P{r['pao']} &nbsp;|&nbsp; "
            f"**Promedio:** {r['promedio']:.2f}"
        )
    st.dataframe(
        datos[["Nivel", "Código", "Materia", "Período"]].sort_values(["Nivel", "Materia"]),
        width="stretch",
        hide_index=True,
    )
else:
    st.subheader("Datos")
    st.dataframe(
        df_view.sort_values(["Estudiante", "Nivel", "Materia"]),
        width="stretch",
        hide_index=True,
    )
