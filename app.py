import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diagnóstico de Perfil y Competencias", layout="wide", initial_sidebar_state="collapsed")

# Colores inspirados en el diseño de referencia
BG_COLOR = "#151622"  
CARD_COLOR = "#1e1f30" 
TEXT_COLOR = "#e0e0e0"

st.markdown(f"""
    <style>
    /* Fondo principal de la aplicación */
    .stApp {{
        background-color: {BG_COLOR};
    }}
    
    /* Cambiar el fondo de la barra superior de Streamlit */
    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    
    .block-container {{ padding-top: 2rem; padding-bottom: 0rem; }}
    h1, h2, h3, p, span {{ color: {TEXT_COLOR} !important; }}
    
    /* Estilos para el muro de citas */
    .quote-card {{
        background-color: {CARD_COLOR};
        border-left: 4px solid #00d4ff;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
        font-style: italic;
        color: #e0e0e0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    
    /* Estilo para los bloques de análisis */
    .analysis-text {{
        font-size: 0.85rem;
        color: #9fa8da;
        background-color: rgba(30, 31, 48, 0.5);
        padding: 8px;
        border-radius: 4px;
        margin-top: -10px;
        margin-bottom: 20px;
        border-left: 2px solid #ff00ff;
    }}
    </style>
""", unsafe_allow_html=True)

# 2. CARGA Y LIMPIEZA DE DATOS
@st.cache_data
def load_data():
    df = pd.read_excel("datos.xlsx", skiprows=1)
    
    # Anonimización
    cols_to_drop = ["Nombre completo", "Correo electrónico del destinatario", "Apellido del destinatario", "Nombre del destinatario", "Dirección IP", "Referencia a datos externos", "Latitud de la ubicación", "Longitud de la ubicación"]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
    
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
        "Nivel de inglés técnico de lectura": "Ingles",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Análisis y visualización de series financieras": "Rk_Series",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Gestión de riesgo de mercado (VaR, volatilidad)": "Rk_Mercado",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Riesgo de crédito y scoring": "Rk_Credito",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Portafolios y optimización": "Rk_Portafolio",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Automatización de reportes financieros": "Rk_Auto",
        "¿Te interesaría que el curso incluyera aplicaciones financieras apoyadas en IA / machine learning?": "Interes_IA",
        "¿Has usado herramientas de IA generativa (ChatGPT, Claude, Copilot) para tareas de trabajo?": "Uso_IAGen",
        "¿Qué te gustaría poder hacer al terminar el curso que hoy no puedas?": "Expectativas"
    }
    df = df.rename(columns=lambda x: col_map.get(x, x))
    
    likert_map = {"Totalmente en desacuerdo": 1, "En desacuerdo": 2, "Neutral": 3, "De acuerdo": 4, "Totalmente de acuerdo": 5}
    py_cols = ['Py_Bucle', 'Py_Pandas', 'Py_Viz', 'Py_Pip', 'Py_Jupyter']
    
    df['Score_Python_Total'] = 0
    for c in py_cols:
        if c in df.columns:
            df[c+'_Num'] = df[c].map(likert_map).fillna(1)
            df['Score_Python_Total'] += df[c+'_Num']
            
    rk_cols = [c for c in df.columns if c.startswith('Rk_')]
    for c in rk_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(7)
            
    return df

df = load_data()

# Función auxiliar para configurar layouts con etiquetas forzosamente claras
def apply_dark_layout(fig, height=220, bottom_margin=10):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=TEXT_COLOR),  # Color de texto global
        legend=dict(font=dict(color=TEXT_COLOR)),  # Asegurar color en leyenda
        xaxis=dict(tickfont=dict(color=TEXT_COLOR), titlefont=dict(color=TEXT_COLOR)), # Eje X
        yaxis=dict(tickfont=dict(color=TEXT_COLOR), titlefont=dict(color=TEXT_COLOR)), # Eje Y
        margin=dict(t=30, b=bottom_margin, l=10, r=10),
        height=height
    )
    return fig

st.title("Diagnóstico de Perfil y Competencias Técnicas")
st.markdown("---")

# ================= FILA 1: DEMOGRAFÍA =================
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### Formación")
    if 'Formacion' in df.columns:
        fig_form = px.pie(df, names='Formacion', hole=0.6, color_discrete_sequence=px.colors.sequential.Agsunset)
        # Importante: theme=None evita que Streamlit sobrescriba nuestros colores de texto
        st.plotly_chart(apply_dark_layout(fig_form), use_container_width=True, theme=None)
    st.markdown("<div class='analysis-text'><b>Análisis:</b> Predominancia de perfiles técnicos/económicos. Base matemática fuerte, ideal para absorber conceptos de modelamiento complejo.</div>", unsafe_allow_html=True)

