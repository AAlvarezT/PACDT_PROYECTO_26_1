"""
Configuracion central del proyecto.

Toda la configuracion se lee desde variables de entorno, que en
desarrollo se cargan desde un archivo .env en la raiz del proyecto.
Asi las credenciales nunca quedan escritas en el codigo ni se suben
al repositorio (el .env esta en .gitignore).

Uso:
    from src.config import settings
    print(settings.supabase_url)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv es opcional; si no esta instalado se usan las
    # variables de entorno del sistema directamente.
    pass


def _lista(valor: str | None) -> list[str]:
    """Convierte una cadena 'a,b,c' en ['a', 'b', 'c'], sin vacios."""
    if not valor:
        return []
    return [item.strip() for item in valor.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    """Configuracion inmutable, cargada una sola vez al importar."""

    # Base de datos (Supabase)
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")

    # Datos de la marca, usados en mensajes de difusion
    nombre_app: str = os.getenv("NOMBRE_APP", "Patitas")
    url_publica: str = os.getenv("URL_PUBLICA", "https://patitas.streamlit.app")

    # Scraping
    scraper_user_agent: str = os.getenv(
        "SCRAPER_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36",
    )
    scraper_delay: float = float(os.getenv("SCRAPER_DELAY", "2.0"))
    scraper_timeout: float = float(os.getenv("SCRAPER_TIMEOUT", "10.0"))
    scraper_urls: list[str] = field(
        default_factory=lambda: _lista(os.getenv("SCRAPER_URLS"))
    )
    output_csv: str = os.getenv("OUTPUT_CSV", "data/raw/anuncios.csv")

    def validar_db(self) -> None:
        """Lanza ConfigError si faltan las credenciales de la base."""
        from src.utils.errors import ConfigError

        if not self.supabase_url or not self.supabase_key:
            raise ConfigError(
                "Faltan SUPABASE_URL o SUPABASE_KEY. "
                "Definelas en tu archivo .env."
            )


# Instancia unica que importa el resto del proyecto.
settings = Settings()
