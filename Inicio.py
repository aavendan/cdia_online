import streamlit as st

st.set_page_config(
    page_title="Registros PAO I 2026",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 Registros PAO I 2026")
st.subheader("Ciencia de Datos e Inteligencia Artificial - Modalidad en línea")

st.markdown("---")

st.markdown(
    """
    Esta aplicación permite analizar el registro de estudiantes por:

    - 📊 **Registros**
    - 📅 **Período de ingreso**
    - 📚 **Nivel de materia**
    - 📖 **Materia**
    - 👤 **Estudiantes registrados**
    """
)

st.info("Utilice el menú lateral para navegar entre las páginas.")
