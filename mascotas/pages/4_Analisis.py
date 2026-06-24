"""
Pagina: Analisis.

Panel con los indicadores y graficos del proyecto. Incluye controles que
filtran los datos y afectan a los graficos: por estado, por especie y por
origen (usuario o scraping). Los graficos se construyen con Plotly para
que sean interactivos.
"""

from __future__ import annotations

import streamlit as st
import plotly.express as px

from ui import styles, components
from ui import theme
from src.services import anuncios_service, difusion_service, metrics_service
from src.utils.errors import PatitasError

st.set_page_config(page_title="Analisis — Patitas", page_icon="🐾", layout="wide")
styles.aplicar(st)
styles.encabezado_marca(st, "Panel de analisis")

# --- Controles -------------------------------------------------------------
with st.sidebar:
    st.markdown("### Controles")
    origen = st.selectbox(
        "Origen de los datos",
        options=[None, "usuario", "scraping"],
        format_func=lambda v: {
            None: "Todos",
            "usuario": "Publicados por usuarios",
            "scraping": "Recolectados de la web",
        }[v],
    )

# --- Carga de datos --------------------------------------------------------
try:
    anuncios = anuncios_service.listar_anuncios(limite=1000)
    difusiones = difusion_service.listar_difusiones()
except PatitasError as exc:
    st.error(f"No se pudieron cargar los datos: {exc}")
    anuncios, difusiones = [], []

# Filtro por origen, aplicado en memoria.
if origen:
    anuncios = [a for a in anuncios if a.origen == origen]

df = metrics_service.anuncios_a_dataframe(anuncios)

if df.empty:
    st.info(
        "Aun no hay datos para analizar. Publica reportes o ejecuta el "
        "scraping para poblar la base."
    )
    components.pie_pagina(st)
    st.stop()

# --- Indicadores -----------------------------------------------------------
kpis = metrics_service.indicadores(df)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total", kpis["total"])
c2.metric("Perdidos", kpis["perdidos"])
c3.metric("Encontrados", kpis["encontrados"])
c4.metric("Reunidos", kpis["reunidos"])
c5.metric("Tasa de reunion", f"{kpis['tasa_reunion']} %")

st.divider()

# --- Graficos en dos columnas ----------------------------------------------
col_izq, col_der = st.columns(2)

with col_izq:
    st.markdown("#### Anuncios por estado")
    por_estado = metrics_service.conteo_por_columna(df, "estado")
    fig_estado = px.pie(
        por_estado,
        names="estado",
        values="cantidad",
        color="estado",
        color_discrete_map=theme.COLOR_ESTADO,
        hole=0.45,
    )
    fig_estado.update_layout(showlegend=True, margin=dict(t=10, b=10))
    st.plotly_chart(fig_estado, use_container_width=True)

with col_der:
    st.markdown("#### Anuncios por especie")
    por_especie = metrics_service.conteo_por_columna(df, "especie")
    fig_especie = px.bar(
        por_especie,
        x="especie",
        y="cantidad",
        color_discrete_sequence=[theme.PINO],
    )
    fig_especie.update_layout(margin=dict(t=10, b=10), xaxis_title="", yaxis_title="")
    st.plotly_chart(fig_especie, use_container_width=True)

# --- Anuncios por distrito (ancho completo) --------------------------------
st.markdown("#### Anuncios por distrito")
por_distrito = metrics_service.conteo_por_columna(df, "distrito")
por_distrito = por_distrito.sort_values("cantidad", ascending=True).tail(15)
fig_distrito = px.bar(
    por_distrito,
    x="cantidad",
    y="distrito",
    orientation="h",
    color_discrete_sequence=[theme.MIEL],
)
fig_distrito.update_layout(margin=dict(t=10, b=10), xaxis_title="", yaxis_title="")
st.plotly_chart(fig_distrito, use_container_width=True)

# --- Tendencia temporal ----------------------------------------------------
serie = metrics_service.serie_temporal(df)
if not serie.empty:
    st.markdown("#### Publicaciones en el tiempo")
    fig_tiempo = px.line(
        serie, x="fecha", y="cantidad", markers=True,
        color_discrete_sequence=[theme.CORAL],
    )
    fig_tiempo.update_layout(margin=dict(t=10, b=10), xaxis_title="", yaxis_title="")
    st.plotly_chart(fig_tiempo, use_container_width=True)

# --- Difusiones por canal --------------------------------------------------
canal_df = metrics_service.difusiones_por_canal(difusiones)
if not canal_df.empty:
    st.markdown("#### Difusiones por red social")
    canal_df["canal"] = canal_df["canal"].map(
        lambda c: theme.NOMBRE_CANAL.get(c, c)
    )
    fig_canal = px.bar(
        canal_df,
        x="canal",
        y="cantidad",
        color_discrete_sequence=[theme.PINO],
    )
    fig_canal.update_layout(margin=dict(t=10, b=10), xaxis_title="", yaxis_title="")
    st.plotly_chart(fig_canal, use_container_width=True)
else:
    st.caption(
        "Aun no se han registrado difusiones. Comparte anuncios desde la "
        "pagina Difundir para ver este grafico."
    )

components.pie_pagina(st)