with c2:
    st.markdown("### Experiencia Previa")
    if 'Experiencia' in df.columns:
        fig_exp = px.histogram(df, y='Experiencia', color_discrete_sequence=['#00d4ff'])
        st.plotly_chart(apply_dark_layout(fig_exp), use_container_width=True, theme=None)
    st.markdown("<div class='analysis-text'><b>Análisis:</b> Experiencia concentrada en bandas intermedias y senior. Los casos de negocio deben estar alineados con problemas corporativos reales.</div>", unsafe_allow_html=True)

with c3:
    st.markdown("### Uso IA Generativa")
    if 'Uso_IAGen' in df.columns:
        fig_ia = px.pie(df, names='Uso_IAGen', hole=0.6, color_discrete_sequence=px.colors.sequential.Tealgrn)
        st.plotly_chart(apply_dark_layout(fig_ia), use_container_width=True, theme=None)
    st.markdown("<div class='analysis-text'><b>Análisis:</b> Alta familiaridad con ChatGPT/Claude. Listos para usar LLMs como asistentes de programación (Copilots) durante el curso.</div>", unsafe_allow_html=True)

st.markdown("---")

# ================= FILA 2: HABILIDADES Y LOGÍSTICA =================
c4, c5, c6 = st.columns([1.2, 1.5, 1])
with c4:
    st.markdown("### Radar de Python")
    py_cols_num = ['Py_Bucle_Num', 'Py_Pandas_Num', 'Py_Viz_Num', 'Py_Pip_Num', 'Py_Jupyter_Num']
    if all(c in df.columns for c in py_cols_num):
        promedios = df[py_cols_num].mean().tolist()
        categorias = ['Bucles', 'Pandas', 'Viz', 'Pip', 'Jupyter']
        fig_radar = go.Figure(data=go.Scatterpolar(r=promedios + [promedios[0]], theta=categorias + [categorias[0]], fill='toself', line=dict(color='#ff00ff')))
        fig_radar.update_layout(
            template="plotly_dark", 
            polar=dict(
                bgcolor='rgba(0,0,0,0)', 
                radialaxis=dict(visible=True, range=[1, 5], gridcolor='#444', tickfont=dict(color=TEXT_COLOR)),
                angularaxis=dict(tickfont=dict(color=TEXT_COLOR))
            )
        )
        st.plotly_chart(apply_dark_layout(fig_radar, height=270, bottom_margin=40), use_container_width=True, theme=None)
    st.markdown("<div class='analysis-text'><b>Análisis:</b> Déficit marcado en instalación de entornos (Pip). Jupyter y Bucles muestran mejor puntaje, pero se requiere nivelación técnica temprana.</div>", unsafe_allow_html=True)

with c5:
    st.markdown("### Herramientas Actuales")
    if 'Herramientas' in df.columns:
        todas_herr = df['Herramientas'].dropna().str.split(',').explode().str.strip()
        conteo_herr = todas_herr.value_counts().reset_index()
        conteo_herr.columns = ['Herramienta', 'Cantidad']
        fig_herr = px.bar(conteo_herr, x='Cantidad', y='Herramienta', orientation='h', color='Cantidad', color_continuous_scale='Purp')
        st.plotly_chart(apply_dark_layout(fig_herr, height=270), use_container_width=True, theme=None)
    st.markdown("<div class='analysis-text'><b>Análisis:</b> Excel/VBA es la zona de confort absoluta. El enfoque debe ser enseñar Python como el 'siguiente paso evolutivo' de Excel.</div>", unsafe_allow_html=True)

with c6:
    st.markdown("### Logística (Inglés y Entorno)")
    if 'Ingles' in df.columns:
        fig_ing = px.pie(df, names='Ingles', title='Lectura Inglés', hole=0.7, color_discrete_sequence=['#4dff4d', '#009900'])
        st.plotly_chart(apply_dark_layout(fig_ing, height=135), use_container_width=True, theme=None)
    if 'Entorno' in df.columns:
        df['Entorno_Corto'] = df['Entorno'].str.split('(').str[0]
        fig_ent = px.pie(df, names='Entorno_Corto', title='Entorno Práctica', hole=0.7, color_discrete_sequence=['#ff4d4d', '#cc0000'])
        st.plotly_chart(apply_dark_layout(fig_ent, height=135), use_container_width=True, theme=None)
    st.markdown("<div class='analysis-text'><b>Análisis:</b> Sin barrera idiomática significativa. Fuerte preferencia y necesidad de trabajar en la Nube (Google Colab).</div>", unsafe_allow_html=True)

