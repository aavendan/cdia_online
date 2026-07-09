import streamlit as st
import pandas as pd
import plotly.express as px
import io
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import cargar_datos, cargar_ingreso, cargar_migrados

st.set_page_config(page_title="Reporte General - CDIA", page_icon="📋", layout="wide")
st.title("📋 Reporte General")

df_reg = cargar_datos()
df_ing = cargar_ingreso()
df_mig = cargar_migrados()

COLS = ["matricula", "nombre", "anio", "pao", "promedio"]
COL_NAMES = ["Matrícula", "Nombre", "Año de Ingreso", "Período de Ingreso", "Promedio"]

# Nombres con al menos un registro
nombres_con_registro = set()
for nombres_str in df_reg["estudiantes"].dropna():
    for nombre in nombres_str.split(","):
        nombre = nombre.strip().upper()
        if nombre:
            nombres_con_registro.add(nombre)

df_registrados = df_ing[df_ing["nombre"].isin(nombres_con_registro)][COLS].copy()
df_sin_registro = df_ing[~df_ing["nombre"].isin(nombres_con_registro)][COLS].copy()
df_homologados = df_mig[COLS].copy()

# --- Filters ---
todos = pd.concat([df_registrados, df_sin_registro, df_homologados])
col1, col2 = st.columns(2)

anios = sorted(todos["anio"].unique())
with col1:
    anio_sel = st.selectbox("Año de ingreso", ["Todos"] + [str(a) for a in anios])

paos_disponibles = (
    sorted(todos["pao"].unique())
    if anio_sel == "Todos"
    else sorted(todos[todos["anio"] == int(anio_sel)]["pao"].unique())
)
with col2:
    pao_sel = st.selectbox("Período de ingreso", ["Todos"] + [str(p) for p in paos_disponibles])

def aplicar_filtro(df):
    if anio_sel != "Todos":
        df = df[df["anio"] == int(anio_sel)]
    if pao_sel != "Todos":
        df = df[df["pao"] == int(pao_sel)]
    df = df.copy()
    df.columns = COL_NAMES
    df.sort_values(["Año de Ingreso", "Período de Ingreso", "Nombre"], inplace=True)
    return df

df_r = aplicar_filtro(df_registrados)
df_s = aplicar_filtro(df_sin_registro)
df_h = aplicar_filtro(df_homologados)

st.markdown("---")

# --- Gráfico de barras agrupadas ---
def conteo_por_periodo(df, label):
    df = df.copy()
    df["periodo_label"] = df["Año de Ingreso"].astype(str) + " - P" + df["Período de Ingreso"].astype(str)
    return df.groupby("periodo_label").size().reset_index(name="Estudiantes").assign(Grupo=label)

resumen = pd.concat([
    conteo_por_periodo(df_r, "Registrados"),
    conteo_por_periodo(df_s, "Sin Registros"),
    conteo_por_periodo(df_h, "Homologados"),
])

periodos_orden = sorted(resumen["periodo_label"].unique())

fig = px.bar(
    resumen, x="periodo_label", y="Estudiantes", color="Grupo", barmode="group",
    color_discrete_map={"Registrados": "#00695c", "Sin Registros": "#b71c1c", "Homologados": "#1565c0"},
    text="Estudiantes",
    category_orders={"periodo_label": periodos_orden, "Grupo": ["Registrados", "Sin Registros", "Homologados"]},
    labels={"periodo_label": "Período de Ingreso"},
)
fig.update_layout(yaxis=dict(rangemode="tozero"), legend_title_text="")
st.plotly_chart(fig, width="stretch")

# --- Descarga Excel (datos filtrados) ---
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df_r.to_excel(writer, sheet_name="Registrados", index=False)
    df_s.to_excel(writer, sheet_name="Sin Registros", index=False)
    df_h.to_excel(writer, sheet_name="Homologados", index=False)

st.download_button(
    label="⬇️ Descargar Excel",
    data=buffer.getvalue(),
    file_name="reporte_general_cdia.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.markdown("---")

tab1, tab2, tab3 = st.tabs([
    f"✅ Registrados ({len(df_r)})",
    f"❌ Sin Registros ({len(df_s)})",
    f"🔄 Homologados ({len(df_h)})",
])

with tab1:
    st.dataframe(df_r, width="stretch", hide_index=True)

with tab2:
    st.dataframe(df_s, width="stretch", hide_index=True)

with tab3:
    st.dataframe(df_h, width="stretch", hide_index=True)
