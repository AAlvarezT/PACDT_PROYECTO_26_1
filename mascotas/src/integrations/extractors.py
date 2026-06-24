"""
Extractores de anuncios por sitio.

Un extractor recibe el HTML de una pagina y la URL de origen, y devuelve
una lista de Anuncios. Cada sitio tiene su propia estructura HTML, asi
que tiene su propio extractor. Para agregar una fuente nueva se escribe
un extractor nuevo aqui; el resto del proyecto no cambia.

Decision de diseno: el scraper guarda una referencia al anuncio (el
enlace original y los datos minimos), no una copia del contenido ajeno.
La plataforma actua como indice que dirige a la fuente original.
"""

from __future__ import annotations

from typing import Callable
from urllib.parse import urljoin

from src.models.anuncio import Anuncio
from src.integrations import parser
from src.utils.errors import ScraperError

# Tipo de un extractor: (html, url) -> lista de anuncios.
Extractor = Callable[[str, str], list[Anuncio]]


def _sopa(html: str):
    """Crea el objeto BeautifulSoup, con mensaje claro si falta la libreria."""
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise ScraperError(
            "Falta 'beautifulsoup4'. Instala con: pip install beautifulsoup4"
        ) from exc
    return BeautifulSoup(html, "html.parser")


def _anuncio_desde_texto(texto: str, fuente: str, url: str,
                         nombre: str = "") -> Anuncio:
    """Construye un Anuncio de scraping a partir de texto detectado."""
    limpio = parser.limpiar_texto(texto)
    return Anuncio(
        origen="scraping",
        fuente=fuente,
        url_original=url,
        nombre=nombre,
        especie=parser.detectar_especie(limpio),
        estado=parser.detectar_estado(limpio),
        distrito=parser.detectar_distrito(limpio),
        descripcion=limpio,
        tiene_recompensa=parser.detectar_recompensa(limpio),
    )


def extractor_petperu(html: str, url: str) -> list[Anuncio]:
    """
    Extractor para petperu.pe.

    El sitio coloca cada anuncio en un <div class="listing-details">, con
    el titulo en <h2 class="accordion-header"> y la descripcion en
    <div class="rtcl-listing-description">.
    """
    sopa = _sopa(html)
    anuncios: list[Anuncio] = []

    for bloque in sopa.find_all("div", class_="listing-details"):
        titulo_elem = bloque.find("h2", class_="accordion-header")
        titulo = titulo_elem.get_text(strip=True) if titulo_elem else ""
        if not titulo:
            continue

        desc_elem = bloque.find("div", class_="rtcl-listing-description")
        descripcion = (
            desc_elem.get_text(separator=" ", strip=True) if desc_elem else ""
        )

        texto = f"{titulo} {descripcion}"
        if len(texto) < 40:
            continue

        enlace = bloque.find("a", href=True)
        url_original = urljoin(url, enlace["href"]) if enlace else url

        anuncios.append(
            _anuncio_desde_texto(texto, "petperu.pe", url_original, titulo)
        )

    return anuncios


def extractor_generico(html: str, url: str) -> list[Anuncio]:
    """
    Extractor de ejemplo basado en bloques <article>.

    Sirve como plantilla. Muchos sitios usan <article> o contenedores con
    clases reconocibles. Para una fuente real, se copia esta funcion y se
    ajustan los selectores al HTML de ese sitio.
    """
    sopa = _sopa(html)
    anuncios: list[Anuncio] = []

    for bloque in sopa.find_all("article"):
        texto = bloque.get_text(separator=" ", strip=True)
        if len(texto) < 40:
            continue

        enlace = bloque.find("a", href=True)
        url_original = urljoin(url, enlace["href"]) if enlace else url

        encabezado = bloque.find(["h1", "h2", "h3"])
        titulo = encabezado.get_text(strip=True) if encabezado else ""

        anuncios.append(
            _anuncio_desde_texto(texto, "generico", url_original, titulo)
        )

    return anuncios


# Registro de extractores disponibles por nombre, para elegirlos facilmente.
EXTRACTORES: dict[str, Extractor] = {
    "petperu": extractor_petperu,
    "generico": extractor_generico,
}
