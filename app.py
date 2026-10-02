import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diagnóstico de Perfil, Competencias e Intereses", layout="wide", initial_sidebar_state="collapsed")

# Colores inspirados en el diseño de referencia
BG_COLOR = "#151622"
CARD_COLOR = "#1e1f30"
TEXT_COLOR = "#ffffff"

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
    color: #ffffff;
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

/* Estilo para las métricas KPI */
[data-testid="stMetricValue"] {{
    color: #00d4ff !important;
}}
</style>
""", unsafe_allow_html=True)

# 2. CARGA Y LIMPIEZA DE DATOS
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("datos.xlsx", skiprows=1)
    except FileNotFoundError:
        return pd.DataFrame()
        
    cols_to_drop = ["Nombre completo", "Correo electrónico del destinatario", "Apellido del destinatario", "Nombre del destinatario", "Dirección IP", "Referencia a datos externos", "Latitud de la ubicación", "Longitud de la ubicación"]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')

    # Nuevo mapeo incluyendo "Temas_IA"
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
        "Temas de IA de interés": "Temas_IA",  # Nueva columna mapeada
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

def apply_dark_layout(fig, height=220, bottom_margin=10):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff'),
        legend=dict(font=dict(color='#ffffff')),
        margin=dict(t=30, b=bottom_margin, l=10, r=10),
        height=height
    )
    fig.update_xaxes(tickfont=dict(color='#ffffff'), title_font=dict(color='#ffffff'))
    fig.update_yaxes(tickfont=dict(color='#ffffff'), title_font=dict(color='#ffffff'))
    return fig

st.title("Diagnóstico de Perfil, Competencias e Intereses del Curso")

# ================= FILA 0: INDICADORES RESUMEN =================
if not df.empty:
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    
    total_participantes = len(df)
    kpi1.metric("Total Participantes", total_participantes)
    
    if 'Experiencia' in df.columns:
        exp_5_plus = df['Experiencia'].astype(str).str.contains(r'5 a 10|Más de 10|5|6|7|8|9|10', case=False, na=False).sum()
        porcentaje_exp = int((exp_5_plus / total_participantes) * 100) if total_participantes > 0 else 0
        kpi2.metric("Con 5+ años exp.", f"{porcentaje_exp}%")
    
    if 'Curso_Previo' in df.columns:
        sin_python = df['Curso_Previo'].astype(str).str.strip().str.lower().eq('no').sum()
        kpi3.metric("Nunca han tomado Python", sin_python)
        
    if 'Exp_Programacion' in df.columns:
        # Se cuenta cualquiera que tenga experiencia Básica, Intermedia o Avanzada
        exp_prog = df['Exp_Programacion'].astype(str).str.contains('Básica|Intermedia|Avanzada', case=False, na=False).sum()
        kpi4.metric("Experiencia programando", exp_prog)
        
    if 'Interes_IA' in df.columns:
        # Se verifica la palabra "Mucho" que es la que viene en la encuesta real
        interes_ia = df['Interes_IA'].astype(str).str.contains('Mucho|Sí|Si', case=False, na=False).sum()
        kpi5.metric("Alto interés en IA/ML", f"{interes_ia} de {total_participantes}")

st.markdown("---")

# ================= FILA 1: DEMOGRAFÍA =================
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### Formación")
    if 'Formacion' in df.columns:
        fig_form = px.pie(df, names='Formacion', hole=0.6, color_discrete_sequence=px.colors.sequential.Agsunset)
        st.plotly_chart(apply_dark_layout(fig_form), use_container_width=True, theme=None)
        st.markdown("<div class='analysis-text'><b>Análisis:</b> Predominancia de perfiles técnicos/económicos, un punto de partida sólido para abordar conceptos de modelamiento complejo.</div>", unsafe_allow_html=True)

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
        st.markdown("<div class='analysis-text'><b>Análisis:</b> Alta familiaridad con herramientas como ChatGPT/Claude. Existe oportunidad para introducir prácticas modernas de código asistido.</div>", unsafe_allow_html=True)

st.markdown("---")

# ================= FILA 2: HABILIDADES Y LOGÍSTICA =================
c4, c5, c6 = st.columns([1.2, 1.5, 1])
with c4:
    # REGRESO AL GRÁFICO DE ARAÑA (RADAR)
    st.markdown("### Nivel Python (Radar)")
    py_cols_num = ['Py_Bucle_Num', 'Py_Pandas_Num', 'Py_Viz_Num', 'Py_Pip_Num', 'Py_Jupyter_Num']
    if all(c in df.columns for c in py_cols_num):
        promedios = df[py_cols_num].mean().tolist()
        categorias = ['Bucles', 'Pandas', 'Viz', 'Pip', 'Jupyter']
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=promedios + [promedios[0]], 
            theta=categorias + [categorias[0]], 
            fill='toself', 
            line=dict(color='#ff00ff')
        ))
        
        fig_radar.update_layout(
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, range=[1, 5], gridcolor='#444', tickfont=dict(color='#ffffff')),
                angularaxis=dict(tickfont=dict(color='#ffffff'))
            )
        )
        
        st.plotly_chart(apply_dark_layout(fig_radar, height=270, bottom_margin=40), use_container_width=True, theme=None)
        st.markdown("<div class='analysis-text'><b>Análisis:</b> En promedio, Jupyter es el entorno más familiar. El déficit más marcado está en la instalación de paquetes (Pip), lo que requerirá nivelación técnica temprana.</div>", unsafe_allow_html=True)

with c5:
    st.markdown("### Herramientas Actuales")
    if 'Herramientas' in df.columns:
        todas_herr = df['Herramientas'].dropna().str.split(',').explode().str.strip()
        conteo_herr = todas_herr.value_counts().reset_index()
        conteo_herr.columns = ['Herramienta', 'Cantidad']
        fig_herr = px.bar(conteo_herr, x='Cantidad', y='Herramienta', orientation='h', color='Cantidad', color_continuous_scale='Purp')
        st.plotly_chart(apply_dark_layout(fig_herr, height=270), use_container_width=True, theme=None)
        st.markdown("<div class='analysis-text'><b>Análisis:</b> Excel/VBA es la herramienta más extendida en el grupo. El enfoque debe ser enseñar Python como el 'siguiente paso evolutivo'.</div>", unsafe_allow_html=True)

with c6:
    st.markdown("### Logística (Inglés y Entorno)")
    if 'Ingles' in df.columns:
        fig_ing = px.pie(df, names='Ingles', title='Lectura Inglés', hole=0.7, color_discrete_sequence=['#4dff4d', '#009900'])
        st.plotly_chart(apply_dark_layout(fig_ing, height=135), use_container_width=True, theme=None)
    if 'Entorno' in df.columns:
        df['Entorno_Corto'] = df['Entorno'].str.split('(').str[0]
        fig_ent = px.pie(df, names='Entorno_Corto', title='Entorno Práctica', hole=0.7, color_discrete_sequence=['#ff4d4d', '#cc0000'])
        st.plotly_chart(apply_dark_layout(fig_ent, height=135), use_container_width=True, theme=None)
    st.markdown("<div class='analysis-text'><b>Análisis:</b> Es explícito que hay participantes con inglés básico. Existen restricciones o incertidumbre sobre acceso a entornos locales y preferencia por la Nube.</div>", unsafe_allow_html=True)

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
        top3_counts = (df[rk_cols_all] <= 3).sum().sort_values(ascending=True)
        nombres_amigables = [col.replace('Rk_', '') for col in top3_counts.index]
        
        fig_rk = px.bar(x=top3_counts.values, y=nombres_amigables, orientation='h', color=top3_counts.values, color_continuous_scale='Sunsetdark')
        fig_rk.update_layout(xaxis_title="Participantes que lo pusieron en su Top 3", yaxis_title="")
        st.plotly_chart(apply_dark_layout(fig_rk, height=280), use_container_width=True, theme=None)
        st.markdown("<div class='analysis-text'><b>Análisis:</b> Automatización y Riesgos lideran las selecciones del Top 3. Se sugiere estructurar proyectos sobre la sistematización de dichos modelos.</div>", unsafe_allow_html=True)

st.markdown("---")

# ================= FILA 4: EXPECTATIVAS Y FOCO EN IA =================
st.markdown("### Expectativas y Casos de Uso en Inteligencia Artificial")
# Se crean 3 columnas en lugar de 2 para acomodar la nueva gráfica de Temas de IA
col_nlp1, col_nlp2, col_nlp3 = st.columns([1.2, 1.2, 1])

if 'Expectativas' in df.columns:
    textos_validos = df['Expectativas'].dropna().astype(str).tolist()
    
    with col_nlp1:
        st.markdown("#### Categorías de Expectativas")
        text_lower = pd.Series(textos_validos).str.lower()
        
        c_riesgo = text_lower.str.contains(r'riesgo|risk|var|volatilidad|crédito|precios').sum()
        c_auto = text_lower.str.contains(r'automat|sistemati|reporte|optimiza|agili').sum()
        c_pred = text_lower.str.contains(r'predi|model|machine learning|ia|pronóstic|analitica|proyectar').sum()
        
        df_cats = pd.DataFrame({
            'Categoría': ['Riesgo / Precios', 'Automatización', 'Predicción / IA'],
            'Menciones': [c_riesgo, c_auto, c_pred]
        })
        
        fig_cats = px.bar(df_cats.sort_values('Menciones', ascending=True), 
                          x='Menciones', y='Categoría', orientation='h', 
                          color='Categoría', color_discrete_sequence=['#00ffff', '#ff00ff', '#00d4ff'])
        fig_cats.update_layout(showlegend=False)
        st.plotly_chart(apply_dark_layout(fig_cats, height=300), use_container_width=True, theme=None)
        st.markdown("<div class='analysis-text'>Las expectativas pivotan fuertemente hacia la reducción de carga operativa y el modelamiento proyectivo.</div>", unsafe_allow_html=True)

with col_nlp2:
    st.markdown("#### Temas Específicos de IA (Interés)")
    if 'Temas_IA' in df.columns:
        # Extrae y cuenta los temas específicos de IA solicitados por el 100% de la clase
        todas_ia = df['Temas_IA'].dropna().str.split(',').explode().str.strip()
        conteo_ia = todas_ia.value_counts().reset_index()
        conteo_ia.columns = ['Tema de IA', 'Votos']
        
        fig_ia_temas = px.bar(conteo_ia.sort_values('Votos', ascending=True), 
                              x='Votos', y='Tema de IA', orientation='h', 
                              color='Votos', color_continuous_scale='Teal')
        st.plotly_chart(apply_dark_layout(fig_ia_temas, height=300), use_container_width=True, theme=None)
        st.markdown("<div class='analysis-text'><b>Correlación:</b> Desglose del KPI '6 de 6'. Muestra qué casos de uso específicos de IA justifican el alto interés general.</div>", unsafe_allow_html=True)

with col_nlp3:
    st.markdown("#### Muro de Citas")
    if 'Expectativas' in df.columns:
        st.markdown("<div style='height: 330px; overflow-y: auto; padding-right: 10px;'>", unsafe_allow_html=True)
        for texto in textos_validos:
            if texto.strip():  # Evitar imprimir textos vacíos
                st.markdown(f"<div class='quote-card'>❝ {texto} ❞</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
