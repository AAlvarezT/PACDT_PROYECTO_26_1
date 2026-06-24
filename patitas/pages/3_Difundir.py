"""
Pagina: Difundir.

Permite elegir un anuncio y compartirlo en redes sociales. Genera un
mensaje listo para publicar, los enlaces de comparticion para cada red y
un codigo QR descargable para carteles fisicos. Cada vez que el usuario
comparte por un canal, lo registra en la base para el analisis.
"""

from __future__ import annotations

import streamlit as st

from ui import styles, components
from src.services import anuncios_service, difusion_service
from src.services.difusion_service import CANALES
from src.models.anuncio import Anuncio
from ui import theme
from src.utils.errors import PatitasError

st.set_page_config(page_title="Difundir — Patitas", page_icon="🐾", layout="centered")
styles.aplicar(st)
styles.encabezado_marca(st)
styles.seccion(st, "Difundir un reporte", "Comparte y multiplica las posibilidades de un reencuentro")

st.markdown(
    "Elige un anuncio y compartelo. Mientras mas personas lo vean, mas "
    "posibilidades de encontrar a la mascota."
)

# --- Cargar anuncios activos (no reunidos) ---------------------------------
try:
    todos = anuncios_service.listar_anuncios(limite=300)
except PatitasError as exc:
    st.error(f"No se pudieron cargar los anuncios: {exc}")
    todos = []

activos = [a for a in todos if a.estado != "reunido" and a.id]

if not activos:
    st.info(
        "No hay anuncios activos para difundir. Publica un reporte desde la "
        "pagina Publicar."
    )
    components.pie_pagina(st)
    st.stop()

# Si se viene de publicar un anuncio, preseleccionarlo.
id_preferido = st.session_state.get("ultimo_anuncio_id")
opciones = {a.id: a for a in activos}
indice_inicial = 0
if id_preferido in opciones:
    indice_inicial = list(opciones.keys()).index(id_preferido)

id_elegido = st.selectbox(
    "Anuncio",
    options=list(opciones.keys()),
    index=indice_inicial,
    format_func=lambda i: opciones[i].titulo,
)
anuncio: Anuncio = opciones[id_elegido]

# --- Vista previa del anuncio ----------------------------------------------
components.tarjeta_anuncio(st, anuncio)

# --- Mensaje para compartir ------------------------------------------------
st.markdown("#### Mensaje")
mensaje = difusion_service.construir_mensaje(anuncio)
st.text_area(
    "Puedes copiarlo y ajustarlo antes de publicar",
    value=mensaje,
    height=160,
)

# --- Enlaces de comparticion -----------------------------------------------
st.markdown("#### Compartir")
st.caption(
    "Al abrir un enlace, la red social se abre con el mensaje ya cargado. "
    "Luego marca abajo por donde compartiste para llevar el registro."
)

enlaces = difusion_service.generar_enlaces(anuncio)
cols = st.columns(len(CANALES))
for columna, canal in zip(cols, CANALES):
    with columna:
        st.link_button(theme.NOMBRE_CANAL[canal], enlaces[canal])

# --- Registro de difusion --------------------------------------------------
st.markdown("#### Registrar difusion")
registro_cols = st.columns(len(CANALES))
for columna, canal in zip(registro_cols, CANALES):
    with columna:
        if st.button(f"Comparti en {theme.NOMBRE_CANAL[canal]}", key=f"reg_{canal}"):
            try:
                difusion_service.registrar_difusion(anuncio.id, canal)
                st.success("Registrado. Gracias.")
            except PatitasError as exc:
                st.error(f"No se pudo registrar: {exc}")

# --- Codigo QR -------------------------------------------------------------
st.markdown("#### Cartel con codigo QR")
st.caption(
    "Descarga este codigo QR e imprimelo en un cartel. Quien lo escanee "
    "llegara al anuncio."
)
try:
    qr = difusion_service.generar_qr(anuncio)
    col_qr, col_btn = st.columns([1, 2])
    with col_qr:
        st.image(qr, width=160)
    with col_btn:
        st.download_button(
            "Descargar codigo QR",
            data=qr,
            file_name=f"patitas_qr_{anuncio.id}.png",
            mime="image/png",
        )
except RuntimeError as exc:
    st.info(str(exc))

components.pie_pagina(st)
