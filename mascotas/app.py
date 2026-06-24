"""
Patitas - Página de inicio.

Punto de entrada de la aplicacion Streamlit. Presenta la plataforma,
muestra algunos indicadores rapidos y guia al usuario hacia las demas
paginas (Publicar, Tablon, Difundir, Analisis).

Ejecutar con:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from ui import styles, components
from src.services import anuncios_service, metrics_service
from src.utils.errors import PatitasError

st.set_page_config(
    page_title="Patitas — De vuelta a casa",
    page_icon="🐾",
    layout="wide",
)

styles.aplicar(st)
styles.encabezado_marca(st)

st.markdown(
    "Una plataforma para reportar mascotas perdidas y encontradas en Lima, "
    "y ayudar a difundir cada caso en redes sociales para que mas personas "
    "puedan reconocerlas."
)

# --- Indicadores rapidos ---------------------------------------------------
try:
    anuncios = anuncios_service.listar_anuncios(limite=500)
    kpis = metrics_service.indicadores(
        metrics_service.anuncios_a_dataframe(anuncios)
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Anuncios", kpis["total"])
    col2.metric("Perdidos", kpis["perdidos"])
    col3.metric("Encontrados", kpis["encontrados"])
    col4.metric("Reunidos", kpis["reunidos"])

    conexion_ok = True
except PatitasError:
    conexion_ok = False
    anuncios = []

if not conexion_ok:
    st.warning(
        "No se pudo conectar con la base de datos. Revisa el archivo .env y "
        "que el esquema este aplicado en Supabase. Mientras tanto, puedes "
        "navegar por la aplicacion."
    )

st.divider()

# --- Guia de uso -----------------------------------------------------------
st.markdown("### Como funciona")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**1. Publica**")
    st.markdown(
        "Reporta a tu mascota perdida o una que encontraste, con foto, zona "
        "y datos de contacto."
    )
with c2:
    st.markdown("**2. Difunde**")
    st.markdown(
        "Genera un mensaje y compartelo en WhatsApp, Facebook, X o Telegram. "
        "Tambien puedes imprimir un cartel con codigo QR."
    )
with c3:
    st.markdown("**3. Reune**")
    st.markdown(
        "Cuando la mascota vuelve a casa, marca el anuncio como reunido para "
        "celebrar el reencuentro."
    )

st.info(
    "Usa el menu de la izquierda para navegar entre las paginas: "
    "Publicar, Tablon, Difundir y Analisis."
)

# --- Anuncios recientes ----------------------------------------------------
if anuncios:
    st.markdown("### Reportes recientes")
    recientes = anuncios[:3]
    columnas = st.columns(len(recientes))
    for columna, anuncio in zip(columnas, recientes):
        with columna:
            components.tarjeta_anuncio(st, anuncio)

components.pie_pagina(st)
