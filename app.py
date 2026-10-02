import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ir primero)
st.set_page_config(page_title="Dashboard Analítico", layout="wide", initial_sidebar_state="collapsed")

# CSS personalizado para ajustar los márgenes y dar un aspecto más compacto tipo dashboard
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    h1, h2, h3 { color: #f0f2f6; }
    .st-emotion-cache-1wivap2 { font-size: 0.8rem; color: #a5a5ae; }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA Y LIMPIEZA DE DATOS
@st.cache_data
def load_data():
    df = pd.read_excel("datos.xlsx", skiprows=1)
    
    # ELIMINAR NOMBRES Y DATOS PERSONALES PARA ANONIMATO
    cols_to_drop = ["Nombre completo", "Correo electrónico del destinatario", "Apellido del destinatario", "Nombre del destinatario", "Dirección IP", "Referencia a datos externos", "Latitud de la ubicación", "Longitud de la ubicación"]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
    
    # Mapeo de todas las columnas relevantes a nombres cortos manejables
    col_map = {
        "Área funcional": "Area",
        "Años de experiencia laboral": "Experiencia",
        "Formación cuantitativa previa": "Formacion",
        "¿Con qué frecuencia usas herramientas de análisis cuantitativo en tu trabajo?": "Frecuencia_Cuantitativo",
        "¿Tienes experiencia previa programando?": "Exp_Programacion",
        "Lenguajes / herramientas que has usado": "Herramientas",
        "Autoevaluación en Python — indica tu grado de acuerdo con cada afirmación - Puedo escribir un bucle for y una función": "Py_Bucle",
        "Autoevaluación en Python — indica tu grado de acuerdo con cada afirmación - He usado pandas para manipular datos": "Py_Pandas",
        "Autoevaluación en Python — indica tu grado de acuerdo con cada afirmación - He hecho gráficos con matplotlib / seaborn": "Py_Viz",
        "Autoevaluación en Python — indica tu grado de acuerdo con cada afirmación - He instalado librerías con pip / conda": "Py_Pip",
        "Autoevaluación en Python — indica tu grado de acuerdo con cada afirmación - He usado Jupyter Notebook o Google Colab": "Py_Jupyter",
        "¿Has tomado algún curso de Python antes?": "Curso_Previo",
        "Preferencia de entorno para las prácticas": "Entorno",
        "¿Tu entidad tiene restricciones de red o políticas que bloqueen el acceso a servicios en la nube como Colab?": "Restriccion_Red",
        "Nivel de inglés técnico de lectura": "Ingles",
        "¿Te sientes cómodo/a recibiendo material complementario en inglés (documentación, librerías, lecturas)?": "Ingles_Material",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Análisis y visualización de series financieras": "Rk_Series",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Gestión de riesgo de mercado (VaR, volatilidad)": "Rk_Mercado",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Riesgo de crédito y scoring": "Rk_Credito",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Portafolios y optimización": "Rk_Portafolio",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Valoración de instrumentos / renta fija": "Rk_Valoracion",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Automatización de reportes financieros": "Rk_Auto",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Análisis de datos macro-financieros": "Rk_Macro",
        "¿Te interesaría que el curso incluyera aplicaciones financieras apoyadas en IA / machine learning?": "Interes_IA",
        "Temas de IA de interés": "Temas_IA",
        "¿Has usado herramientas de IA generativa (ChatGPT, Claude, Copilot) para tareas de trabajo?": "Uso_IAGen",
        "¿Qué te gustaría poder hacer al terminar el curso que hoy no puedas?": "Expectativas"
    }
    df = df.rename(columns=lambda x: col_map.get(x, x))
    
    # Transformación a numérico para gráficas (1=Bajo, 5=Alto)
    likert_map = {"Totalmente en desacuerdo": 1, "En desacuerdo": 2, "Neutral": 3, "De acuerdo": 4, "Totalmente de acuerdo": 5}
    py_cols = ['Py_Bucle', 'Py_Pandas', 'Py_Viz', 'Py_Pip', 'Py_Jupyter']
    for c in py_cols:
        if c in df.columns:
            df[c+'_Num'] = df[c].map(likert_map).fillna(1)
            
    return df

df = load_data()

# 3. TEMA OSCURO PARA PLOTLY
template_dark = "plotly_dark"
color_palette = px.colors.qualitative.Pastel # Colores vibrantes en fondo oscuro

st.title("🌌 Análisis Consolidado de Audiencia")

# ================= FILA 1: KPIs SUPERIORES =================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("👥 Total Participantes", len(df))
    st.caption("Análisis: Muestra total de encuestados anónimos.")
with col2:
    exp_alta = len(df[df['Experiencia'].isin(['5 a 10', 'Más de 10'])]) if 'Experiencia' in df.columns else 0
    st.metric("💼 Seniority (5+ Años)", f"{(exp_alta/len(df)*100):.0f}%")
    st.caption("Análisis: Proporción de perfiles intermedios-senior.")
with col3:
    ia_alta = len(df[df['Interes_IA'] == 'Mucho']) if 'Interes_IA' in df.columns else 0
    st.metric("🤖 Alta Demanda IA", f"{(ia_alta/len(df)*100):.0f}%")
    st.caption("Análisis: Interés marcado en integrar Machine Learning.")
with col4:
    restriccion = len(df[df['Restriccion_Red'] == 'Sí']) if 'Restriccion_Red' in df.columns else 0
    st.metric("⚠️ Restricciones Red Nube", f"{(restriccion/len(df)*100):.0f}%")
    st.caption("Análisis: Alerta para configurar entornos de práctica (Colab).")

st.markdown("---")

# ================= FILA 2: DEMOGRAFÍA Y PERFIL (3 Columnas) =================
c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("Formación y Área")
    if 'Formacion' in df.columns:
        fig_form = px.pie(df, names='Formacion', hole=0.6, color_discrete_sequence=px.colors.sequential.Agsunset)
        fig_form.update_layout(template=template_dark, margin=dict(t=20, b=0, l=0, r=0), height=250, showlegend=True)
        st.plotly_chart(fig_form, use_container_width=True)
    st.caption("Dominio de ingenierías y economía en la muestra inicial.")

with c2:
    st.subheader("Experiencia Previa")
    if 'Experiencia' in df.columns:
        fig_exp = px.histogram(df, y='Experiencia', color_discrete_sequence=['#00d4ff'])
        fig_exp.update_layout(template=template_dark, margin=dict(t=20, b=0, l=0, r=0), height=250, yaxis_title="")
        st.plotly_chart(fig_exp, use_container_width=True)
    st.caption("Distribución homogénea entre perfiles junior y senior.")

with c3:
    st.subheader("Uso IA Generativa")
    if 'Uso_IAGen' in df.columns:
        fig_ia = px.pie(df, names='Uso_IAGen', hole=0.6, color_discrete_sequence=px.colors.sequential.Tealgrn)
        fig_ia.update_layout(template=template_dark, margin=dict(t=20, b=0, l=0, r=0), height=250)
        st.plotly_chart(fig_ia, use_container_width=True)
    st.caption("Nivel de adopción de herramientas como ChatGPT/Claude.")

st.markdown("---")

# ================= FILA 3: COMPETENCIAS TÉCNICAS (RADAR Y BARRAS) =================
c4, c5 = st.columns([1, 1.5])

with c4:
    st.subheader("Autoevaluación en Python (Promedio)")
    py_cols_num = ['Py_Bucle_Num', 'Py_Pandas_Num', 'Py_Viz_Num', 'Py_Pip_Num', 'Py_Jupyter_Num']
    if all(c in df.columns for c in py_cols_num):
        promedios = df[py_cols_num].mean().tolist()
        categorias = ['Bucles/Funciones', 'Pandas', 'Matplotlib/Seaborn', 'Pip/Conda', 'Jupyter/Colab']
        
        fig_radar = go.Figure(data=go.Scatterpolar(
          r=promedios + [promedios[0]], # Cerrar el polígono
          theta=categorias + [categorias[0]],
          fill='toself',
          line=dict(color='#ff00ff')
        ))
        fig_radar.update_layout(
          template=template_dark, height=300, margin=dict(t=20, b=20),
          polar=dict(radialaxis=dict(visible=True, range=[1, 5]))
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        st.caption("Radar de habilidades. 1 = Nulo, 5 = Avanzado.")

with c5:
    st.subheader("Herramientas Más Utilizadas")
    if 'Herramientas' in df.columns:
        # Extraer herramientas separadas por comas
        todas_herr = df['Herramientas'].dropna().str.split(',').explode().str.strip()
        conteo_herr = todas_herr.value_counts().reset_index()
        conteo_herr.columns = ['Herramienta', 'Cantidad']
        
        fig_herr = px.bar(conteo_herr, x='Cantidad', y='Herramienta', orientation='h', 
                          color='Cantidad', color_continuous_scale='Purp')
        fig_herr.update_layout(template=template_dark, margin=dict(t=0, b=0), height=300)
        st.plotly_chart(fig_herr, use_container_width=True)
        st.caption("Excel Avanzado/VBA domina el panorama actual frente a lenguajes modernos.")

st.markdown("---")

# ================= FILA 4: INTERESES Y LOGÍSTICA =================
c6, c7 = st.columns([1.5, 1])

with c6:
    st.subheader("Ranking de Intereses Temáticos (Prioridad Media)")
    # Calculamos el promedio de ranking (menor número = más interés)
    rk_cols = [c for c in df.columns if c.startswith('Rk_')]
    if rk_cols:
        # Convertir a numérico y llenar vacíos con 7
        df_rk = df[rk_cols].apply(pd.to_numeric, errors='coerce').fillna(7)
        promedios_rk = df_rk.mean().sort_values(ascending=True) # Menor es mejor
        
        nombres_amigables = [col.replace('Rk_', '') for col in promedios_rk.index]
        
        fig_rk = px.bar(x=promedios_rk.values, y=nombres_amigables, orientation='h',
                        color=promedios_rk.values, color_continuous_scale='Sunsetdark')
        fig_rk.update_layout(template=template_dark, xaxis_title="Prioridad Media (Más cerca a 1 es más deseado)", 
                             yaxis_title="Tema", height=300, margin=dict(t=20, b=20))
        st.plotly_chart(fig_rk, use_container_width=True)
        st.caption("Automatización y Riesgos suelen liderar. Barras más cortas indican mayor interés general.")

with c7:
    st.subheader("Logística e Inglés")
    colA, colB = st.columns(2)
    with colA:
        if 'Ingles' in df.columns:
            fig_ing = px.pie(df, names='Ingles', title='Nivel Inglés', hole=0.7, color_discrete_sequence=['#4dff4d', '#009900', '#003300'])
            fig_ing.update_layout(template=template_dark, margin=dict(t=30, b=0, l=0, r=0), height=200, showlegend=False)
            st.plotly_chart(fig_ing, use_container_width=True)
    with colB:
        if 'Entorno' in df.columns:
            # Acortar texto
            df['Entorno_Corto'] = df['Entorno'].str.split('(').str[0]
            fig_ent = px.pie(df, names='Entorno_Corto', title='Pref. Entorno', hole=0.7, color_discrete_sequence=['#ff4d4d', '#cc0000'])
            fig_ent.update_layout(template=template_dark, margin=dict(t=30, b=0, l=0, r=0), height=200, showlegend=False)
            st.plotly_chart(fig_ent, use_container_width=True)
    st.caption("Análisis de barreras idiomáticas e infraestructura para los laboratorios.")

st.markdown("---")

# ================= FILA 5: ANÁLISIS NLP EXPECTATIVAS =================
st.subheader("Análisis de Expectativas Abiertas (NLP)")
if 'Expectativas' in df.columns:
    textos_validos = df['Expectativas'].dropna().astype(str).tolist()
    text = " ".join(textos_validos)
    
    stopwords = set(['para', 'en', 'el', 'la', 'los', 'las', 'un', 'una', 'con', 'de', 'del', 'al', 'que', 'hoy', 'pueda', 'poder', 'ser', 'a', 'y', 'o', 'las', 'los'])
    
    if text.strip():
        # Generar nube con fondo oscuro y colores acordes al tema
        wordcloud = WordCloud(width=1200, height=300, background_color='#0e1117', 
                              stopwords=stopwords, colormap='cool', max_words=100).generate(text)
        
        fig_wc, ax_wc = plt.subplots(figsize=(15, 3), facecolor='#0e1117')
        ax_wc.imshow(wordcloud, interpolation='bilinear')
        ax_wc.axis("off")
        st.pyplot(fig_wc)
        st.caption("Conceptos más repetidos: Palabras más grandes indican objetivos pedagógicos clave demandados por los estudiantes anónimos.")
