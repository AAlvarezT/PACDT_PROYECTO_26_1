"""
viz.py
Funciones de visualización para el dashboard RENIPED.
Todas las funciones que retornan figuras Plotly aceptan el DataFrame
ya filtrado desde app.py.

Manejo de errores + decoradores (entrega final):
- Cada función está envuelta con @safe_plot (definido en utils.py), que
  captura cualquier excepción (columna faltante, datos vacíos tras
  filtrar, tipos inesperados) y devuelve una figura de respaldo con un
  mensaje visible, en vez de tumbar todo el dashboard con un traceback.
  Esto une el requisito de "decoradores útiles" con el de "manejo de
  errores robusto" en un solo mecanismo reutilizable.
"""

import matplotlib
matplotlib.use("Agg")  # backend sin pantalla para Streamlit

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud

from utils import STOPWORDS_ES, safe_plot

# Paleta consistente en todos los gráficos
COLOR_APARECIDO = {True: "#2E7D32", False: "#C62828"}
LABEL_APARECIDO = {True: "Apareció", False: "No apareció"}


# ---------------------------------------------------------------------------
# G1 — Distribución de edad
# ---------------------------------------------------------------------------

@safe_plot(fallback_title="No se pudo generar la distribución de edad")
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

@safe_plot(fallback_title="No se pudo generar la serie temporal")
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

@safe_plot(fallback_title="No se pudo generar el estado de aparición")
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

@safe_plot(fallback_title="No se pudo generar el box plot de horas")
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

@safe_plot(fallback_title="No se pudo generar el top de regiones")
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

@safe_plot(fallback_title="No se pudo generar el mapa")
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

@safe_plot(fallback_title="No se pudo generar la nube de palabras", as_none=True)
def plot_wordcloud(df: pd.DataFrame, col: str) -> plt.Figure | None:
    """
    Nube de palabras sobre una columna de texto libre.
    Retorna None si no hay texto suficiente (o si algo falla: app.py ya
    maneja el caso None mostrando un st.info).
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


# ---------------------------------------------------------------------------
# G7 — Análisis de sentimientos (sobre columna de texto + estado de aparición)
# ---------------------------------------------------------------------------

@safe_plot(fallback_title="No se pudo generar el análisis de sentimientos")
def plot_sentiment_dist(df: pd.DataFrame, label_col: str) -> go.Figure:
    """
    Barras agrupadas: distribución Positivo/Neutral/Negativo del tono
    del texto, comparada entre casos aparecidos y no aparecidos.
    """
    data = df.dropna(subset=[label_col]).copy()
    data["Estado"] = data["Aparecido"].map(LABEL_APARECIDO)

    order = ["Negativo", "Neutral", "Positivo"]
    counts = (
        data.groupby(["Estado", label_col]).size()
        .reindex(pd.MultiIndex.from_product([["Apareció", "No apareció"], order]), fill_value=0)
        .reset_index(name="casos")
    )
    counts.columns = ["Estado", label_col, "casos"]

    fig = px.bar(
        counts,
        x=label_col,
        y="casos",
        color="Estado",
        barmode="group",
        category_orders={label_col: order},
        color_discrete_map={"Apareció": "#2E7D32", "No apareció": "#C62828"},
        labels={label_col: "Tono", "casos": "Casos"},
        title="Tono del texto, por estado de aparición",
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
# G8 — Topic modeling (TF-IDF + K-Means)
# ---------------------------------------------------------------------------

@safe_plot(fallback_title="No se pudo generar el tamaño de los temas")
def plot_topic_sizes(sizes: dict, labels: dict) -> go.Figure:
    """Barras horizontales: cantidad de casos por tema (cluster)."""
    data = pd.DataFrame({
        "tema": [labels[k] for k in sizes.keys()],
        "casos": list(sizes.values()),
    }).sort_values("casos", ascending=True)

    fig = px.bar(
        data,
        x="casos",
        y="tema",
        orientation="h",
        color="casos",
        color_continuous_scale="Purples",
        labels={"tema": "Tema", "casos": "Casos"},
        title="Casos por tema",
    )
    fig.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_size=13,
        yaxis={"tickfont": {"size": 11}},
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    return fig


@safe_plot(fallback_title="No se pudo generar la proyección de temas")
def plot_topics_scatter(coords_2d, cluster_ids, labels: dict) -> go.Figure:
    """
    Scatter 2D (proyección SVD del espacio TF-IDF) de los documentos,
    coloreado por tema. Permite "ver" visualmente qué tan separados
    están los clusters -no son coordenadas geográficas ni tienen una
    unidad interpretable, son ejes latentes de similitud de texto-.
    """
    data = pd.DataFrame({
        "x": coords_2d[:, 0],
        "y": coords_2d[:, 1],
        "Tema": [labels[c] for c in cluster_ids],
    })

    fig = px.scatter(
        data,
        x="x",
        y="y",
        color="Tema",
        opacity=0.75,
        labels={"x": "Componente 1", "y": "Componente 2"},
        title="Casos agrupados por tema (proyección 2D de similitud de texto)",
    )
    fig.update_traces(marker_size=7)
    fig.update_layout(
        legend_title_text="Tema",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_size=13,
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig
