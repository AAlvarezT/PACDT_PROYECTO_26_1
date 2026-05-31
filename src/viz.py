"""
viz.py
Funciones de visualización para el dashboard RENIPED.
Todas las funciones que retornan figuras Plotly aceptan el DataFrame
ya filtrado desde app.py.
"""

import matplotlib
matplotlib.use("Agg")  # backend sin pantalla para Streamlit

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud

# Paleta consistente en todos los gráficos
COLOR_APARECIDO = {True: "#2E7D32", False: "#C62828"}
LABEL_APARECIDO = {True: "Apareció", False: "No apareció"}

STOPWORDS_ES = {
    "de", "la", "el", "en", "y", "a", "con", "sin", "del",
    "los", "las", "se", "por", "que", "su", "un", "una", "al",
    "lo", "le", "les", "no", "es", "era", "fue", "han", "hay",
    "para", "como", "pero", "más", "sobre", "entre", "hasta",
    "desde", "cuando", "donde", "quien", "cuya", "cuyo", "xxxxx",
}


# ---------------------------------------------------------------------------
# G1 — Distribución de edad
# ---------------------------------------------------------------------------

def plot_age_dist(df: pd.DataFrame) -> go.Figure:
    """Histograma de EDAD coloreado por estado de aparición."""
    df_plot = df.copy()
    df_plot["Estado"] = df_plot["Aparecido"].map(LABEL_APARECIDO)

    fig = px.histogram(
        df_plot,
        x="EDAD",
        color="Estado",
        color_discrete_map={"Apareció": "#2E7D32", "No apareció": "#C62828"},
        barmode="overlay",
        opacity=0.75,
        nbins=30,
        labels={"EDAD": "Edad (años)", "count": "Cantidad"},
        title="Distribución de edad",
    )
    fig.update_layout(
        legend_title_text="Estado",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_size=13,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#e5e5e5")
    return fig


# ---------------------------------------------------------------------------
# G2 — Serie temporal
# ---------------------------------------------------------------------------

def plot_time_series(df: pd.DataFrame) -> go.Figure:
    """Casos registrados por mes según Fecha Hecho."""
    ts = df.dropna(subset=["mes_hecho"]).copy()
    if ts.empty:
        return go.Figure().update_layout(title="Sin datos para la serie temporal")

    ts_grouped = ts.groupby("mes_hecho").size().reset_index(name="casos")

    fig = px.line(
        ts_grouped,
        x="mes_hecho",
        y="casos",
        markers=True,
        labels={"mes_hecho": "Mes", "casos": "Casos registrados"},
        title="Casos registrados por mes",
    )
    fig.update_traces(line_color="#1565C0", marker_color="#1565C0", marker_size=5)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_size=13,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#e5e5e5")
    return fig


# ---------------------------------------------------------------------------
# G3a — Donut estado de aparición
# ---------------------------------------------------------------------------

def plot_aparecido_donut(df: pd.DataFrame) -> go.Figure:
    """Donut: proporción de aparecidos vs no aparecidos."""
    counts = df["Aparecido"].value_counts().reset_index()
    counts.columns = ["Aparecido", "n"]
    counts["label"] = counts["Aparecido"].map(LABEL_APARECIDO)

    fig = px.pie(
        counts,
        values="n",
        names="label",
        color="label",
        color_discrete_map={"Apareció": "#2E7D32", "No apareció": "#C62828"},
        hole=0.5,
        title="Estado de aparición",
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        font_size=13,
    )
    return fig


# ---------------------------------------------------------------------------
# G3b — Box horas para aparecer
# ---------------------------------------------------------------------------

def plot_hours_box(df: pd.DataFrame) -> go.Figure:
    """Box plot de horas hasta aparecer (solo casos resueltos)."""
    data = df[df["Aparecido"] & df["Horas para Aparecer"].notna()]

    if data.empty:
        return go.Figure().update_layout(title="Sin datos de horas para aparecer")

    fig = px.box(
        data,
        y="Horas para Aparecer",
        points="outliers",
        labels={"Horas para Aparecer": "Horas"},
        title="Horas hasta aparecer (casos resueltos)",
        color_discrete_sequence=["#2E7D32"],
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_size=13,
    )
    fig.update_yaxes(gridcolor="#e5e5e5")
    return fig


# ---------------------------------------------------------------------------
# G4 — Top N regiones
# ---------------------------------------------------------------------------

def plot_top_regions(df: pd.DataFrame, n: int = 10) -> go.Figure:
    """Barras horizontales con los N departamentos de mayor frecuencia."""
    top = df["region"].value_counts().head(n).reset_index()
    top.columns = ["region", "casos"]
    top = top.sort_values("casos", ascending=True)

    fig = px.bar(
        top,
        x="casos",
        y="region",
        orientation="h",
        color="casos",
        color_continuous_scale="Blues",
        labels={"region": "Departamento", "casos": "Casos"},
        title=f"Top {n} departamentos con más casos",
    )
    fig.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_size=13,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    return fig


# ---------------------------------------------------------------------------
# G5 — Mapa
# ---------------------------------------------------------------------------

def plot_map(df: pd.DataFrame) -> go.Figure:
    """Scatter mapbox de casos con coordenadas válidas."""
    geo = df.dropna(subset=["Latitud", "Longitud"]).copy()
    geo["Estado"] = geo["Aparecido"].map(LABEL_APARECIDO)
    geo["_edad_str"] = geo["EDAD"].astype(int).astype(str) + " años"

    if geo.empty:
        return go.Figure().update_layout(title="Sin coordenadas disponibles")

    fig = px.scatter_mapbox(
        geo,
        lat="Latitud",
        lon="Longitud",
        color="Estado",
        color_discrete_map={"Apareció": "#2E7D32", "No apareció": "#C62828"},
        hover_name="Nombres",
        hover_data={"_edad_str": True, "region": True, "Latitud": False, "Longitud": False, "Estado": False},
        labels={"_edad_str": "Edad", "region": "Región"},
        zoom=4,
        center={"lat": -9.5, "lon": -75.5},
        mapbox_style="carto-positron",
        opacity=0.75,
        title="Distribución geográfica de casos",
    )
    fig.update_layout(
        legend_title_text="Estado",
        paper_bgcolor="rgba(0,0,0,0)",
        font_size=13,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
    )
    return fig


# ---------------------------------------------------------------------------
# G6 — Nube de palabras
# ---------------------------------------------------------------------------

def plot_wordcloud(df: pd.DataFrame, col: str) -> plt.Figure | None:
    """
    Nube de palabras sobre una columna de texto libre.
    Retorna None si no hay texto suficiente.
    """
    text = " ".join(df[col].dropna().astype(str).tolist()).strip()
    if len(text) < 20:
        return None

    wc = WordCloud(
        width=1000,
        height=450,
        background_color=None,
        mode="RGBA",
        colormap="viridis",
        max_words=120,
        stopwords=STOPWORDS_ES,
        collocations=False,
        min_font_size=10,
    ).generate(text)

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_alpha(0)
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    plt.tight_layout(pad=0)
    return fig
