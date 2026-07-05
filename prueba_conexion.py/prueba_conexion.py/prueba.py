import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("📊 Mi Panel de Control en la Nube")
st.write("Los datos de este formulario se sincronizan directamente con Google Sheets.")

# Conexión directa usando la librería oficial y las credenciales seguras de Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. Leer los datos existentes
try:
    df_existente = conn.read()
except Exception as e:
    st.error(f"Error al conectar con las hojas de Google: {e}")
    df_existente = None

# 2. Formulario para registrar información
with st.form("formulario_ventas"):
    st.subheader("📝 Registrar Información")
    producto = st.text_input("Nombre del Producto")
    ventas = st.number_input("Total de Ventas ($)", min_value=0, step=100)
    boton_guardar = st.form_submit_button("Guardar Datos")

# 3. Acción al presionar el botón Guardar
if boton_guardar:
    if producto.strip() == "":
        st.warning("⚠️ Por favor, introduce el nombre de un producto.")
    elif df_existente is None:
        st.error("❌ No se puede guardar porque no hay conexión con la base de datos.")
    else:
        try:
            # Añadir la nueva fila al DataFrame existente
            import pandas as pd
            nueva_fila = pd.DataFrame([{"Producto": producto, "Ventas": ventas}])
            df_actualizado = pd.concat([df_existente, nueva_fila], ignore_index=True)
            
            # Subir y sobreescribir la hoja de Google con el dato nuevo
            conn.update(data=df_actualizado)
            
            st.success(f"✅ ¡Datos guardados en Google Sheets! Producto: {producto} | Ventas: ${ventas}")
            st.balloons() # ¡Globos de celebración!
        except Exception as e:
            st.error(f"❌ Error al intentar escribir en Google Sheets: {e}")

# 4. Mostrar Gráfica en Vivo si hay datos
if df_existente is not None and not df_existente.empty:
    st.subheader("Ventas Actualizadas en Vivo")
    import plotly.express as px
    fig = px.bar(df_existente, x="Producto", y="Ventas", title="Ventas por Producto", color="Producto")
    st.plotly_chart(fig, use_container_width=True)