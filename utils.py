import pandas as pd
import streamlit as st
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "data/registros.xlsx")
INGRESO_PATH = os.path.join(os.path.dirname(__file__), "data/estudiantes_ingreso_enlinea.xlsx")
HISTORIAL_PATH = os.path.join(os.path.dirname(__file__), "data_dropout/historial_academico_2024II.xlsx")
AVANCE_PATH = os.path.join(os.path.dirname(__file__), "data_dropout/avance_2024II.xlsx")

@st.cache_data
def cargar_datos():
    df = pd.read_excel(DATA_PATH, engine="openpyxl")
    df.columns = df.columns.str.strip()
    df["periodo_label"] = df["anio_ingreso"].astype(str) + " - P" + df["periodo_ingreso"].astype(str)
    return df

@st.cache_data
def cargar_migrados():
    df = pd.read_excel(INGRESO_PATH, engine="openpyxl")
    df.columns = df.columns.str.strip()
    df.rename(columns={df.columns[0]: "matricula"}, inplace=True)
    df["nombre"] = df["nombre"].str.strip().str.upper()
    df = df[df["estado"].str.strip().str.upper() == "STA"]
    return df

@st.cache_data
def cargar_ingreso():
    df = pd.read_excel(INGRESO_PATH, engine="openpyxl")
    df.columns = df.columns.str.strip()
    df.rename(columns={df.columns[0]: "matricula"}, inplace=True)
    df["nombre"] = df["nombre"].str.strip().str.upper()
    df = df[df["estado"].str.strip().str.upper() == "ADMISIONES"]
    return df

@st.cache_data
def cargar_historial_academico():
    df = pd.read_excel(HISTORIAL_PATH, sheet_name="Historial 2024-II", engine="openpyxl")
    df.columns = df.columns.str.strip()
    df.columns = ["matricula", "nombre", "modalidad", "anio_termino", "codigo",
                  "materia", "creditos", "no_vez", "estado", "nivel", "penalidad"]
    df["nombre"] = df["nombre"].str.strip().str.upper()
    df["creditos"] = pd.to_numeric(df["creditos"].astype(str).str.replace(",", "."), errors="coerce")
    return df

@st.cache_data
def cargar_materias_pendientes():
    df = pd.read_excel(AVANCE_PATH, sheet_name="Materias pendientes", engine="openpyxl")
    df.columns = df.columns.str.strip()
    df.columns = ["matricula", "nombre", "modalidad", "materia", "nivel", "penalidad"]
    df["nombre"] = df["nombre"].str.strip().str.upper()
    return df

@st.cache_data
def cargar_penalidad_referencia():
    df = pd.read_excel(AVANCE_PATH, sheet_name="Penalidad", engine="openpyxl")
    df.columns = ["nivel", "penalidad"]
    return df
