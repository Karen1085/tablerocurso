from pathlib import Path

code = r'''import html
import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Diagnóstico de Perfil y Competencias",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Paleta
BG_COLOR = "#151622"
CARD_COLOR = "#1e1f30"
TEXT_COLOR = "#e0e0e0"
MUTED_COLOR = "#9fa8da"
ACCENT = "#ff00ff"
CYAN = "#00d4ff"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BG_COLOR};
    }}

    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 1rem;
    }}

    h1, h2, h3, p, span {{
        color: {TEXT_COLOR} !important;
    }}

    .kpi-card {{
        background: linear-gradient(145deg, rgba(30,31,48,0.96), rgba(23,24,37,0.96));
        border: 1px solid rgba(255,255,255,0.07);
        border-top: 3px solid {ACCENT};
        border-radius: 10px;
        padding: 14px 16px;
        min-height: 112px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.22);
    }}

    .kpi-value {{
        font-size: 1.85rem;
        line-height: 1.05;
        font-weight: 750;
        color: #ffffff;
        margin-bottom: 7px;
    }}

    .kpi-label {{
        font-size: 0.80rem;
        color: {MUTED_COLOR};
        line-height: 1.25;
    }}

    .analysis-text {{
        font-size: 0.84rem;
        color: {MUTED_COLOR};
        background-color: rgba(30,31,48,0.60);
        padding: 9px 10px;
        border-radius: 5px;
        margin-top: -8px;
        margin-bottom: 18px;
        border-left: 2px solid {ACCENT};
        line-height: 1.4;
    }}

    .quote-card {{
        background-color: {CARD_COLOR};
        border-left: 4px solid {CYAN};
        padding: 13px 14px;
        border-radius: 6px;
        margin-bottom: 10px;
        font-style: italic;
        color: {TEXT_COLOR};
        box-shadow: 0 4px 6px rgba(0,0,0,0.25);
        line-height: 1.45;
    }}

    .theme-card {{
        background-color: {CARD_COLOR};
        border: 1px solid rgba(255,255,255,0.07);
        border-left: 4px solid {ACCENT};
        padding: 13px 14px;
        border-radius: 7px;
        margin-bottom: 10px;
    }}

    .theme-title {{
        font-size: 0.95rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 3px;
    }}

    .theme-desc {{
        font-size: 0.82rem;
        color: {MUTED_COLOR};
        line-height: 1.35;
    }}

    .recommendation-box {{
        background: linear-gradient(145deg, rgba(30,31,48,0.94), rgba(25,26,40,0.94));
        border: 1px solid rgba(255,255,255,0.08);
        border-left: 5px solid {CYAN};
        border-radius: 9px;
        padding: 16px 18px;
        margin-top: 8px;
        margin-bottom: 18px;
    }}

    .small-note {{
        color: {MUTED_COLOR};
        font-size: 0.78rem;
        margin-top: -8px;
        margin-bottom: 8px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 2. CARGA Y LIMPIEZA DE DATOS
# =========================================================
@st.cache_data
def load_data():
    df = pd.read_excel("datos.xlsx", skiprows=1)

    # Limpieza mínima de encabezados
    df.columns = df.columns.astype(str).str.strip()

    # Anonimización: se eliminan variables personales y de geolocalización
    cols_to_drop = [
        "Nombre completo",
        "Correo electrónico del destinatario",
        "Apellido del destinatario",
        "Nombre del destinatario",
        "Dirección IP",
        "Referencia a datos externos",
        "Latitud de la ubicación",
        "Longitud de la ubicación",
        "ID de respuesta"
    ]
    df = df.drop(
        columns=[c for c in cols_to_drop if c in df.columns],
        errors="ignore"
    )

    # Renombrado de variables principales
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
        "¿Tu entidad tiene restricciones de red o políticas que bloqueen el acceso a servicios en la nube como Colab?": "Restriccion_Nube",
        "Nivel de inglés técnico de lectura": "Ingles",
        "¿Te sientes cómodo/a recibiendo material complementario en inglés (documentación, librerías, lecturas)?": "Material_Ingles",

        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Análisis y visualización de series financieras": "Rk_Series",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Gestión de riesgo de mercado (VaR, volatilidad)": "Rk_Mercado",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Riesgo de crédito y scoring": "Rk_Credito",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Portafolios y optimización": "Rk_Portafolio",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Valoración de instrumentos / renta fija": "Rk_RentaFija",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Automatización de reportes financieros": "Rk_Auto",
        "De los siguientes temas de aplicación, selecciona y ordena tus 3 favoritos (1 = mayor interés) - Análisis de datos macro-financieros": "Rk_Macro",

        "¿Te interesaría que el curso incluyera aplicaciones financieras apoyadas en IA / machine learning?": "Interes_IA",
        "Temas de IA de interés": "Tema_IA",
        "¿Has usado herramientas de IA generativa (ChatGPT, Claude, Copilot) para tareas de trabajo?": "Uso_IAGen",
        "¿Qué te gustaría poder hacer al terminar el curso que hoy no puedas?": "Expectativas"
    }

    df = df.rename(columns=lambda x: col_map.get(x, x))

    # ---- Python: Likert 1-5
    likert_map = {
        "Totalmente en desacuerdo": 1,
        "En desacuerdo": 2,
        "Neutral": 3,
        "De acuerdo": 4,
        "Totalmente de acuerdo": 5
    }

    py_cols = ["Py_Bucle", "Py_Pandas", "Py_Viz", "Py_Pip", "Py_Jupyter"]
    py_num_cols = []

    for c in py_cols:
        if c in df.columns:
            num_col = f"{c}_Num"
            # Se conserva NaN si no hubo respuesta; no se imputa automáticamente como 1
            df[num_col] = df[c].map(likert_map)
            py_num_cols.append(num_col)

    if py_num_cols:
        df["Score_Python_Total"] = df[py_num_cols].sum(axis=1, min_count=1)

    # ---- Rankings: conservar NaN si faltó respuesta
    rk_cols = [c for c in df.columns if c.startswith("Rk_")]
    for c in rk_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # ID anónimo solo para visualización
    df["Participante"] = [f"P{i}" for i in range(1, len(df) + 1)]

    return df


df = load_data()
N = len(df)


# =========================================================
# 3. FUNCIONES AUXILIARES
# =========================================================
def apply_dark_layout(fig, height=240, bottom_margin=20, left_margin=20, right_margin=15):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR),
        legend=dict(font=dict(color=TEXT_COLOR)),
        xaxis=dict(
            tickfont=dict(color=TEXT_COLOR),
            titlefont=dict(color=TEXT_COLOR)
        ),
        yaxis=dict(
            tickfont=dict(color=TEXT_COLOR),
            titlefont=dict(color=TEXT_COLOR)
        ),
        margin=dict(t=35, b=bottom_margin, l=left_margin, r=right_margin),
        height=height
    )
    return fig


def kpi_card(value, label):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def count_contains(column, pattern):
    if column not in df.columns:
        return 0
    return int(
        df[column]
        .fillna("")
        .astype(str)
        .str.contains(pattern, case=False, regex=True)
        .sum()
    )


def clean_tool_counts(series):
    """
    Separa respuestas múltiples por coma.
    Si una persona marcó 'Ninguno' junto con una herramienta real,
    se descarta 'Ninguno' para esa persona.
    """
    tools = []

    for value in series.dropna():
        items = [x.strip() for x in str(value).split(",") if x.strip()]

        if len(items) > 1:
            items = [x for x in items if x.lower() != "ninguno"]

        tools.extend(items)

    if not tools:
        return pd.DataFrame(columns=["Herramienta", "Cantidad"])

    result = (
        pd.Series(tools)
        .value_counts()
        .rename_axis("Herramienta")
        .reset_index(name="Cantidad")
    )
    return result


# =========================================================
# 4. ENCABEZADO + KPIs
# =========================================================
st.title("Diagnóstico de Perfil y Competencias Técnicas")
st.markdown(
    "<div class='small-note'>Lectura descript
