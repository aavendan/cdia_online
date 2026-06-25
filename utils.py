import pandas as pd
import streamlit as st
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "datos.xlsx")

@st.cache_data
def cargar_datos():
    df = pd.read_excel(DATA_PATH, engine="openpyxl")
    df.columns = df.columns.str.strip()
    df["periodo_label"] = df["anio_ingreso"].astype(str) + " - P" + df["periodo_ingreso"].astype(str)
    return df
