import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Configuración inicial de la página
st.set_page_config(page_title="Dashboard de Diagnóstico - Curso", layout="wide")

# 1. CARGA Y PREPARACIÓN DE DATOS
@st.cache_data
def load_data():
    # Leer el archivo Excel que subiste
    df = pd.read_excel("datos.xlsx", skiprows=1) # skiprows=1 omite la fila de metadata de Qualtrics si la tiene
    
    # Diccionario para acortar los nombres de las columnas de la encuesta
    column_mapping = {
        "Nombre completo": "Nombre",
        "Área funcional": "Area",
        "Años de experiencia laboral": "Experiencia",
        "Formación cuantitativa previa": "Formacion",
        "¿Con qué frecuencia usas herramientas de análisis cuantitativo en tu trabajo?": "Uso_Cuantitativo",
        "Autoevaluación en Python — indica tu grado de acuerdo con cada afirmación - Puedo escribir un bucle for y una función": "Python_Bucle",
        "Autoevaluación en Python — indica tu grado de acuerdo con cada afirmación - He usado pandas para manipular datos": "Python_Pandas",
        "¿Te interesaría que el curso incluyera aplicaciones financieras apoyadas en IA / machine learning?": "Interes_IA",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Automatización de reportes financieros": "Ranking_Automatizacion",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Riesgo de crédito y scoring": "Ranking_RiesgoCredito",
        "¿Qué te gustaría poder hacer al terminar el curso que hoy no puedas?": "Expectativas"
    }
    
    # Renombrar las columnas
    df = df.rename(columns=lambda x: column_mapping.get(x, x))
    
    # --- TRANSFORMACIÓN PARA EL MODELO ---
    likert_map = {
        "Totalmente en desacuerdo": 1, 
        "En desacuerdo": 2, 
        "Neutral": 3, 
        "De acuerdo": 4, 
        "Totalmente de acuerdo": 5
    }
    
    # Crear un "Score Técnico" numérico
    if 'Python_Bucle' in df.columns:
        df['Score_Bucle'] = df['Python_Bucle'].map(likert_map).fillna(1)
        df['Score_Pandas'] = df['Python_Pandas'].map(likert_map).fillna(1)
        df['Score_Python_Total'] = df['Score_Bucle'] + df['Score_Pandas']
    else:
        df['Score_Python_Total'] = 0

    # Limpiar columnas numéricas para el ranking (llenar vacíos con 7 que es baja prioridad)
    if 'Ranking_Automatizacion' in df.columns:
        df['Ranking_Automatizacion'] = pd.to_numeric(df['Ranking_Automatizacion'], errors='coerce').fillna(7)
        df['Ranking_RiesgoCredito'] = pd.to_numeric(df['Ranking_RiesgoCredito'], errors='coerce').fillna(7)

    return df

# Cargar los datos
try:
    df = load_data()
except Exception as e:
    st.error(f"Error al cargar los datos. Verifica el archivo datos.xlsx. Detalle: {e}")
    st.stop()

# Título del Dashboard
st.title("📊 Tablero de Diagnóstico y Diseño Curricular")
st.markdown("Análisis de perfil de estudiantes, nivel técnico y expectativas para personalización del curso.")

# Crear pestañas
tab1, tab2, tab3 = st.tabs(["👥 Perfil General", "📈 Correlaciones y Nivel Técnico", "🎯 Expectativas del Curso"])

# --- PESTAÑA 1: PERFIL GENERAL ---
with tab1:
    st.header("Demografía y Background de los Estudiantes")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Matriculados", len(df))
    
    if 'Uso_Cuantitativo' in df.columns:
        alto_uso = len(df[df['Uso_Cuantitativo'].isin(['Diario', 'Semanal'])])
        col2.metric("Dominio Cuantitativo Alto", f"{(alto_uso/len(df)*100):.0f}%")
        
    if 'Score_Python_Total' in df.columns:
        col3.metric("Score Técnico Promedio", f"{df['Score_Python_Total'].mean():.1f}/10")
    
    c1, c2 = st.columns(2)
    with c1:
        if 'Formacion' in df.columns:
            fig_formacion = px.pie(df, names='Formacion', title='Formación Académica Previa', hole=0.4)
            st.plotly_chart(fig_formacion, use_container_width=True)
    with c2:
        if 'Experiencia' in df.columns:
            fig_exp = px.histogram(df, y='Experiencia', title='Años de Experiencia Laboral', color='Experiencia')
            st.plotly_chart(fig_exp, use_container_width=True)

