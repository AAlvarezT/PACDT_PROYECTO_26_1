"""
Pagina: Tablon.

Muestra todas las mascotas con filtros (estado, especie, distrito y
busqueda) y un mapa con la ubicacion aproximada de cada caso. Los filtros
afectan tanto la lista como el mapa. Cuando no hay resultados, muestra un
estado vacio con diseno en lugar de una pantalla en blanco.
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
styles.encabezado_marca(st)
styles.seccion(st, "Tablon de mascotas", "Explora los reportes y ayuda a difundirlos")

ETIQUETAS_ESTADO = {"perdido": "Perdido", "encontrado": "Encontrado", "reunido": "En casa"}
ETIQUETAS_ESPECIE = {"perro": "Perro", "gato": "Gato", "otro": "Otra"}

# --- Filtros en la barra lateral -------------------------------------------
with st.sidebar:
    styles.encabezado_marca(st)
    st.markdown("#### Filtros")
    estado = st.selectbox(
        "Estado", options=[None] + list(ESTADOS),
        format_func=lambda v: "Todos" if v is None else ETIQUETAS_ESTADO[v],
    )
    especie = st.selectbox(
        "Especie", options=[None] + list(ESPECIES),
        format_func=lambda v: "Todas" if v is None else ETIQUETAS_ESPECIE[v],
    )
    distrito = st.selectbox(
        "Distrito", options=[None] + list(DISTRITOS),
        format_func=lambda v: "Todos" if v is None else v,
    )
    texto = st.text_input("Buscar", placeholder="Nombre, raza o sena")

# --- Carga con los filtros aplicados ---------------------------------------
try:
    anuncios = anuncios_service.listar_anuncios(
        estado=estado, especie=especie, distrito=distrito, texto=texto or None,
    )
    error = None
except PatitasError as exc:
    anuncios, error = [], str(exc)

if error:
    st.error(f"No se pudieron cargar los anuncios: {error}")

# --- Resumen y mapa --------------------------------------------------------
if anuncios:
    st.caption(f"{len(anuncios)} mascotas encontradas")
    mapa = components.mapa_anuncios(anuncios)
    if mapa is not None:
        try:
            from streamlit_folium import st_folium
            st_folium(mapa, height=360, width=None)
        except ImportError:
            st.info("Para ver el mapa instala streamlit-folium.")

    st.markdown("")  # respiro
    # --- Cuadricula de tarjetas --------------------------------------------
    cols = st.columns(3)
    for indice, anuncio in enumerate(anuncios):
        with cols[indice % 3]:
            components.tarjeta_anuncio(st, anuncio)
            if anuncio.estado != "reunido" and anuncio.id:
                if st.button("Marcar como en casa", key=f"reunir_{anuncio.id}"):
                    try:
                        anuncios_service.cambiar_estado(anuncio.id, "reunido")
                        st.success("Que alegria. Actualizado.")
                        st.rerun()
                    except PatitasError as exc:
                        st.error(f"No se pudo actualizar: {exc}")
            st.markdown("")  # separacion entre tarjetas
elif not error:
    components.estado_vacio(
        st, "ti-search",
        "No hay mascotas con estos filtros",
        "Prueba a ampliar la busqueda, o publica un reporte desde la pagina Publicar.",
    )

components.pie_pagina(st)
