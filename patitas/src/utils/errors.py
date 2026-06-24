"""
Excepciones propias del proyecto.

Centralizar las excepciones permite que cada capa lance un error
descriptivo y que las capas superiores decidan como reaccionar:
reintentar, registrar en el log o mostrar un mensaje al usuario.
"""


class PatitasError(Exception):
    """Excepcion base. Todas las demas heredan de esta."""


class ConfigError(PatitasError):
    """Falta una variable de configuracion o tiene un valor invalido."""


class DatabaseError(PatitasError):
    """Error al conectar o consultar la base de datos."""


class ScraperError(PatitasError):
    """Error durante la descarga o lectura de una pagina externa."""


class ValidationError(PatitasError):
    """Los datos de un anuncio no cumplen las reglas minimas."""
