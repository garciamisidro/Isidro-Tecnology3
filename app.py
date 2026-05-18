import streamlit as st
import pandas as pd
from datetime import date

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Consolidador de Obra", layout="wide")
st.title("📂 Unificador de Reportes de Obra")
st.write("Sube todos los archivos Excel de los trabajadores para generar el Informe Maestro.")

# --- 1. SUBIDA DE ARCHIVOS MÚLTIPLES ---
archivos_subidos = st.file_uploader(
    "Selecciona todos los archivos .xlsx", 
    type="xlsx", 
    accept_multiple_files=True
)

if archivos_subidos:
    lista_df = []
    
    # Procesar cada archivo subido
    for archivo in archivos_subidos:
        try:
            df_temp = pd.read_excel(archivo)
            lista_df.append(df_temp)
        except Exception as e:
            st.error(f"Error al leer {archivo.name}: {e}")

    if lista_df:
        # --- 2. UNIFICACIÓN (RA3/RA4) ---
        # Concatenamos todos los Excels en uno solo
        df_maestro = pd.concat(lista_df, ignore_index=True)
        
        # Limpieza: Eliminamos filas que sean exactamente iguales si las hay
        df_maestro = df_maestro.drop_duplicates()

        st.success(f"✅ Se han unificado {len(archivos_subidos)} archivos con éxito.")

        # --- 3. DASHBOARD GLOBAL DE ESTADO DE OBRA ---
        st.divider()
        st.subheader("📊 Visualización Global del Estado de la Obra")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_registros = len(df_maestro)
            st.metric("Total de Tareas Reportadas", total_registros)
        
with col2:
            # Verificamos si la columna existe antes de contar
            if "Trabajador" in df_maestro.columns:
                num_trabajadores = df_maestro["Trabajador"].nunique()
                st.metric("Trabajadores Activos", num_trabajadores)
            else:
                st.metric("Trabajadores Activos", "N/A")
                st.warning("⚠️ No se encontró la columna 'Trabajador' en los archivos.")
        with col3:
            # Cálculo de progreso medio global
            valor_estado = {
                "Avance de la tarea en torno al 25% aprox.": 25,
                "Avance de la tarea en torno al 50% aprox.": 50,
                "Avance de la tarea en torno al 75% aprox.": 75,
                "OK, finalizado sin errores": 100,
                "Finalizado, pero con errores pendientes de corregir": 90,
                "Finalizado y corregidos los errores": 100
            }
            if "Estado" in df_maestro.columns:
                progreso_global = df_maestro["Estado"].map(valor_estado).mean()
                st.metric("Progreso Global Obra", f"{progreso_global:.1f}%")
                st.progress(progreso_global / 100)

        # --- 4. TABLA MAESTRA INTERACTIVA ---
        st.write("### 📝 Tabla Maestra de Seguimiento")
        # Filtro interactivo por trabajador
        filtro_trabajador = st.multiselect("Filtrar por trabajador:", df_maestro["Trabajador"].unique())
        
        df_filtrado = df_maestro
        if filtro_trabajador:
            df_filtrado = df_maestro[df_maestro["Trabajador"].isin(filtro_trabajador)]
            
        st.dataframe(df_filtrado, use_container_width=True)

        # --- 5. EXPORTACIÓN DEL ARCHIVO FINAL ---
        st.divider()
        archivo_final = "Informe_Maestro_Obra.xlsx"
        df_maestro.to_excel(archivo_final, index=False)
        
        st.download_button(
            label="📥 Descargar Excel Maestro Unificado",
            data=open(archivo_final, "rb"),
            file_name=archivo_final,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("Esperando archivos... Por favor, sube los reportes recibidos por correo.")
