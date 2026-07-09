import streamlit as st

st.set_page_config(
    page_title="Registros PAO I 2026",
    page_icon="🎓",
    layout="wide",
)

pg = st.navigation({
    "General": [
        st.Page("pages/2_Reporte_General.py", title="Reporte General", icon="📋"),
    ],
    "Avance en la Malla": [
        st.Page("pages/11_Materias_Pendientes.py", title="Materias Pendientes", icon="📌"),
    ],
    "Estudiantes Registrados": [
        st.Page("pages/3_Estudiantes_Registrados.py", title="Resumen", icon="👤"),
        st.Page("pages/1_Registros.py", title="Por Registros", icon="📊"),
        st.Page("pages/4_Periodo_de_Ingreso.py", title="Por Período de Ingreso", icon="📅"),
        st.Page("pages/5_Nivel_de_Materia.py", title="Por Nivel de Materia", icon="📚"),
        st.Page("pages/6_Materia.py", title="Por Materia", icon="📖"),
    ],
    "Estudiantes Homologados": [
        st.Page("pages/7_Estudiantes_Homologados_Grupal.py", title="Análisis Grupal", icon="🔄"),
        st.Page("pages/8_Estudiantes_Homologados_Individual.py", title="Análisis Individual", icon="🔎"),
    ],
    "Estudiantes Sin Registros": [
        st.Page("pages/9_Estudiantes_Sin_Registros.py", title="Resumen", icon="❌"),
    ],
    
})

pg.run()
