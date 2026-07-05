import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y TÍTULO
# ==========================================
st.set_page_config(page_title="Panel de Control", page_icon="📊", layout="wide")

st.title("📊 Mi Panel de Control en la Nube")
st.write("Los datos de este formulario se sincronizan directamente con Google Sheets en tiempo real.")

# ==========================================
# 2. CONEXIÓN A LA BASE DE DATOS (GOOGLE SHEETS)
# ==========================================
# Se conecta de forma segura usando la sección [connections.gsheets] de tus Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# Intentar leer los datos actuales de la hoja
try:
    # Se fuerza a limpiar la caché para que siempre traiga los datos más recientes de internet
    df_existente = conn.read(ttl=0)
except Exception as e:
    st.error(f"❌ Error al conectar con Google Sheets: {e}")
    df_existente = None

# ==========================================
# 3. FORMULARIO DE REGISTRO DE DATOS
# ==========================================
# Usamos columnas para centrar y estilizar el formulario
col1, col2 = st.columns([1, 2])

with col1:
    with st.form("formulario_ventas", clear_on_submit=True):
        st.subheader("📝 Registrar Información")
        
        producto = st.text_input("Nombre del Producto", placeholder="Ej. Laptop, Teclado...")
        ventas = st.number_input("Total de Ventas ($)", min_value=0, step=50, value=0)
        
        boton_guardar = st.form_submit_button("Guardar Datos")

# ==========================================
# 4. ACCIÓN AL PRESIONAR EL BOTÓN GUARDAR
# ==========================================
if boton_guardar:
    if producto.strip() == "":
        st.warning("⚠️ Por favor, introduce el nombre de un producto.")
    elif df_existente is None:
        st.error("❌ No se puede guardar porque no hay conexión con la base de datos.")
    else:
        try:
            # Crear la nueva fila con los datos ingresados por el usuario
            nueva_fila = pd.DataFrame([{"PRODUCTO": producto.strip(), "VENTAS": ventas}])
            
            # Asegurar que las columnas coincidan en mayúsculas/minúsculas con tu Sheets
            # Si tu Google Sheets usa "PRODUCTO" y "VENTAS", esto lo junta perfectamente
            df_actualizado = pd.concat([df_existente, nueva_fila], ignore_index=True)
            
            # Subir y sobreescribir la hoja de Google con la nueva información
            conn.update(data=df_actualizado)
            
            # Mensajes visuales de éxito total
            st.success(f"¡Excelente! '{producto}' procesado correctamente.")
            st.balloons()
            
            # Forzar actualización inmediata de los datos para la gráfica
            df_existente = df_actualizado
            
        except Exception as e:
            st.error(f"❌ Error al intentar escribir en Google Sheets: {e}")

# ==========================================
# 5. MOSTRAR GRÁFICA EN VIVO
# ==========================================
with col2:
    st.subheader("Ventas Actualizadas en Vivo")
    
    if df_existente is not None and not df_existente.empty:
        try:
            # Detectar automáticamente los nombres reales de tus columnas
            col_x = "PRODUCTO" if "PRODUCTO" in df_existente.columns else df_existente.columns[0]
            col_y = "VENTAS" if "VENTAS" in df_existente.columns else df_existente.columns[1]
            
            # Crear la gráfica de barras interactiva con Plotly
            fig = px.bar(
                df_existente, 
                x=col_x, 
                y=col_y, 
                title="Ventas por Producto", 
                color=col_x,
                text_auto=True # Muestra el valor encima de cada barra
            )
            
            # Ajustes visuales para que se vea profesional
            fig.update_layout(showlegend=False, margin=dict(t=30, b=10, l=10, r=10))
            
            # Renderizar la gráfica en la pantalla web
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.info("Estructurando los datos para la gráfica...")
    else:
        st.info("Aún no hay datos registrados en el documento o la tabla está vacía.")