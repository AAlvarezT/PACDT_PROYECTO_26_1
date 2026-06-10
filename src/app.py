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
from viz import (
    plot_age_dist,
    plot_aparecido_donut,
    plot_hours_box,
    plot_map,
    plot_time_series,
    plot_top_regions,
    plot_wordcloud,
    plot_heatmap_temporal,
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

@st.cache_data(show_spinner="Cargando datos...")
def get_data():
    df = load_data(DATA_PATH)
    df, _ = clean_data(df)
    return df


df_full = get_data()

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
    st.plotly_chart(plot_heatmap_temporal(df), use_container_width=True)

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
