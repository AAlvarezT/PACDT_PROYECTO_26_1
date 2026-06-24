"""
Servicio de difusion.

Genera el contenido para compartir un anuncio en redes sociales y
registra cada difusion en la base. No usa las APIs oficiales de las
redes (que son de pago o requieren aprobacion); en su lugar construye
enlaces de comparticion, que abren la red con el mensaje ya preparado y
no necesitan credenciales.

Canales soportados: WhatsApp, Facebook, X (Twitter) y Telegram.
"""

from __future__ import annotations

import io
import logging
from urllib.parse import quote

from src.config import settings
from src.database.connection import get_client
from src.models.anuncio import Anuncio
from src.utils.decorators import timer
from src.utils.errors import DatabaseError

log = logging.getLogger("patitas")

TABLA = "difusiones"
CANALES = ("whatsapp", "facebook", "x", "telegram")


def construir_mensaje(anuncio: Anuncio) -> str:
    """
    Arma un mensaje claro y listo para publicar a partir de un anuncio.

    El mensaje resume lo esencial para que alguien que lo vea en una red
    pueda reconocer a la mascota y saber a quien avisar.
    """
    if anuncio.estado == "encontrado":
        encabezado = "MASCOTA ENCONTRADA"
    else:
        encabezado = "SE BUSCA MASCOTA PERDIDA"

    partes = [encabezado]

    descripcion_mascota = " ".join(
        p for p in (
            anuncio.especie.capitalize(),
            anuncio.raza,
            anuncio.color,
        ) if p
    ).strip()
    if anuncio.nombre:
        descripcion_mascota = f"{anuncio.nombre} ({descripcion_mascota})"
    if descripcion_mascota:
        partes.append(descripcion_mascota)

    if anuncio.distrito:
        ubicacion = anuncio.distrito
        if anuncio.referencia_lugar:
            ubicacion += f", cerca de {anuncio.referencia_lugar}"
        partes.append(f"Zona: {ubicacion}")

    if anuncio.tiene_recompensa:
        if anuncio.monto_recompensa:
            partes.append(f"Recompensa: S/ {anuncio.monto_recompensa:.0f}")
        else:
            partes.append("Se ofrece recompensa")

    contacto = anuncio.contacto_telefono or anuncio.contacto_email
    if contacto:
        partes.append(f"Contacto: {contacto}")

    partes.append(f"Publicado en {settings.nombre_app}")
    return "\n".join(partes)


def enlace_anuncio(anuncio: Anuncio) -> str:
    """
    Devuelve el enlace publico que acompana a la mascota.

    Si el anuncio proviene de un sitio externo, usa su enlace original.
    En otro caso, apunta a la plataforma.
    """
    if anuncio.url_original:
        return anuncio.url_original
    return settings.url_publica


def generar_enlaces(anuncio: Anuncio) -> dict[str, str]:
    """
    Construye los enlaces de comparticion para cada red social.

    Devuelve un diccionario {canal: url}. Abrir cualquiera de estas URLs
    abre la red correspondiente con el mensaje y el enlace ya cargados.
    """
    mensaje = construir_mensaje(anuncio)
    url = enlace_anuncio(anuncio)
    texto = quote(mensaje)
    enlace = quote(url, safe="")

    return {
        "whatsapp": f"https://wa.me/?text={quote(mensaje + ' ' + url)}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={enlace}",
        "x": f"https://twitter.com/intent/tweet?text={texto}&url={enlace}",
        "telegram": f"https://t.me/share/url?url={enlace}&text={texto}",
    }


def generar_qr(anuncio: Anuncio) -> bytes:
    """
    Genera un codigo QR (PNG) que enlaza al anuncio.

    Sirve para imprimir carteles fisicos: quien escanea el QR llega al
    anuncio en linea. Devuelve los bytes de la imagen.
    """
    try:
        import qrcode
    except ImportError as exc:
        raise RuntimeError(
            "Falta la dependencia 'qrcode'. Instala con: pip install qrcode[pil]"
        ) from exc

    imagen = qrcode.make(enlace_anuncio(anuncio))
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    return buffer.getvalue()


@timer
def registrar_difusion(anuncio_id: str, canal: str) -> None:
    """
    Registra en la base que un anuncio se compartio por un canal.

    Estos registros alimentan el panel de analisis (que canal difunde
    mas, que anuncios se comparten mas).
    """
    if canal not in CANALES:
        log.warning("Canal de difusion no reconocido: %s", canal)
    client = get_client()
    try:
        client.table(TABLA).insert(
            {"anuncio_id": anuncio_id, "canal": canal}
        ).execute()
        log.info("Difusion registrada: anuncio %s por %s.", anuncio_id, canal)
    except Exception as exc:
        raise DatabaseError(f"No se pudo registrar la difusion: {exc}") from exc


@timer
def listar_difusiones(limite: int = 1000) -> list[dict]:
    """Devuelve las difusiones registradas, para el analisis."""
    client = get_client()
    try:
        respuesta = (
            client.table(TABLA)
            .select("*")
            .order("fecha_difusion", desc=True)
            .limit(limite)
            .execute()
        )
        return respuesta.data or []
    except Exception as exc:
        raise DatabaseError(f"No se pudieron listar las difusiones: {exc}") from exc
