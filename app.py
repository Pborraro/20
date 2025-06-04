import streamlit as st
import pandas as pd
from fpdf import FPDF

# Cargar base de datos de perfiles desde CSV
@st.cache_data
def cargar_base():
    return pd.read_csv("base_perfiles_fexa.csv", dtype={"Código": str})

df_base = cargar_base()

st.set_page_config(page_title="FEXA - Cortes y Vidrios", layout="centered")
st.title("📐 App de Cortes y Evaluación de Vidrios")

st.markdown("### Cargar perfil")
codigo_input = st.text_input("Código del perfil (máx. 4 dígitos)", max_chars=4)

perfil = df_base[df_base["Código"] == codigo_input] if codigo_input else pd.DataFrame()

if not perfil.empty:
    nombre = perfil["Nombre"].values[0]
    peso = perfil["Peso (kg/m)"].values[0]
    largo = perfil["Largo (m)"].values[0]
    st.success(f"✔ Perfil encontrado: {nombre} | Peso: {peso} kg/m | Largo: {largo} m")
else:
    nombre = st.text_input("Nombre del perfil")
    peso = st.number_input("Peso por metro (kg)", min_value=0.01)
    largo = st.number_input("Largo de barra (m)", min_value=0.01, max_value=6.20)

precio = st.number_input("Precio del kg ($)", min_value=0.01)

st.markdown("### Cargar vidrio")
usar_vidrio = st.radio("¿Va a usar vidrio?", ["No", "Sí"]) == "Sí"
if usar_vidrio:
    a = st.number_input("Ancho (mm)", min_value=1.0)
    h = st.number_input("Alto (mm)", min_value=1.0)
    espesor = st.number_input("Espesor (mm)", min_value=4.0)
    tipo = st.selectbox("Tipo de vidrio", ["Float", "Templado", "Laminado", "DVH"])
    area = a * h / 1_000_000
    peso_vidrio = area * espesor * 2.531
    st.success(f"Área: {area:.3f} m² | Peso: {peso_vidrio:.2f} kg")

    limite = 2.0  # ejemplo
    if area > limite:
        st.error("INSEGURO: Excede el área permitida")
        st.info("Sugerencia: usar vidrio templado o reducir dimensiones")
    else:
        st.success("SEGURO")

st.markdown("### Exportar PDF")
if st.button("Generar PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Perfil {codigo_input} - {nombre}", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Peso: {peso} kg/m | Largo: {largo} m | Precio/kg: ${precio}", ln=True)
    if usar_vidrio:
        pdf.cell(0, 10, f"Vidrio: {tipo} {espesor} mm - {area:.3f} m² - {peso_vidrio:.2f} kg", ln=True)
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    st.download_button("📄 Descargar PDF", data=pdf_bytes, file_name="corte.pdf", mime="application/pdf")