"""
Verificacion de la conexion a Supabase.

Comprueba que las credenciales del .env funcionan y que las tablas
existen y son accesibles. Util para confirmar el setup antes de usar la
aplicacion.

Uso:
    python -m src.database.check_connection
"""

from __future__ import annotations

import sys
import logging

from src.database.connection import get_client
from src.utils.errors import PatitasError


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    log = logging.getLogger("patitas")

    try:
        client = get_client()
        anuncios = client.table("anuncios").select("id", count="exact").execute()
        difusiones = (
            client.table("difusiones").select("id", count="exact").execute()
        )
        log.info("Conexion correcta.")
        log.info("  anuncios:   %s filas", anuncios.count)
        log.info("  difusiones: %s filas", difusiones.count)
        log.info("Todo listo para usar la aplicacion.")
        return 0
    except PatitasError as exc:
        log.error("No se pudo conectar o leer las tablas: %s", exc)
        log.error(
            "Revisa que el .env tenga las credenciales y que hayas aplicado "
            "src/database/schema.sql en Supabase."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
