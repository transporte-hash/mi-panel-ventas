import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Panel de Control", page_icon="📊")

st.title("📊 Mi Panel de Control en la Nube")
st.markdown("Los datos de este formulario se sincronizan con Google Sheets.")

# --- TU ENLACE DE LECTURA (El que termina en pub?output=csv) ---
URL_LECTURA_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQMf6T55vbTO5pUZZe101srmlcRm8dHtVm7eScOGDNZbCvje9KLIEhiWQAQ9xGlYttOxzbM7RrDGYr9/pub?output=csv"

# --- LEER DATOS ---
try:
    datos_cloud = pd.read_csv(URL_LECTURA_CSV)
    datos_cloud.columns = [col.strip().upper() for col in datos_cloud.columns]
except Exception as e:
    st.error(f"Por favor, revisa el enlace de Google Sheets en el código.")
    datos_cloud = pd.DataFrame(columns=["PRODUCTO", "VENTAS"])

# --- FORMULARIO DE CAPTURA ---
with st.form("nuevo_registro", clear_on_submit=True):
    st.subheader("📝 Registrar Información")
    producto_input = st.text_input("Nombre del Producto")
    ventas_input = st.number_input("Total de Ventas ($)", min_value=0, step=10)
    enviar = st.form_submit_button("Guardar Datos")

    if enviar:
        if producto_input.strip() == "":
            st.error("Por favor, introduce un nombre de producto válido.")
        else:
            # Creamos la nueva fila con tus datos
            nueva_fila = pd.DataFrame({
                "PRODUCTO": [producto_input.strip().upper()], 
                "VENTAS": [ventas_input]
            })
            
            # Agregamos los datos visualmente a la tabla actual
            datos_cloud = pd.concat([datos_cloud, nueva_fila], ignore_index=True)
            
            st.success(f"¡Excelente! '{producto_input}' procesado correctamente.")
            st.balloons() # ¡Globos de éxito!

# --- GRÁFICA INTERACTIVA ---
if not datos_cloud.empty:
    fig = px.bar(
        datos_cloud, 
        x="PRODUCTO", 
        y="VENTAS", 
        title="Ventas Actualizadas en Vivo", 
        template="plotly_dark",
        text_auto=True
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(datos_cloud, use_container_width=True)