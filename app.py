import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Dashboard Analítico", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    h1, h2, h3 { color: #f0f2f6; }
    .st-emotion-cache-1wivap2 { font-size: 0.8rem; color: #a5a5ae; }
    .quote-card {
        background-color: #1e1e27;
        border-left: 4px solid #00d4ff;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
        font-style: italic;
        color: #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA Y LIMPIEZA DE DATOS
@st.cache_data
def load_data():
    df = pd.read_excel("datos.xlsx", skiprows=1)
    
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
template_dark = "plotly_dark"

st.title("🌌 Análisis Consolidado de Audiencia")

# ================= ANÁLISIS GENERAL Y KPIs =================
st.info("💡 **Análisis General del Grupo:** El cohort presenta una fuerte inclinación hacia la analítica aplicada. Con una experiencia sólida en sus áreas, buscan trascender el uso de herramientas tradicionales (Excel) hacia soluciones automatizadas y modelos predictivos (Machine Learning). El desafío pedagógico será nivelar las bases de programación en un grupo con alta expectativa técnica.")

col1, col2 = st.columns(2)
with col1:
    exp_alta = len(df[df['Experiencia'].isin(['5 a 10', 'Más de 10'])]) if 'Experiencia' in df.columns else 0
    st.metric("💼 Seniority (5+ Años)", f"{(exp_alta/max(len(df),1)*100):.0f}%")
    st.caption("Proporción de perfiles intermedios-senior.")
with col2:
    ia_alta = len(df[df['Interes_IA'] == 'Mucho']) if 'Interes_IA' in df.columns else 0
    st.metric("🤖 Alta Demanda IA", f"{(ia_alta/max(len(df),1)*100):.0f}%")
    st.caption("Interés marcado en integrar Machine Learning.")

st.markdown("---")

# ================= FILA 1: DEMOGRAFÍA =================
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("Formación")
    if 'Formacion' in df.columns:
        fig_form = px.pie(df, names='Formacion', hole=0.6, color_discrete_sequence=px.colors.sequential.Agsunset)
        fig_form.update_layout(template=template_dark, margin=dict(t=20, b=0, l=0, r=0), height=220)
        st.plotly_chart(fig_form, use_container_width=True)

with c2:
    st.subheader("Experiencia Previa")
    if 'Experiencia' in df.columns:
        fig_exp = px.histogram(df, y='Experiencia', color_discrete_sequence=['#00d4ff'])
        fig_exp.update_layout(template=template_dark, margin=dict(t=20, b=0, l=0, r=0), height=220, yaxis_title="")
        st.plotly_chart(fig_exp, use_container_width=True)

with c3:
    st.subheader("Uso IA Generativa")
    if 'Uso_IAGen' in df.columns:
        fig_ia = px.pie(df, names='Uso_IAGen', hole=0.6, color_discrete_sequence=px.colors.sequential.Tealgrn)
        fig_ia.update_layout(template=template_dark, margin=dict(t=20, b=0, l=0, r=0), height=220)
        st.plotly_chart(fig_ia, use_container_width=True)

st.markdown("---")

# ================= FILA 2: HABILIDADES Y LOGÍSTICA =================
c4, c5, c6 = st.columns([1.2, 1.5, 1])
with c4:
    st.subheader("Radar de Python")
    py_cols_num = ['Py_Bucle_Num', 'Py_Pandas_Num', 'Py_Viz_Num', 'Py_Pip_Num', 'Py_Jupyter_Num']
    if all(c in df.columns for c in py_cols_num):
        promedios = df[py_cols_num].mean().tolist()
        categorias = ['Bucles', 'Pandas', 'Viz', 'Pip', 'Jupyter']
        fig_radar = go.Figure(data=go.Scatterpolar(r=promedios + [promedios[0]], theta=categorias + [categorias[0]], fill='toself', line=dict(color='#ff00ff')))
        fig_radar.update_layout(template=template_dark, height=250, margin=dict(t=20, b=20), polar=dict(radialaxis=dict(visible=True, range=[1, 5])))
        st.plotly_chart(fig_radar, use_container_width=True)

with c5:
    st.subheader("Herramientas Actuales")
    if 'Herramientas' in df.columns:
        todas_herr = df['Herramientas'].dropna().str.split(',').explode().str.strip()
        conteo_herr = todas_herr.value_counts().reset_index()
        conteo_herr.columns = ['Herramienta', 'Cantidad']
        fig_herr = px.bar(conteo_herr, x='Cantidad', y='Herramienta', orientation='h', color='Cantidad', color_continuous_scale='Purp')
        fig_herr.update_layout(template=template_dark, margin=dict(t=0, b=0), height=250)
        st.plotly_chart(fig_herr, use_container_width=True)

with c6:
    st.subheader("Logística")
    if 'Ingles' in df.columns:
        fig_ing = px.pie(df, names='Ingles', title='Lectura Inglés', hole=0.7, color_discrete_sequence=['#4dff4d', '#009900'])
        fig_ing.update_layout(template=template_dark, margin=dict(t=30, b=0, l=0, r=0), height=125, showlegend=False)
        st.plotly_chart(fig_ing, use_container_width=True)
    if 'Entorno' in df.columns:
        df['Entorno_Corto'] = df['Entorno'].str.split('(').str[0]
        fig_ent = px.pie(df, names='Entorno_Corto', title='Entorno Práctica', hole=0.7, color_discrete_sequence=['#ff4d4d', '#cc0000'])
        fig_ent.update_layout(template=template_dark, margin=dict(t=30, b=0, l=0, r=0), height=125, showlegend=False)
        st.plotly_chart(fig_ent, use_container_width=True)

st.markdown("---")

# ================= FILA 3: CORRELACIONES E INTERESES =================
st.subheader("Análisis de Correlaciones y Demanda Temática")
st.caption("¿Existe relación entre el nivel técnico del estudiante y lo que desea aprender?")

colA, colB, colC = st.columns([1, 1, 1.2])

with colA:
    if 'Score_Python_Total' in df.columns and 'Rk_Auto' in df.columns:
        fig_scatter = px.scatter(df, x='Score_Python_Total', y='Rk_Auto', trendline="ols", 
                                 color_discrete_sequence=['#00ffff'])
        fig_scatter.update_layout(template=template_dark, height=280, margin=dict(t=10, b=10),
                                  xaxis_title="Score Python (Alto=Mejor)", yaxis_title="Interés Automatización (1=Alto)")
        st.plotly_chart(fig_scatter, use_container_width=True)

with colB:
    rk_cols = ['Rk_Auto', 'Rk_Credito', 'Rk_Mercado']
    rk_cols = [c for c in rk_cols if c in df.columns]
    if rk_cols and 'Score_Python_Total' in df.columns:
        cols_corr = ['Score_Python_Total'] + rk_cols
        corr_matrix = df[cols_corr].corr().round(2)
        fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r', aspect="auto")
        fig_corr.update_layout(template=template_dark, height=280, margin=dict(t=10, b=10))
        st.plotly_chart(fig_corr, use_container_width=True)

with colC:
    rk_cols_all = [c for c in df.columns if c.startswith('Rk_')]
    if rk_cols_all:
        promedios_rk = df[rk_cols_all].mean().sort_values(ascending=True)
        nombres_amigables = [col.replace('Rk_', '') for col in promedios_rk.index]
        fig_rk = px.bar(x=promedios_rk.values, y=nombres_amigables, orientation='h', color=promedios_rk.values, color_continuous_scale='Sunsetdark')
        fig_rk.update_layout(template=template_dark, xaxis_title="Prioridad Media (Cerca a 1 = Mejor)", yaxis_title="", height=280, margin=dict(t=10, b=10))
        st.plotly_chart(fig_rk, use_container_width=True)

st.markdown("---")

# ================= FILA 4: EXPECTATIVAS (NUBE + MURO DE CITAS) =================
st.subheader("Expectativas del Curso")

col_nlp1, col_nlp2 = st.columns([1.5, 1])

if 'Expectativas' in df.columns:
    textos_validos = df['Expectativas'].dropna().astype(str).tolist()
    
    with col_nlp1:
        text = " ".join(textos_validos)
        stopwords = set(['para', 'en', 'el', 'la', 'los', 'las', 'un', 'una', 'con', 'de', 'del', 'al', 'que', 'hoy', 'pueda', 'poder', 'ser', 'a', 'y', 'o', 'las', 'los', 'poder', 'hacer'])
        if text.strip():
            wordcloud = WordCloud(width=800, height=400, background_color='#0e1117', stopwords=stopwords, colormap='cool', max_words=80).generate(text)
            fig_wc, ax_wc = plt.subplots(figsize=(10, 5), facecolor='#0e1117')
            ax_wc.imshow(wordcloud, interpolation='bilinear')
            ax_wc.axis("off")
            st.pyplot(fig_wc)
            st.caption("Conceptos más demandados en texto libre.")

    with col_nlp2:
        st.markdown("<div style='height: 400px; overflow-y: auto;'>", unsafe_allow_html=True)
        for texto in textos_validos:
            st.markdown(f"<div class='quote-card'>❝ {texto} ❞</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.caption("Muro de citas anónimas.")
