"""
Punto de entrada del scraping.

Ejecuta el flujo completo:

    sitios publicos -> scraper -> base de datos (tabla anuncios)

1. Lee las URLs configuradas en el .env (SCRAPER_URLS).
2. Las scrapea con el extractor elegido.
3. Guarda los anuncios en Supabase, marcados con origen 'scraping'.

Uso:
    python -m src.integrations.run_scraper

Antes de ejecutar:
    1. pip install -r requirements.txt
    2. Completa SCRAPER_URLS en el .env con sitios publicos.
    3. Aplica el esquema src/database/schema.sql en Supabase.

El extractor por defecto es el de petperu.pe. Para otro sitio, cambia el
nombre en la variable EXTRACTOR_POR_DEFECTO o crea un extractor nuevo en
src/integrations/extractors.py.
"""

from __future__ import annotations

import sys
import logging

from src.config import settings
from src.integrations.extractors import EXTRACTORES
from src.integrations.scraper import scrapear_todos
from src.services.anuncios_service import guardar_varios
from src.utils.errors import PatitasError

EXTRACTOR_POR_DEFECTO = "petperu"


def configurar_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> int:
    configurar_logging()
    log = logging.getLogger("patitas")

    if not settings.scraper_urls:
        log.error(
            "No hay URLs configuradas. Define SCRAPER_URLS en tu archivo .env."
        )
        return 1

    extractor = EXTRACTORES[EXTRACTOR_POR_DEFECTO]

    try:
        anuncios = scrapear_todos(settings.scraper_urls, extractor)
        if not anuncios:
            log.warning(
                "No se obtuvieron anuncios relevantes. Revisa las URLs o el "
                "extractor para el sitio."
            )
            return 0

        guardados = guardar_varios(anuncios)
        log.info("Anuncios guardados en la base: %d", guardados)
        log.info("Flujo completado.")
        return 0

    except PatitasError as exc:
        log.error("Fallo el proceso: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