# --- PESTAÑA 2: MODELO DE CORRELACIÓN ---
with tab2:
    st.header("Análisis de Relaciones: Habilidad vs. Intereses")
    st.markdown("""
    **Hipótesis del Modelo:** ¿Los estudiantes con mayor habilidad previa en Python (Score Técnico) 
    tienden a priorizar temas más avanzados de automatización (Ranking cercano a 1)?
    """)
    
    if 'Score_Python_Total' in df.columns and 'Ranking_Automatizacion' in df.columns:
        colA, colB = st.columns([2, 1])
        
        with colA:
            fig_scatter = px.scatter(
                df, x='Score_Python_Total', y='Ranking_Automatizacion', 
                trendline="ols", 
                title="Regresión: Habilidad en Python vs. Interés en Automatización",
                labels={
                    "Score_Python_Total": "Score Técnico en Python (2 a 10)",
                    "Ranking_Automatizacion": "Prioridad de Automatización (1=Alto, 7=Bajo)"
                },
                hover_data=['Nombre'] if 'Nombre' in df.columns else []
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        with colB:
            st.subheader("Matriz de Correlación")
            num_cols = ['Score_Python_Total', 'Ranking_Automatizacion', 'Ranking_RiesgoCredito']
            # Filtrar solo las que existen
            num_cols = [c for c in num_cols if c in df.columns]
            
            if len(num_cols) > 1:
                corr_matrix = df[num_cols].corr()
                fig_corr, ax = plt.subplots(figsize=(5, 4))
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, ax=ax, fmt=".2f")
                st.pyplot(fig_corr)
            
        st.info("💡 **Interpretación del Modelo:** Si la línea de tendencia desciende (correlación negativa), significa que los alumnos con más bases de programación están exigiendo que el curso se enfoque fuertemente en automatizar reportes.")

# --- PESTAÑA 3: EXPECTATIVAS (NLP VISUAL) ---
with tab3:
    st.header("¿Qué esperan lograr los estudiantes al terminar?")
    
    if 'Expectativas' in df.columns:
        # Generar Nube de Palabras
        textos_validos = df['Expectativas'].dropna().astype(str).tolist()
        text = " ".join(textos_validos)
        
        stopwords = set(['para', 'en', 'el', 'la', 'los', 'las', 'un', 'una', 'con', 'de', 'del', 'al', 'que', 'hoy', 'pueda', 'poder', 'ser', 'a', 'y', 'o'])
        
        if text.strip():
            wordcloud = WordCloud(width=800, height=400, background_color='white', 
                                  stopwords=stopwords, colormap='viridis').generate(text)
            
            st.subheader("Conceptos Clave Demandados")
            fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
            ax_wc.imshow(wordcloud, interpolation='bilinear')
            ax_wc.axis("off")
            st.pyplot(fig_wc)
        
        st.markdown("---")
        st.subheader("Muro de Expectativas Individuales")
        
        for index, row in df.iterrows():
            nombre = row['Nombre'] if 'Nombre' in row and pd.notna(row['Nombre']) else f"Estudiante {index+1}"
            formacion = row['Formacion'] if 'Formacion' in row else "N/A"
            exp = row['Experiencia'] if 'Experiencia' in row else "N/A"
            
            with st.expander(f"👤 {nombre} ({formacion} - {exp})"):
                st.markdown("**Expectativa:**")
                st.info(f"*{row['Expectativas']}*")
                
                if 'Uso_Cuantitativo' in row:
                    st.markdown(f"- **Uso de Herramientas Cuantitativas:** {row['Uso_Cuantitativo']}")
                if 'Interes_IA' in row:
                    st.markdown(f"- **Interés en IA:** {row['Interes_IA']}")