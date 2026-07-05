import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y TÍTULO
# ==========================================
st.set_page_config(page_title="Panel de Control", page_icon="📊", layout="wide")

st.title("📊 Mi Panel de Control en la Nube")
st.write("Los datos de este formulario se sincronizan directamente con Google Sheets en tiempo real.")

# ==========================================
# CONEXIÓN A LA BASE DE DATOS (GOOGLE SHEETS)
# ==========================================
# Se conecta automáticamente usando tu bloque [connections.gsheets] de los secretos
conn = st.connection("gsheets", type=GSheetsConnection)

# Intentar leer los datos actuales de la hoja
try:
    # ttl=0 fuerza al sistema a traer siempre lo último de internet sin usar memoria caché
    df_existente = conn.read(ttl=0)
except Exception as e:
    st.error(f"❌ Error al conectar con Google Sheets: {e}")
    df_existente = None

# ==========================================
# FORMULARIO DE REGISTRO DE DATOS
# ==========================================
# Dividimos la pantalla en dos columnas para una visualización más profesional
col1, col2 = st.columns([1, 2])

with col1:
    with st.form("formulario_ventas", clear_on_submit=True):
        st.subheader("📝 Registrar Información")
        
        producto = st.text_input("Nombre del Producto", placeholder="Ej. Laptop, Teclado...")
        ventas = st.number_input("Total de Ventas ($)", min_value=0, step=50, value=0)
        
        boton_guardar = st.form_submit_button("Guardar Datos")

# ==========================================
# ACCIÓN AL PRESIONAR EL BOTÓN GUARDAR
# ==========================================
if boton_guardar:
    if producto.strip() == "":
        st.warning("⚠️ Por favor, introduce el nombre de un producto.")
    elif df_existente is None:
        st.error("❌ No se puede guardar porque no hay conexión con la base de datos.")
    else:
        try:
            # Crear la nueva fila manteniendo consistencia con las mayúsculas de tu Excel
            nueva_fila = pd.DataFrame([{"PRODUCTO": producto.strip().upper(), "VENTAS": ventas}])
            
            # Unir los datos existentes con el nuevo registro
            df_actualizado = pd.concat([df_existente, nueva_fila], ignore_index=True)
            
            # Guardar y sobreescribir la hoja de Google Sheets completa
            conn.update(data=df_actualizado)
            
            # Efectos visuales de éxito en la interfaz
            st.success(f"¡Excelente! '{producto}' procesado correctamente.")
            st.balloons()
            
            # Forzar actualización de la variable para refrescar la gráfica de inmediato
            df_existente = df_actualizado
            
        except Exception as e:
            st.error(f"❌ Error al intentar escribir en Google Sheets: {e}")

# ==========================================
# MOSTRAR GRÁFICA EN VIVO
# ==========================================
with col2:
    st.subheader("Ventas Actualizadas en Vivo")
    
    if df_existente is not None and not df_existente.empty:
        try:
            # Detectar automáticamente si los nombres de columnas están en mayúsculas o minúsculas
            col_x = "PRODUCTO" if "PRODUCTO" in df_existente.columns else df_existente.columns[0]
            col_y = "VENTAS" if "VENTAS" in df_existente.columns else df_existente.columns[1]
            
            # Crear la gráfica interactiva de barras con Plotly
            fig = px.bar(
                df_existente, 
                x=col_x, 
                y=col_y, 
                title="Ventas por Producto", 
                color=col_x,
                text_auto=True  # Muestra el número exacto sobre cada barra
            )
            
            # Ajustes visuales para optimizar espacios
            fig.update_layout(showlegend=False, margin=dict(t=30, b=10, l=10, r=10))
            
            # Renderizar en la app
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.info("Formateando los datos para la gráfica...")
    else:
        st.info("Aún no hay datos registrados en el documento o la tabla está vacía.")