"""
app.py
Dashboard interactivo — Personas Desaparecidas en Perú (RENIPED)
Ejecutar con: streamlit run src/app.py
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from processing import clean_data, get_summary, load_data
from sentiment import SENTIMENT_ELIGIBLE_COLUMNS, add_sentiment, load_analyzer
from topics import TOPIC_ELIGIBLE_COLUMNS, fit_topics
from utils import logger
from viz import (
    plot_age_dist,
    plot_aparecido_donut,
    plot_hours_box,
    plot_map,
    plot_sentiment_dist,
    plot_time_series,
    plot_top_regions,
    plot_topic_sizes,
    plot_topics_scatter,
    plot_wordcloud,
)

# ---------------------------------------------------------------------------
# Configuración de página
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Desaparecidos Perú — RENIPED",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "data_raw.csv"

# ---------------------------------------------------------------------------
# Carga con caché
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Cargando modelo de sentimiento (RoBERTuito, ~435 MB la primera vez)...")
def get_sentiment_analyzer():
    """
    Carga el modelo de sentimiento una sola vez por sesión del proceso
    (st.cache_resource, no st.cache_data: es un objeto/modelo, no datos
    serializables).

    Si falla (librería no instalada, sin internet la primera vez, RAM
    insuficiente), se loguea y se retorna None: el resto del dashboard
    sigue funcionando, solo sin la sección de sentimientos -ver cómo se
    usa este valor en get_data() y en la pestaña de Texto-.
    """
    try:
        return load_analyzer()
    except ImportError:
        logger.exception("pysentimiento no está instalado")
        return None
    except Exception:
        logger.exception("No se pudo cargar el modelo de sentimiento")
        return None


@st.cache_data(show_spinner="Cargando datos...")
def get_data():
    """
    Carga y limpia el dataset (cacheado por Streamlit).

    Cualquier problema de archivo, formato o columnas faltantes se
    muestra al usuario con st.error() y detiene la ejecución de forma
    controlada (st.stop()), en vez de romper la app con un traceback
    completo en pantalla.
    """
    try:
        df = load_data(DATA_PATH)
        df, _ = clean_data(df)
        # Sentimiento se calcula una sola vez aquí (cacheado junto con la
        # limpieza), no en cada rerender al mover un filtro del sidebar.
        analyzer = get_sentiment_analyzer()
        if analyzer is None:
            logger.warning("Modelo de sentimiento no disponible: se omite esa columna.")
        else:
            for col in SENTIMENT_ELIGIBLE_COLUMNS:
                if col in df.columns:
                    df = add_sentiment(df, col, analyzer)
        return df
    except FileNotFoundError as e:
        st.error(f"⚠️ No se encontró el archivo de datos.\n\n{e}")
        st.stop()
    except ValueError as e:
        st.error(f"⚠️ El archivo de datos tiene un problema de formato o le faltan columnas.\n\n{e}")
        st.stop()
    except Exception as e:
        logger.exception("Error inesperado cargando datos")
        st.error(f"⚠️ Ocurrió un error inesperado al cargar los datos: {e}")
        st.stop()


df_full = get_data()

# El warning de "modelo no disponible" dentro de get_data() solo se loguea
# a la terminal (las llamadas a st.* dentro de una función @st.cache_data
# no se vuelven a mostrar en reruns posteriores con cache hit). Por eso
# se revisa aquí, en el cuerpo principal del script, que sí se ejecuta
# en cada rerun: así el aviso es visible en la app de forma confiable,
# no solo en la consola donde corriste `streamlit run`.
_sentiment_disponible = any(
    f"{c}_sentimiento_label" in df_full.columns for c in SENTIMENT_ELIGIBLE_COLUMNS
)
if not _sentiment_disponible:
    st.warning(
        "⚠️ El análisis de sentimientos no está disponible (el modelo no pudo cargar). "
        "Revisa la terminal donde corriste `streamlit run` para ver el error exacto. "
        "Las causas más comunes: falta instalar `pysentimiento` (`pip install -r requirements.txt`), "
        "o no había internet la primera vez que se descarga el modelo (~435 MB) desde Hugging Face. "
        "El resto del dashboard funciona igual; solo se omite esta sección."
    )

# ---------------------------------------------------------------------------
# Sidebar — filtros globales
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🔎 Filtros")
    st.divider()

    edad_rango = st.slider(
        "Rango de edad",
        min_value=0, max_value=100,
        value=(0, 100),
        step=1,
    )

    aparecido_sel = st.selectbox(
        "Estado de aparición",
        options=["Todos", "Apareció", "No apareció"],
    )

    sentiment_col = st.selectbox(
        "Columna de texto para sentimiento",
        options=SENTIMENT_ELIGIBLE_COLUMNS,
        help="Sobre qué columna se calcula el tono. Se usa para el filtro de abajo y para la pestaña de Texto.",
    )

    tono_sel = st.selectbox(
        "Tono del texto",
        options=["Todos", "Positivo", "Neutral", "Negativo"],
    )

    st.divider()
    st.caption("Opciones de gráficos")

    top_n = st.slider(
        "Top N regiones",
        min_value=5, max_value=15,
        value=10, step=1,
    )

    wc_col = st.selectbox(
        "Nube de palabras sobre",
        options=["Circunstancias", "Vestimenta", "Otras observaciones"],
    )

    st.divider()
    st.caption("Topic modeling (clustering)")

    topic_col = st.selectbox(
        "Columna de texto para temas",
        options=TOPIC_ELIGIBLE_COLUMNS,
    )

    n_topics = st.slider(
        "Número de temas (K)",
        min_value=2, max_value=8,
        value=4, step=1,
        help="K para K-Means. Más temas = grupos más específicos pero más pequeños.",
    )

    st.divider()
    st.caption("Fuente: RENIPED — Policía Nacional del Perú")
    st.caption("https://desaparecidosenperu.policia.gob.pe/")

# ---------------------------------------------------------------------------
# Aplicar filtros
# ---------------------------------------------------------------------------

df = df_full.copy()
df = df[(df["EDAD"] >= edad_rango[0]) & (df["EDAD"] <= edad_rango[1])]

if aparecido_sel == "Apareció":
    df = df[df["Aparecido"] == True]
elif aparecido_sel == "No apareció":
    df = df[df["Aparecido"] == False]

if tono_sel != "Todos":
    _label_col_filtro = f"{sentiment_col}_sentimiento_label"
    if _label_col_filtro in df.columns:
        df = df[df[_label_col_filtro] == tono_sel]

# ---------------------------------------------------------------------------
# Encabezado + KPIs
# ---------------------------------------------------------------------------

st.title("🔍 Personas Desaparecidas en Perú")
st.caption("Datos del Registro Nacional de Información de Personas Desaparecidas (RENIPED)")

if df.empty:
    st.warning("No hay registros para los filtros seleccionados.")
    st.stop()

summary = get_summary(df)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total de casos",               f"{summary['total']:,}")
c2.metric("Aparecidos",                   f"{summary['pct_aparecidos']}%")
c3.metric("Menores de 18 años",           f"{summary['pct_menores']}%")
c4.metric("Mediana horas hasta denuncia", f"{summary['mediana_horas_denuncia']} h")

st.divider()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_explorar, tab_analisis, tab_texto = st.tabs(
    ["📊 Explorar", "🗺️ Análisis", "☁️ Texto"]
)

# ── Tab 1: Explorar ──────────────────────────────────────────────────────────
with tab_explorar:
    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(plot_age_dist(df), use_container_width=True)
    with col_r:
        st.plotly_chart(plot_time_series(df), use_container_width=True)

    st.subheader("Tabla de casos")

    TABLA_COLS = [
        "Nombres", "EDAD", "region",
        "Aparecido", "Fecha Hecho",
        "Horas para Denunciar", "Horas para Aparecer",
    ]
    tabla_cols_presentes = [c for c in TABLA_COLS if c in df.columns]
    df_tabla = df[tabla_cols_presentes].copy()
    df_tabla["Aparecido"] = df_tabla["Aparecido"].map({True: "Sí", False: "No"})

    st.dataframe(df_tabla, use_container_width=True, hide_index=True)
    st.download_button(
        label="⬇️ Descargar tabla filtrada (.csv)",
        data=df_tabla.to_csv(index=False).encode("utf-8"),
        file_name="reniped_filtrado.csv",
        mime="text/csv",
    )

# ── Tab 2: Análisis ───────────────────────────────────────────────────────────
with tab_analisis:
    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(plot_aparecido_donut(df), use_container_width=True)
    with col_r:
        st.plotly_chart(plot_hours_box(df), use_container_width=True)

    st.plotly_chart(plot_top_regions(df, n=top_n), use_container_width=True)
    st.plotly_chart(plot_map(df), use_container_width=True)

# ── Tab 3: Texto ──────────────────────────────────────────────────────────────
with tab_texto:
    st.subheader(f"Nube de palabras — {wc_col}")

    if wc_col not in df.columns or df[wc_col].dropna().empty:
        st.info(f'No hay texto disponible en "{wc_col}" con los filtros actuales.')
    else:
        fig_wc = plot_wordcloud(df, wc_col)
        if fig_wc is None:
            st.info("Texto insuficiente para generar la nube.")
        else:
            st.pyplot(fig_wc, use_container_width=True)

        with st.expander("Ver textos originales"):
            st.dataframe(
                df[["Nombres", wc_col]].dropna(subset=[wc_col]),
                use_container_width=True,
                hide_index=True,
            )

    st.divider()
    st.subheader(f"Temas (clustering) — {topic_col}")
    st.caption(
        "TF-IDF + K-Means (scikit-learn): agrupa los casos por similitud de "
        "palabras y muestra los términos más característicos de cada grupo. "
        "Ver topics.py para metodología y limitaciones."
    )

    try:
        topics_result = fit_topics(df, topic_col, n_topics=n_topics)
    except ValueError as e:
        st.info(str(e))
    else:
        sizes, labels = topics_result["sizes"], topics_result["labels"]

        if topics_result["silhouette"] is not None:
            st.caption(
                f"Silhouette score: **{topics_result['silhouette']}** "
                "(de -1 a 1; más alto = clusters mejor separados. "
                "Prueba cambiar K en el sidebar para comparar.)"
            )

        col_l, col_r = st.columns([1, 1.4])
        with col_l:
            st.plotly_chart(plot_topic_sizes(sizes, labels), use_container_width=True)
        with col_r:
            st.plotly_chart(
                plot_topics_scatter(topics_result["coords_2d"], topics_result["cluster_ids"], labels),
                use_container_width=True,
            )

        with st.expander("Ver términos completos por tema"):
            for k, terms in topics_result["terms_per_topic"].items():
                st.markdown(f"**{labels[k]}**")
                st.write(", ".join(terms) if terms else "(sin términos suficientes)")

        df_topics_export = (
            topics_result["df"][["Nombres", topic_col, f"{topic_col}_tema", f"{topic_col}_tema_label"]]
            .dropna(subset=[topic_col])
            .copy()
        )
        with st.expander("Ver casos con su tema asignado"):
            st.dataframe(df_topics_export, use_container_width=True, hide_index=True)

        st.download_button(
            label="⬇️ Descargar temas (.csv)",
            data=df_topics_export.to_csv(index=False).encode("utf-8"),
            file_name=f"reniped_temas_{topic_col.lower().replace(' ', '_')}.csv",
            mime="text/csv",
        )

    st.divider()
    st.subheader(f"Análisis de sentimientos — {sentiment_col}")
    st.caption(
        "Modelo: RoBERTuito (pysentimiento), Transformer pre-entrenado en español "
        "y fine-tuneado para sentimiento (Pérez et al., 2021). Ver sentiment.py "
        "para detalles, limitaciones y citación."
    )

    label_col = f"{sentiment_col}_sentimiento_label"

    if label_col not in df.columns or df[sentiment_col].dropna().empty:
        st.info(f'No hay texto disponible en "{sentiment_col}" con los filtros actuales.')
    else:
        dist_pct = df[label_col].value_counts(normalize=True).mul(100).round(1)
        k1, k2, k3 = st.columns(3)
        k1.metric("😟 Negativo", f"{dist_pct.get('Negativo', 0.0)}%")
        k2.metric("😐 Neutral", f"{dist_pct.get('Neutral', 0.0)}%")
        k3.metric("🙂 Positivo", f"{dist_pct.get('Positivo', 0.0)}%")

        st.plotly_chart(plot_sentiment_dist(df, label_col), use_container_width=True)

        df_sent_export = (
            df[["Nombres", sentiment_col, f"{sentiment_col}_sentimiento", label_col]]
            .dropna(subset=[sentiment_col])
            .copy()
        )

        with st.expander("Ver casos con su tono asignado"):
            st.dataframe(df_sent_export, use_container_width=True, hide_index=True)

        st.download_button(
            label="⬇️ Descargar análisis de sentimientos (.csv)",
            data=df_sent_export.to_csv(index=False).encode("utf-8"),
            file_name=f"reniped_sentimiento_{sentiment_col.lower().replace(' ', '_')}.csv",
            mime="text/csv",
        )
