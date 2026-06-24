"""
Componentes reutilizables de la interfaz.

Funciones que dibujan piezas de la interfaz que se repiten en varias
paginas, como la tarjeta de un anuncio o el mapa de ubicaciones. Aislar
estos componentes evita repetir codigo y mantiene un aspecto consistente.
"""

from __future__ import annotations

import html

from src.models.anuncio import Anuncio
from src.utils.geo import coords_de
from ui import theme


def etiqueta_estado(estado: str) -> str:
    """Devuelve el HTML de una etiqueta de color segun el estado."""
    color = theme.COLOR_ESTADO.get(estado, theme.GRIS)
    texto = theme.ETIQUETA_ESTADO.get(estado, estado.capitalize())
    return (
        f'<span class="etiqueta" style="background:{color}">'
        f'{html.escape(texto)}</span>'
    )


def tarjeta_anuncio(st, anuncio: Anuncio) -> None:
    """
    Dibuja la tarjeta de un anuncio.

    Muestra el titulo, la especie, el distrito, la fecha del hecho, la
    etiqueta de estado y un extracto de la descripcion. Si hay foto, la
    coloca arriba.
    """
    especie = theme.ETIQUETA_ESPECIE.get(anuncio.especie, anuncio.especie)
    meta = especie
    if anuncio.distrito:
        meta += f"  ·  {anuncio.distrito}"
    if anuncio.fecha_evento:
        meta += f"  ·  {anuncio.fecha_evento}"

    descripcion = html.escape(anuncio.descripcion[:220])
    if len(anuncio.descripcion) > 220:
        descripcion += "..."

    if anuncio.foto_url:
        st.image(anuncio.foto_url, use_container_width=True)

    st.markdown(
        f"""
        <div class="tarjeta">
            <div class="titulo">{html.escape(anuncio.titulo)}</div>
            <div class="meta">{html.escape(meta)}</div>
            {etiqueta_estado(anuncio.estado)}
            <div class="descripcion" style="margin-top:0.6rem">{descripcion}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mapa_anuncios(anuncios: list[Anuncio]):
    """
    Construye un mapa de Folium con la ubicacion aproximada de cada anuncio.

    Usa el centro del distrito como coordenada, porque los anuncios se
    registran por distrito y no por direccion exacta. Devuelve el mapa, o
    None si la libreria no esta disponible o no hay ubicaciones.
    """
    try:
        import folium
    except ImportError:
        return None

    ubicados = [a for a in anuncios if coords_de(a.distrito)]
    if not ubicados:
        return None

    centro = coords_de(ubicados[0].distrito)
    mapa = folium.Map(location=centro, zoom_start=11, tiles="cartodbpositron")

    for anuncio in ubicados:
        lat, lon = coords_de(anuncio.distrito)
        color = {
            "perdido": "red",
            "encontrado": "orange",
            "reunido": "green",
        }.get(anuncio.estado, "blue")
        folium.Marker(
            location=(lat, lon),
            tooltip=anuncio.titulo,
            popup=f"{anuncio.titulo} ({anuncio.distrito})",
            icon=folium.Icon(color=color, icon="paw", prefix="fa"),
        ).add_to(mapa)

    return mapa


def pie_pagina(st) -> None:
    """Dibuja un pie discreto comun a todas las paginas."""
    st.markdown(
        '<div class="pie">Patitas — De vuelta a casa  ·  '
        'Proyecto academico de ciencia de datos</div>',
        unsafe_allow_html=True,
    )
