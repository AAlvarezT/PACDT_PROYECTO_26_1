"""
Pruebas de la logica de los servicios.

Validan las partes que no dependen de la base de datos: validacion de
anuncios, construccion del mensaje de difusion, generacion de enlaces de
comparticion y calculo de indicadores. No requieren conexion a Supabase.

Ejecutar con:
    pytest tests/test_services.py -v
"""

import pytest

from src.models.anuncio import Anuncio
from src.services import anuncios_service, difusion_service, metrics_service
from src.utils.errors import ValidationError


def anuncio_valido() -> Anuncio:
    return Anuncio(
        origen="usuario",
        estado="perdido",
        especie="perro",
        nombre="Rocky",
        raza="Labrador",
        color="marron",
        distrito="Miraflores",
        descripcion="Collar rojo, muy amigable",
        contacto_telefono="999888777",
    )


# --- Validacion ------------------------------------------------------------

def test_validar_acepta_anuncio_completo():
    # No debe lanzar excepcion.
    anuncios_service.validar(anuncio_valido())


def test_validar_rechaza_sin_distrito():
    anuncio = anuncio_valido()
    anuncio.distrito = ""
    with pytest.raises(ValidationError):
        anuncios_service.validar(anuncio)


def test_validar_rechaza_sin_contacto():
    anuncio = anuncio_valido()
    anuncio.contacto_telefono = ""
    anuncio.contacto_email = ""
    with pytest.raises(ValidationError):
        anuncios_service.validar(anuncio)


def test_validar_rechaza_especie_invalida():
    anuncio = anuncio_valido()
    anuncio.especie = "dinosaurio"
    with pytest.raises(ValidationError):
        anuncios_service.validar(anuncio)


# --- Mensaje de difusion ---------------------------------------------------

def test_mensaje_incluye_datos_clave():
    mensaje = difusion_service.construir_mensaje(anuncio_valido())
    assert "Rocky" in mensaje
    assert "Miraflores" in mensaje
    assert "PERDIDA" in mensaje.upper()


def test_mensaje_de_encontrado_cambia_encabezado():
    anuncio = anuncio_valido()
    anuncio.estado = "encontrado"
    mensaje = difusion_service.construir_mensaje(anuncio)
    assert "ENCONTRADA" in mensaje.upper()


# --- Enlaces de comparticion -----------------------------------------------

def test_generar_enlaces_cubre_todos_los_canales():
    enlaces = difusion_service.generar_enlaces(anuncio_valido())
    for canal in difusion_service.CANALES:
        assert canal in enlaces
        assert enlaces[canal].startswith("http")


# --- Metricas --------------------------------------------------------------

def test_indicadores_calcula_tasa_de_reunion():
    anuncios = [
        anuncio_valido(),
        Anuncio(estado="reunido", especie="gato", distrito="Surco",
                descripcion="x", contacto_telefono="1"),
    ]
    df = metrics_service.anuncios_a_dataframe(anuncios)
    kpis = metrics_service.indicadores(df)
    assert kpis["total"] == 2
    assert kpis["reunidos"] == 1
    assert kpis["tasa_reunion"] == 50.0


def test_indicadores_con_dataframe_vacio():
    df = metrics_service.anuncios_a_dataframe([])
    kpis = metrics_service.indicadores(df)
    assert kpis["total"] == 0
    assert kpis["tasa_reunion"] == 0.0


def test_conteo_por_columna():
    anuncios = [
        Anuncio(especie="perro", estado="perdido", distrito="Surco",
                descripcion="x", contacto_telefono="1"),
        Anuncio(especie="perro", estado="perdido", distrito="Surco",
                descripcion="x", contacto_telefono="1"),
        Anuncio(especie="gato", estado="perdido", distrito="Surco",
                descripcion="x", contacto_telefono="1"),
    ]
    df = metrics_service.anuncios_a_dataframe(anuncios)
    conteo = metrics_service.conteo_por_columna(df, "especie")
    fila_perro = conteo[conteo["especie"] == "perro"]["cantidad"].iloc[0]
    assert fila_perro == 2


# --- Validacion de imagenes ------------------------------------------------

def test_validar_imagen_acepta_jpg():
    from src.database import storage
    extension = storage.validar_imagen(b"contenido", "image/jpeg")
    assert extension == "jpg"


def test_validar_imagen_rechaza_tipo_no_permitido():
    from src.database import storage
    with pytest.raises(ValidationError):
        storage.validar_imagen(b"contenido", "application/pdf")


def test_validar_imagen_rechaza_archivo_muy_grande():
    from src.database import storage
    grande = b"x" * (storage.TAMANO_MAXIMO + 1)
    with pytest.raises(ValidationError):
        storage.validar_imagen(grande, "image/png")
