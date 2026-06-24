"""
Decoradores reutilizables para todo el proyecto.

    timer    mide y registra el tiempo de ejecucion de una funcion.
    retry    reintenta una funcion si lanza una excepcion.
    logged   registra la entrada y la salida de una funcion.

Se usan para anadir logging, medir tiempos y dar robustez sin
ensuciar la logica de cada funcion.
"""

from __future__ import annotations

import time
import logging
import functools
from typing import Callable, Type

log = logging.getLogger("patitas")


def timer(func: Callable) -> Callable:
    """Mide cuanto tarda la funcion y lo registra en el log."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            transcurrido = time.perf_counter() - inicio
            log.debug("%s tardo %.3f s", func.__name__, transcurrido)

    return wrapper


def retry(
    intentos: int = 3,
    espera: float = 2.0,
    excepciones: tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """
    Reintenta la funcion si lanza alguna de las excepciones indicadas.

    Parametros:
        intentos:    numero total de intentos antes de rendirse.
        espera:      segundos a esperar entre intentos.
        excepciones: tipos de excepcion que disparan un reintento.
    """

    def decorador(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ultimo_error: Exception | None = None
            for intento in range(1, intentos + 1):
                try:
                    return func(*args, **kwargs)
                except excepciones as exc:
                    ultimo_error = exc
                    log.warning(
                        "%s fallo (intento %d de %d): %s",
                        func.__name__, intento, intentos, exc,
                    )
                    if intento < intentos:
                        time.sleep(espera)
            raise ultimo_error  # type: ignore[misc]

        return wrapper

    return decorador


def logged(func: Callable) -> Callable:
    """Registra en el log cuando la funcion empieza y cuando termina."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        log.debug("inicio %s", func.__name__)
        resultado = func(*args, **kwargs)
        log.debug("fin %s", func.__name__)
        return resultado

    return wrapper
