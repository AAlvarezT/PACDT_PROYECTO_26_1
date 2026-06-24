"""
Scraper de sitios publicos.

Descarga paginas publicas (sin iniciar sesion) y aplica un extractor
para obtener los anuncios. Maneja los errores de red sin abortar todo el
proceso: si una URL falla, registra el error y continua con las demas.

Antes de scrapear un sitio, revisa su archivo /robots.txt y sus terminos
de uso. Este modulo asume que las URLs configuradas corresponden a
sitios que permiten el acceso automatizado.
"""

from __future__ import annotations

import logging
from typing import Iterable

from src.config import settings
from src.integrations.extractors import Extractor
from src.integrations import parser
from src.models.anuncio import Anuncio
from src.utils.decorators import timer, retry
from src.utils.errors import ScraperError

log = logging.getLogger("patitas")


@retry(intentos=3, espera=settings.scraper_delay, excepciones=(ScraperError,))
def descargar(url: str) -> str:
    """
    Descarga el HTML de una URL publica.

    Reintenta hasta tres veces ante fallos de red. Lanza ScraperError si
    no logra obtener la pagina.
    """
    try:
        import requests
    except ImportError as exc:
        raise ScraperError(
            "Falta 'requests'. Instala con: pip install requests"
        ) from exc

    try:
        respuesta = requests.get(
            url,
            headers={"User-Agent": settings.scraper_user_agent},
            timeout=settings.scraper_timeout,
        )
        respuesta.raise_for_status()
        return respuesta.text
    except requests.RequestException as exc:
        raise ScraperError(f"No se pudo descargar {url}: {exc}") from exc


@timer
def scrapear_sitio(url: str, extractor: Extractor) -> list[Anuncio]:
    """
    Descarga una URL y aplica su extractor para obtener anuncios.

    Devuelve solo los anuncios relevantes (los que parecen de mascotas
    perdidas o encontradas). Si la descarga falla, registra el error y
    devuelve una lista vacia en vez de abortar.
    """
    try:
        html = descargar(url)
    except ScraperError as exc:
        log.error("Se omite %s: %s", url, exc)
        return []

    anuncios = extractor(html, url)
    relevantes = [
        a for a in anuncios
        if parser.es_relevante(f"{a.nombre} {a.descripcion}")
    ]
    log.info("%s: %d anuncios, %d relevantes", url, len(anuncios), len(relevantes))
    return relevantes


@timer
def scrapear_todos(urls: Iterable[str], extractor: Extractor) -> list[Anuncio]:
    """
    Recorre varias URLs con el mismo extractor y junta los resultados.

    Pensado para varias URLs del mismo sitio. Para sitios distintos, se
    llama una vez por sitio con su extractor correspondiente.
    """
    resultados: list[Anuncio] = []
    for url in urls:
        resultados.extend(scrapear_sitio(url, extractor))
    log.info("Total de anuncios relevantes: %d", len(resultados))
    return resultados
