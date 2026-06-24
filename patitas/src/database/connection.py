"""
Conexion a Supabase.

Crea un unico cliente de Supabase para todo el proyecto, leyendo las
credenciales desde la configuracion central. El cliente se crea la
primera vez que se solicita y se reutiliza despues.
"""

from __future__ import annotations

import logging

from src.config import settings
from src.utils.errors import DatabaseError

log = logging.getLogger("patitas")

_cliente = None


def get_client():
    """
    Devuelve el cliente de Supabase, creandolo si aun no existe.

    Lanza:
        ConfigError   si faltan las credenciales en el .env.
        DatabaseError si la libreria no esta instalada o falla la conexion.
    """
    global _cliente
    if _cliente is not None:
        return _cliente

    settings.validar_db()  # lanza ConfigError si faltan URL o KEY

    try:
        from supabase import create_client
    except ImportError as exc:
        raise DatabaseError(
            "Falta la dependencia 'supabase'. "
            "Instala con: pip install supabase"
        ) from exc

    try:
        _cliente = create_client(settings.supabase_url, settings.supabase_key)
        log.info("Cliente de Supabase inicializado.")
        return _cliente
    except Exception as exc:
        raise DatabaseError(f"No se pudo conectar a Supabase: {exc}") from exc