st.markdown("---")

# ================= FILA 3: CORRELACIONES E INTERESES =================
st.markdown("### Análisis de Correlaciones y Demanda Temática")

colA, colB, colC = st.columns([1, 1, 1.2])

with colA:
    if 'Score_Python_Total' in df.columns and 'Rk_Auto' in df.columns:
        fig_scatter = px.scatter(df, x='Score_Python_Total', y='Rk_Auto', trendline="ols", color_discrete_sequence=['#00ffff'])
        fig_scatter.update_layout(xaxis_title="Score Python (Alto=Mejor)", yaxis_title="Interés Automatización (1=Alto)")
        st.plotly_chart(apply_dark_layout(fig_scatter, height=280), use_container_width=True, theme=None)
    st.markdown("<div class='analysis-text'><b>Análisis:</b> Relación lineal (Scatter). Permite validar si quienes más saben programar son los que más piden temas automáticos.</div>", unsafe_allow_html=True)

with colB:
    rk_cols = ['Rk_Auto', 'Rk_Credito', 'Rk_Mercado']
    rk_cols = [c for c in rk_cols if c in df.columns]
    if rk_cols and 'Score_Python_Total' in df.columns:
        cols_corr = ['Score_Python_Total'] + rk_cols
        corr_matrix = df[cols_corr].corr().round(2)
        fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r', aspect="auto")
        st.plotly_chart(apply_dark_layout(fig_corr, height=280), use_container_width=True, theme=None)
    st.markdown("<div class='analysis-text'><b>Análisis:</b> Mapa de calor. Colores extremos indican variables que se mueven juntas. Útil para empaquetar módulos del temario.</div>", unsafe_allow_html=True)

with colC:
    rk_cols_all = [c for c in df.columns if c.startswith('Rk_')]
    if rk_cols_all:
        promedios_rk = df[rk_cols_all].mean().sort_values(ascending=True)
        nombres_amigables = [col.replace('Rk_', '') for col in promedios_rk.index]
        fig_rk = px.bar(x=promedios_rk.values, y=nombres_amigables, orientation='h', color=promedios_rk.values, color_continuous_scale='Sunsetdark')
        fig_rk.update_layout(xaxis_title="Prioridad Media (Cerca a 1 = Mejor)", yaxis_title="")
        st.plotly_chart(apply_dark_layout(fig_rk, height=280), use_container_width=True, theme=None)
    st.markdown("<div class='analysis-text'><b>Análisis:</b> Automatización y Riesgos lideran. Se sugiere estructurar el proyecto final alrededor de la sistematización de modelos de riesgo.</div>", unsafe_allow_html=True)

st.markdown("---")

# ================= FILA 4: EXPECTATIVAS (NUBE + MURO DE CITAS) =================
st.markdown("### Expectativas del Curso (Text Mining)")

col_nlp1, col_nlp2 = st.columns([1.5, 1])

if 'Expectativas' in df.columns:
    textos_validos = df['Expectativas'].dropna().astype(str).tolist()
    
    with col_nlp1:
        text = " ".join(textos_validos)
        stopwords = set(['para', 'en', 'el', 'la', 'los', 'las', 'un', 'una', 'con', 'de', 'del', 'al', 'que', 'hoy', 'pueda', 'poder', 'ser', 'a', 'y', 'o', 'las', 'los', 'poder', 'hacer'])
        if text.strip():
            wordcloud = WordCloud(width=800, height=400, background_color=BG_COLOR, stopwords=stopwords, colormap='cool', max_words=80).generate(text)
            fig_wc, ax_wc = plt.subplots(figsize=(10, 5), facecolor=BG_COLOR)
            ax_wc.imshow(wordcloud, interpolation='bilinear')
            ax_wc.axis("off")
            st.pyplot(fig_wc)
        st.markdown("<div class='analysis-text'><b>Análisis Lexicométrico:</b> Verbos y sustantivos principales evidencian una meta clara hacia la operatividad técnica aplicada.</div>", unsafe_allow_html=True)

    with col_nlp2:
        st.markdown("<div style='height: 380px; overflow-y: auto; padding-right: 10px;'>", unsafe_allow_html=True)
        for texto in textos_validos:
            st.markdown(f"<div class='quote-card'>❝ {texto} ❞</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='analysis-text' style='margin-top: 5px;'><b>Análisis Cualitativo:</b> Muro de expectativas literales. Clave leerlo antes del diseño final del syllabus.</div>", unsafe_allow_html=True)
