"""
Componentes reutilizables de la interfaz.

Dibujan las piezas que se repiten en varias paginas: la tarjeta de una
mascota, el bloque de contacto, las historias de exito, los pasos de "como
funciona", los estados vacios y el mapa.

La tarjeta se construye como HTML propio (no con st.image) para controlar
el recorte de la foto con CSS. Asi la imagen siempre se ve proporcionada,
sin importar su tamano original.
"""

from __future__ import annotations

import html
import re

from src.models.anuncio import Anuncio
from src.utils.geo import coords_de
from ui import theme


def _telefono_limpio(telefono: str) -> str:
    """Deja solo los digitos de un telefono, para armar el enlace de WhatsApp."""
    return re.sub(r"\D", "", telefono or "")


def enlace_whatsapp_contacto(anuncio: Anuncio) -> str:
    """
    Arma el enlace de WhatsApp para contactar a quien publico el anuncio.

    Antepone el codigo de Peru (51) si el numero no lo trae. Devuelve cadena
    vacia si no hay telefono.
    """
    digitos = _telefono_limpio(anuncio.contacto_telefono)
    if not digitos:
        return ""
    if not digitos.startswith("51"):
        digitos = "51" + digitos
    mensaje = f"Hola, vi tu publicacion en Patitas sobre {anuncio.titulo}."
    from urllib.parse import quote
    return f"https://wa.me/{digitos}?text={quote(mensaje)}"


def etiqueta_estado_html(estado: str) -> str:
    """Devuelve el HTML de la etiqueta de color segun el estado."""
    color = theme.COLOR_ESTADO.get(estado, theme.GRIS)
    texto = theme.ETIQUETA_ESTADO.get(estado, estado.capitalize())
    icono = theme.ICONO_ESTADO.get(estado, "ti-paw")
    return (
        f'<span class="etiqueta" style="background:{color}">'
        f'<i class="ti {icono}"></i>{html.escape(texto)}</span>'
    )


def tarjeta_anuncio(st, anuncio: Anuncio) -> None:
    """
    Dibuja la tarjeta de una mascota como HTML.

    Incluye foto recortada (o un marcador si no hay), etiqueta de estado,
    titulo, metadatos con iconos, un extracto y el boton de contacto por
    WhatsApp cuando hay telefono.
    """
    # Foto: si hay URL se recorta con CSS; si no, marcador con icono.
    icono_especie = theme.ICONO_ESPECIE.get(anuncio.especie, "ti-paw")
    if anuncio.foto_url:
        foto = f'<img class="foto" src="{html.escape(anuncio.foto_url)}" alt="Foto de la mascota">'
    else:
        foto = f'<div class="foto-vacia"><i class="ti {icono_especie}"></i></div>'

    # Metadatos con iconos
    especie = theme.ETIQUETA_ESPECIE.get(anuncio.especie, "Mascota")
    metas = [f'<span><i class="ti {icono_especie}"></i>{html.escape(especie)}</span>']
    if anuncio.distrito:
        metas.append(f'<span><i class="ti ti-map-pin"></i>{html.escape(anuncio.distrito)}</span>')
    if anuncio.fecha_evento:
        metas.append(f'<span><i class="ti ti-calendar"></i>{html.escape(str(anuncio.fecha_evento))}</span>')
    meta_html = "".join(metas)

    descripcion = html.escape(anuncio.descripcion or "")

    # Boton de contacto por WhatsApp
    enlace = enlace_whatsapp_contacto(anuncio)
    if enlace:
        contacto = (
            f'<a class="contacto" href="{enlace}" target="_blank">'
            f'<i class="ti ti-brand-whatsapp"></i>Contactar</a>'
        )
    else:
        contacto = ""

    st.markdown(
        f"""
        <div class="tarjeta">
            {foto}
            <div class="cuerpo">
                {etiqueta_estado_html(anuncio.estado)}
                <div class="titulo">{html.escape(anuncio.titulo)}</div>
                <div class="meta">{meta_html}</div>
                <div class="descripcion">{descripcion}</div>
                {contacto}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def paso(st, numero: int, icono: str, titulo: str, texto: str) -> None:
    """Dibuja una tarjeta de paso para la seccion 'como funciona'."""
    st.markdown(
        f"""
        <div class="paso">
            <div class="num"><i class="ti {icono}"></i></div>
            <h4>{numero}. {html.escape(titulo)}</h4>
            <p>{html.escape(texto)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def historia(st, cita: str, autor: str) -> None:
    """Dibuja una tarjeta de historia de exito."""
    st.markdown(
        f"""
        <div class="historia">
            <div class="cita">"{html.escape(cita)}"</div>
            <div class="autor">{html.escape(autor)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def confianza(st, icono: str, texto: str) -> None:
    """Dibuja una insignia de confianza (seguridad, verificacion, etc.)."""
    st.markdown(
        f'<div class="confianza"><i class="ti {icono}"></i>{html.escape(texto)}</div>',
        unsafe_allow_html=True,
    )


def estado_vacio(st, icono: str, titulo: str, texto: str) -> None:
    """Dibuja un estado vacio con diseno, en lugar de una pantalla en blanco."""
    st.markdown(
        f"""
        <div class="vacio">
            <i class="ti {icono}"></i>
            <div class="t">{html.escape(titulo)}</div>
            <div>{html.escape(texto)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mapa_anuncios(anuncios: list[Anuncio]):
    """
    Construye un mapa de Folium con la ubicacion aproximada de cada anuncio.

    Usa el centro del distrito como coordenada. Devuelve el mapa, o None si
    Folium no esta disponible o no hay ubicaciones.
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
        color = {"perdido": "red", "encontrado": "orange", "reunido": "green"}.get(
            anuncio.estado, "blue"
        )
        folium.Marker(
            location=(lat, lon),
            tooltip=anuncio.titulo,
            popup=f"{anuncio.titulo} ({anuncio.distrito})",
            icon=folium.Icon(color=color, icon="paw", prefix="fa"),
        ).add_to(mapa)
    return mapa


def pie_pagina(st) -> None:
    """Pie comun. Se delega en styles para mantener un solo lugar."""
    from ui import styles
    styles.pie_pagina(st)
