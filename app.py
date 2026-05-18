import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Consolidador de Obra", layout="wide")
st.title("📂 Unificador de Reportes de Obra")
st.write("Sube los archivos Excel de los trabajadores para generar el Informe Maestro.")

# --- 1. SUBIDA DE ARCHIVOS ---
archivos_subidos = st.file_uploader(
    "Selecciona los archivos .xlsx", 
    type="xlsx", 
    accept_multiple_files=True
)

if archivos_subidos:
    lista_df = []
    
    for archivo in archivos_subidos:
        try:
            # Leemos cada archivo asegurando el motor openpyxl
            df_temp = pd.read_excel(archivo, engine='openpyxl')
            lista_df.append(df_temp)
        except Exception as e:
            st.error(f"Error al leer {archivo.name}: {e}")

    if lista_df:
        # Unificamos todos los datos
        df_maestro = pd.concat(lista_df, ignore_index=True).drop_duplicates()

        st.divider()
        st.subheader("📊 Visualización Global del Estado de la Obra")
        
        # --- BLOQUE DE COLUMNAS (CORREGIDO) ---
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Tareas", len(df_maestro))
        
        with col2:
            if "Trabajador" in df_maestro.columns:
                st.metric("Trabajadores", df_maestro["Trabajador"].nunique())
            else:
                st.metric("Trabajadores", "0")
            
        with col3:
            # Cálculo de progreso si existe la columna Estado
            if "Estado" in df_maestro.columns:
                valor_estado = {
                    "Avance de la tarea en torno al 25% aprox.": 25,
                    "Avance de la tarea en torno al 50% aprox.": 50,
                    "Avance de la tarea en torno al 75% aprox.": 75,
                    "OK, finalizado sin errores": 100,
                    "Finalizado, pero con errores pendientes de corregir": 90,
                    "Finalizado y corregidos los errores": 100
                }
                progreso = df_maestro["Estado"].map(valor_estado).mean()
                st.metric("Progreso Global", f"{progreso:.1f}%")
                st.progress(progreso / 100)
            else:
                st.metric("Progreso Global", "N/A")

        # --- TABLA Y DESCARGA ---
        st.write("### 📝 Tabla Maestra Unificada")
        st.dataframe(df_maestro, use_container_width=True)

        archivo_final = "Informe_Maestro_Obra.xlsx"
        df_maestro.to_excel(archivo_final, index=False)
        
        with open(archivo_final, "rb") as f:
            st.download_button(
                label="📥 Descargar Excel Maestro",
                data=f,
                file_name=archivo_final,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.info("💡 Arrastra aquí los Excels que te han enviado los trabajadores.")
