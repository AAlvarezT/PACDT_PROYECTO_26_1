"""
Pagina: Tablon.

Muestra todos los anuncios con filtros interactivos (estado, especie,
distrito y busqueda por texto) y un mapa con la ubicacion aproximada de
cada caso. Los filtros afectan tanto la lista como el mapa.
"""

from __future__ import annotations

import streamlit as st

from ui import styles, components
from src.models.anuncio import ESPECIES, ESTADOS
from src.services import anuncios_service
from src.utils.geo import DISTRITOS
from src.utils.errors import PatitasError

st.set_page_config(page_title="Tablon — Patitas", page_icon="🐾", layout="wide")
styles.aplicar(st)
styles.encabezado_marca(st, "Tablon de mascotas")

ETIQUETAS_ESTADO = {"perdido": "Perdido", "encontrado": "Encontrado", "reunido": "Reunido"}
ETIQUETAS_ESPECIE = {"perro": "Perro", "gato": "Gato", "otro": "Otra"}

# --- Filtros ---------------------------------------------------------------
with st.sidebar:
    st.markdown("### Filtros")
    estado = st.selectbox(
        "Estado",
        options=[None] + list(ESTADOS),
        format_func=lambda v: "Todos" if v is None else ETIQUETAS_ESTADO[v],
    )
    especie = st.selectbox(
        "Especie",
        options=[None] + list(ESPECIES),
        format_func=lambda v: "Todas" if v is None else ETIQUETAS_ESPECIE[v],
    )
    distrito = st.selectbox(
        "Distrito",
        options=[None] + list(DISTRITOS),
        format_func=lambda v: "Todos" if v is None else v,
    )
    texto = st.text_input("Buscar", placeholder="Nombre, raza o sena")

# --- Carga de datos con los filtros aplicados ------------------------------
try:
    anuncios = anuncios_service.listar_anuncios(
        estado=estado,
        especie=especie,
        distrito=distrito,
        texto=texto or None,
    )
except PatitasError as exc:
    st.error(f"No se pudieron cargar los anuncios: {exc}")
    anuncios = []

st.caption(f"{len(anuncios)} anuncios encontrados")

# --- Mapa ------------------------------------------------------------------
mapa = components.mapa_anuncios(anuncios)
if mapa is not None:
    try:
        from streamlit_folium import st_folium
        st_folium(mapa, height=380, use_container_width=True)
    except ImportError:
        st.info(
            "Para ver el mapa, instala streamlit-folium: "
            "pip install streamlit-folium"
        )

st.divider()

# --- Lista de anuncios en columnas -----------------------------------------
if not anuncios:
    st.markdown(
        "No hay anuncios que coincidan con los filtros. Prueba a ampliarlos, "
        "o publica un reporte desde la pagina Publicar."
    )
else:
    columnas = st.columns(3)
    for indice, anuncio in enumerate(anuncios):
        with columnas[indice % 3]:
            components.tarjeta_anuncio(st, anuncio)
            # Permite marcar como reunido directamente desde el tablon.
            if anuncio.estado != "reunido" and anuncio.id:
                if st.button(
                    "Marcar como reunido",
                    key=f"reunir_{anuncio.id}",
                ):
                    try:
                        anuncios_service.cambiar_estado(anuncio.id, "reunido")
                        st.success("Actualizado. Que alegria.")
                        st.rerun()
                    except PatitasError as exc:
                        st.error(f"No se pudo actualizar: {exc}")

components.pie_pagina(st)
