"""
Almacenamiento de fotos en Supabase Storage.

Las fotos de las mascotas no se guardan como bytes dentro de la tabla,
sino en Supabase Storage (el almacenamiento de archivos del proyecto).
La tabla 'anuncios' guarda solo la URL publica de la foto. Esta es la
practica recomendada: mantiene la base ligera y las consultas rapidas.

Flujo:
    1. El usuario sube una imagen desde el formulario.
    2. Se valida tipo y tamano.
    3. Se sube al bucket con un nombre unico.
    4. Se devuelve la URL publica, que se guarda en el anuncio.
"""

from __future__ import annotations

import logging
import uuid

from src.database.connection import get_client
from src.utils.decorators import timer
from src.utils.errors import DatabaseError, ValidationError

log = logging.getLogger("patitas")

BUCKET = "fotos-mascotas"

# Tipos de imagen permitidos y su extension de archivo.
TIPOS_PERMITIDOS = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}

# Tamano maximo permitido por foto (5 MB).
TAMANO_MAXIMO = 5 * 1024 * 1024


def validar_imagen(contenido: bytes, tipo_mime: str) -> str:
    """
    Verifica que la imagen sea de un tipo permitido y no exceda el tamano.

    Devuelve la extension de archivo correspondiente al tipo.
    Lanza ValidationError si la imagen no es valida.
    """
    if tipo_mime not in TIPOS_PERMITIDOS:
        raise ValidationError(
            "Formato de imagen no permitido. Usa JPG, PNG o WEBP."
        )
    if len(contenido) > TAMANO_MAXIMO:
        raise ValidationError(
            "La imagen pesa mas de 5 MB. Usa una mas liviana."
        )
    return TIPOS_PERMITIDOS[tipo_mime]


@timer
def subir_foto(contenido: bytes, tipo_mime: str) -> str:
    """
    Sube una foto al bucket y devuelve su URL publica.

    Genera un nombre unico para evitar colisiones. Lanza ValidationError
    si la imagen no es valida, o DatabaseError si falla la subida.
    """
    extension = validar_imagen(contenido, tipo_mime)
    nombre = f"{uuid.uuid4().hex}.{extension}"

    client = get_client()
    try:
        client.storage.from_(BUCKET).upload(
            path=nombre,
            file=contenido,
            file_options={"content-type": tipo_mime, "upsert": "false"},
        )
        url = client.storage.from_(BUCKET).get_public_url(nombre)
        log.info("Foto subida a Storage: %s", nombre)
        return url
    except Exception as exc:
        raise DatabaseError(f"No se pudo subir la foto: {exc}") from exc
