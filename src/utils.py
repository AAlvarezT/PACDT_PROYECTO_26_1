"""
utils.py
Utilidades transversales del proyecto: configuración de logging y
decoradores reutilizables para instrumentación (timing/debug) y
manejo de errores en procesamiento y visualización.

Este módulo se agrega en la entrega final para cubrir el requisito de
"decoradores para logging/tiempos/debug" y centralizar el manejo de
errores en lugar de repetir try/except sueltos por todo el código.
"""

import functools
import logging
import time
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Stopwords en español (compartidas entre viz.py -nube de palabras- y
# topics.py -TF-IDF para topic modeling-)
# ---------------------------------------------------------------------------

STOPWORDS_ES = {
    "de", "la", "el", "en", "y", "a", "con", "sin", "del",
    "los", "las", "se", "por", "que", "su", "un", "una", "al",
    "lo", "le", "les", "no", "es", "era", "fue", "han", "hay",
    "para", "como", "pero", "más", "sobre", "entre", "hasta",
    "desde", "cuando", "donde", "quien", "cuya", "cuyo", "xxxxx",
}

# ---------------------------------------------------------------------------
# Configuración de logging
# ---------------------------------------------------------------------------
# Se escribe a consola siempre, y a un archivo app.log si el entorno lo
# permite. En algunos despliegues en la nube el filesystem puede ser de
# solo lectura, así que el FileHandler se intenta de forma defensiva.

LOG_PATH = Path(__file__).resolve().parent.parent / "app.log"

_handlers = [logging.StreamHandler()]
try:
    _handlers.append(logging.FileHandler(LOG_PATH, encoding="utf-8"))
except OSError:
    # Entorno sin permisos de escritura: se sigue logueando a consola.
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    handlers=_handlers,
    force=True,  # evita handlers duplicados si Streamlit re-ejecuta el módulo
)

logger = logging.getLogger("reniped")


# ---------------------------------------------------------------------------
# Decorador 1 — logging + tiempos de ejecución
# ---------------------------------------------------------------------------

def log_step(func):
    """
    Decorador para funciones de procesamiento (carga, limpieza, KPIs).

    Registra: inicio, duración, y -si el resultado es un DataFrame o una
    tupla que empieza con uno- su shape. Si la función lanza una excepción,
    la registra con traceback completo y la vuelve a lanzar (no la oculta:
    quien llama decide cómo manejarla, p. ej. con st.error en app.py).
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("→ Iniciando '%s'", func.__name__)
        t0 = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        except Exception:
            elapsed = time.perf_counter() - t0
            logger.exception("✗ '%s' falló tras %.3fs", func.__name__, elapsed)
            raise

        elapsed = time.perf_counter() - t0
        if isinstance(result, pd.DataFrame):
            logger.info("✓ '%s' OK en %.3fs — shape=%s", func.__name__, elapsed, result.shape)
        elif isinstance(result, tuple) and result and isinstance(result[0], pd.DataFrame):
            logger.info("✓ '%s' OK en %.3fs — shape=%s", func.__name__, elapsed, result[0].shape)
        else:
            logger.info("✓ '%s' OK en %.3fs", func.__name__, elapsed)
        return result
    return wrapper


# ---------------------------------------------------------------------------
# Decorador 2 — blindaje de funciones de graficación
# ---------------------------------------------------------------------------

def safe_plot(fallback_title: str = "No se pudo generar el gráfico", as_none: bool = False):
    """
    Decorador parametrizado para las funciones de viz.py.

    Si la función decorada lanza una excepción (columna ausente, datos
    vacíos tras filtrar, tipo inesperado, etc.), se registra el error
    con traceback y se devuelve un resultado de respaldo en vez de
    romper todo el dashboard con un traceback de Streamlit:

    - as_none=False (default): retorna una go.Figure vacía con el
      título de error visible (para funciones Plotly).
    - as_none=True: retorna None (para plot_wordcloud, que ya maneja
      el caso None mostrando un st.info en app.py).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception("✗ Error en '%s': %s", func.__name__, e)
                if as_none:
                    return None
                fig = go.Figure()
                fig.update_layout(
                    title=f"⚠️ {fallback_title}<br><sub>{type(e).__name__}: {str(e)[:90]}</sub>",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                return fig
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Validación reutilizable de columnas requeridas
# ---------------------------------------------------------------------------

def require_columns(df: pd.DataFrame, columns: list[str], context: str = "") -> None:
    """
    Lanza ValueError con un mensaje claro si faltan columnas esperadas en df.
    Se llama al inicio de las funciones de processing.py antes de operar,
    para fallar rápido y con un mensaje legible en vez de un KeyError
    críptico a mitad de una transformación.
    """
    faltantes = [c for c in columns if c not in df.columns]
    if faltantes:
        raise ValueError(
            f"Columnas faltantes{f' en {context}' if context else ''}: {faltantes}"
        )
