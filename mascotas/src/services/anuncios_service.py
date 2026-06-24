"""
Servicio de anuncios.

Contiene la logica de negocio para crear, listar, filtrar y actualizar
anuncios. Las paginas de Streamlit y el scraper usan estas funciones y
nunca hablan con la base de datos directamente. Asi, si cambia la forma
de almacenar los datos, solo se modifica esta capa.
"""

from __future__ import annotations

import logging
from typing import Sequence

from src.database.connection import get_client
from src.models.anuncio import Anuncio, ESPECIES, ESTADOS
from src.utils.decorators import timer
from src.utils.errors import DatabaseError, ValidationError

log = logging.getLogger("patitas")

TABLA = "anuncios"


def validar(anuncio: Anuncio) -> None:
    """
    Verifica que un anuncio cumpla las reglas minimas antes de guardarlo.

    Lanza ValidationError con un mensaje claro si algo falta o es invalido.
    """
    if anuncio.especie not in ESPECIES:
        raise ValidationError(
            f"Especie invalida: {anuncio.especie!r}. "
            f"Debe ser una de {ESPECIES}."
        )
    if anuncio.estado not in ESTADOS:
        raise ValidationError(
            f"Estado invalido: {anuncio.estado!r}. "
            f"Debe ser uno de {ESTADOS}."
        )
    if not anuncio.distrito.strip():
        raise ValidationError("El distrito es obligatorio.")
    if not anuncio.descripcion.strip():
        raise ValidationError("La descripcion es obligatoria.")
    # Si es un anuncio de usuario, debe haber al menos un medio de contacto.
    if anuncio.origen == "usuario":
        tiene_contacto = bool(
            anuncio.contacto_telefono.strip()
            or anuncio.contacto_email.strip()
        )
        if not tiene_contacto:
            raise ValidationError(
                "Indica al menos un telefono o un correo de contacto."
            )


@timer
def crear_anuncio(anuncio: Anuncio) -> dict:
    """
    Valida y guarda un anuncio nuevo. Devuelve la fila creada.

    Lanza ValidationError si los datos no son validos, o DatabaseError si
    falla la insercion.
    """
    validar(anuncio)
    client = get_client()
    try:
        respuesta = client.table(TABLA).insert(anuncio.to_dict()).execute()
        fila = (respuesta.data or [{}])[0]
        log.info("Anuncio creado (%s, %s).", anuncio.especie, anuncio.distrito)
        return fila
    except Exception as exc:
        raise DatabaseError(f"No se pudo crear el anuncio: {exc}") from exc


@timer
def guardar_varios(anuncios: Sequence[Anuncio]) -> int:
    """
    Inserta varios anuncios de una vez (usado por el scraper).

    Usa upsert sobre url_original: si un anuncio externo ya existe, lo
    actualiza en lugar de duplicarlo. Devuelve cuantos se enviaron.
    """
    if not anuncios:
        return 0
    client = get_client()
    filas = [a.to_dict() for a in anuncios]
    try:
        client.table(TABLA).upsert(filas, on_conflict="url_original").execute()
        log.info("Guardados %d anuncios externos.", len(filas))
        return len(filas)
    except Exception as exc:
        raise DatabaseError(f"No se pudieron guardar los anuncios: {exc}") from exc


@timer
def listar_anuncios(
    estado: str | None = None,
    especie: str | None = None,
    distrito: str | None = None,
    texto: str | None = None,
    limite: int = 200,
) -> list[Anuncio]:
    """
    Devuelve anuncios de la base, con filtros opcionales.

    Parametros:
        estado, especie, distrito: filtran por igualdad exacta (None = todos).
        texto:  busca el termino en el nombre, la raza o la descripcion.
        limite: numero maximo de anuncios a devolver.
    """
    client = get_client()
    try:
        consulta = client.table(TABLA).select("*")
        if estado:
            consulta = consulta.eq("estado", estado)
        if especie:
            consulta = consulta.eq("especie", especie)
        if distrito:
            consulta = consulta.eq("distrito", distrito)
        if texto:
            # Busca el texto en varias columnas (insensible a mayusculas).
            patron = f"%{texto}%"
            consulta = consulta.or_(
                f"nombre.ilike.{patron},"
                f"raza.ilike.{patron},"
                f"descripcion.ilike.{patron}"
            )
        respuesta = (
            consulta.order("fecha_publicacion", desc=True)
            .limit(limite)
            .execute()
        )
        return [Anuncio.from_dict(fila) for fila in (respuesta.data or [])]
    except Exception as exc:
        raise DatabaseError(f"No se pudieron listar los anuncios: {exc}") from exc


@timer
def cambiar_estado(anuncio_id: str, nuevo_estado: str) -> None:
    """
    Actualiza el estado de un anuncio (por ejemplo, marcarlo como reunido).

    Lanza ValidationError si el estado no es valido.
    """
    if nuevo_estado not in ESTADOS:
        raise ValidationError(f"Estado invalido: {nuevo_estado!r}.")
    client = get_client()
    try:
        client.table(TABLA).update({"estado": nuevo_estado}).eq(
            "id", anuncio_id
        ).execute()
        log.info("Anuncio %s actualizado a estado %s.", anuncio_id, nuevo_estado)
    except Exception as exc:
        raise DatabaseError(f"No se pudo actualizar el estado: {exc}") from exc
