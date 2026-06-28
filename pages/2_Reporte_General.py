import streamlit as st
import pandas as pd
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

for df in [df_registrados, df_sin_registro, df_homologados]:
    df.columns = COL_NAMES
    df.sort_values(["Año de Ingreso", "Período de Ingreso", "Nombre"], inplace=True)

# --- Descarga Excel ---
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df_registrados.to_excel(writer, sheet_name="Registrados", index=False)
    df_sin_registro.to_excel(writer, sheet_name="Sin Registros", index=False)
    df_homologados.to_excel(writer, sheet_name="Homologados", index=False)

st.download_button(
    label="⬇️ Descargar Excel",
    data=buffer.getvalue(),
    file_name="reporte_general_cdia.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.markdown("---")

tab1, tab2, tab3 = st.tabs([
    f"✅ Registrados ({len(df_registrados)})",
    f"❌ Sin Registros ({len(df_sin_registro)})",
    f"🔄 Homologados ({len(df_homologados)})",
])

with tab1:
    st.dataframe(df_registrados, width="stretch", hide_index=True)

with tab2:
    st.dataframe(df_sin_registro, width="stretch", hide_index=True)

with tab3:
    st.dataframe(df_homologados, width="stretch", hide_index=True)
