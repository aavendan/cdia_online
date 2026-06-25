import pandas as pd
import streamlit as st
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "data/registros.xlsx")
INGRESO_PATH = os.path.join(os.path.dirname(__file__), "data/estudiantes_ingreso_enlinea.xlsx")

@st.cache_data
def cargar_datos():
    df = pd.read_excel(DATA_PATH, engine="openpyxl")
    df.columns = df.columns.str.strip()
    df["periodo_label"] = df["anio_ingreso"].astype(str) + " - P" + df["periodo_ingreso"].astype(str)
    return df

@st.cache_data
def cargar_ingreso():
    df = pd.read_excel(INGRESO_PATH, engine="openpyxl")
    df.columns = df.columns.str.strip()
    df.rename(columns={df.columns[0]: "matricula"}, inplace=True)
    df["nombre"] = df["nombre"].str.strip().str.upper()
    return df
