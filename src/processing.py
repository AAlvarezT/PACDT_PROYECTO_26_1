"""
processing.py
Carga, limpieza documentada y métricas descriptivas del dataset RENIPED.

Manejo de errores (entrega final):
- load_data valida existencia del archivo, formato CSV y columnas
  mínimas esperadas ANTES de transformar nada, lanzando excepciones con
  mensajes legibles (FileNotFoundError / ValueError) en vez de dejar que
  un KeyError críptico aparezca a mitad de una transformación.
- clean_data y get_summary validan sus columnas requeridas con
  require_columns() y registran advertencias (sin tumbar la app) cuando
  una columna categórica no es texto.

Decoradores (entrega final):
- @log_step (definido en utils.py) instrumenta tiempos de ejecución y
  resultado de las tres funciones públicas de este módulo.
"""

import numpy as np
import pandas as pd
from pathlib import Path

from utils import log_step, logger, require_columns

# Bounding box aproximado del territorio peruano
PERU_LAT = (-18.5, -0.5)
PERU_LON = (-81.5, -68.5)

# Columnas mínimas que debe traer data_raw.csv para que el resto del
# pipeline (limpieza, KPIs, gráficos) tenga sentido.
REQUIRED_RAW_COLUMNS = [
    "Nombres", "EDAD", "Aparecido",
    "Fecha Denuncia", "Fecha Hecho", "Fecha de Aparición", "Fecha Nacimiento",
    "Lugar Hecho", "Horas para Aparecer", "Horas para Denunciar",
    "Latitud", "Longitud",
]


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------

@log_step
def load_data(path: str | Path) -> pd.DataFrame:
    """
    Lee data_raw.csv y aplica transformaciones de tipo básicas:
    - Parseo de fechas (dos formatos distintos en el dataset)
    - Derivación de columna 'region' a partir de 'Lugar Hecho'
    - Columnas auxiliares de año y mes para series temporales

    Parameters
    ----------
    path : str | Path
        Ruta al archivo data_raw.csv.

    Returns
    -------
    pd.DataFrame

    Raises
    ------
    FileNotFoundError
        Si `path` no existe.
    ValueError
        Si el archivo está vacío, no es un CSV legible, o le faltan
        columnas mínimas requeridas (REQUIRED_RAW_COLUMNS).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de datos en: {path}")

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError as e:
        raise ValueError(f"El archivo '{path.name}' está vacío.") from e
    except pd.errors.ParserError as e:
        raise ValueError(f"El archivo '{path.name}' no es un CSV válido: {e}") from e

    require_columns(df, REQUIRED_RAW_COLUMNS, context="data_raw.csv")

    # Fechas en formato ISO (YYYY-MM-DD)
    for col in ["Fecha Denuncia", "Fecha Hecho", "Fecha de Aparición"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Fecha de nacimiento en formato DD/MM/YYYY
    df["Fecha Nacimiento"] = pd.to_datetime(
        df["Fecha Nacimiento"], format="%d/%m/%Y", errors="coerce"
    )

    # Extracción de región: primer segmento de 'Lugar Hecho'
    # Formato original: "REGION-PROVINCIA-DISTRITO- DIRECCION"
    try:
        df["region"] = (
            df["Lugar Hecho"]
            .str.split("-")
            .str[0]
            .str.strip()
            .str.title()
        )
    except AttributeError as e:
        # 'Lugar Hecho' no es texto en algún caso inesperado: no detenemos
        # la carga completa por esto, dejamos 'region' vacía y avisamos.
        logger.warning("No se pudo derivar 'region' desde 'Lugar Hecho': %s", e)
        df["region"] = np.nan

    # Forzar numérico en columnas que pueden venir como string
    for col in ["Horas para Aparecer", "Horas para Denunciar", "Latitud", "Longitud", "EDAD"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Auxiliares temporales para las series
    df["anio_hecho"] = df["Fecha Hecho"].dt.year
    df["mes_hecho"] = df["Fecha Hecho"].dt.to_period("M").dt.to_timestamp()

    return df


# ---------------------------------------------------------------------------
# Limpieza documentada
# ---------------------------------------------------------------------------

@log_step
def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Aplica las transformaciones de limpieza documentadas sobre el dataset.

    Pasos:
    1. Eliminación de registros duplicados.
    2. Anulación de valores negativos en 'Horas para Aparecer' (→ NaN).
    3. Anulación de coordenadas fuera del territorio peruano (→ NaN).
    4. Estandarización de variables categóricas físicas.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame cargado con load_data().

    Returns
    -------
    tuple[pd.DataFrame, dict]
        DataFrame limpio y diccionario con métricas del proceso de limpieza.

    Raises
    ------
    ValueError
        Si faltan columnas indispensables para poder limpiar (p. ej. si
        se llama sobre un DataFrame que no pasó por load_data()).
    """
    require_columns(df, ["Horas para Aparecer", "Latitud", "Longitud"], context="clean_data")

    report = {}
    df = df.copy()

    # 1. Duplicados
    n_antes = len(df)
    df = df.drop_duplicates()
    report["duplicados_eliminados"] = n_antes - len(df)

    # 2. Horas para Aparecer negativas
    # Valores negativos indican inconsistencias en el registro de fechas.
    # Se anula el campo (NaN) sin eliminar la fila, ya que el resto de
    # variables del registro siguen siendo válidas.
    neg_mask = df["Horas para Aparecer"] < 0
    report["horas_aparecer_negativas"] = int(neg_mask.sum())
    df.loc[neg_mask, "Horas para Aparecer"] = np.nan

    # 3. Coordenadas fuera de Perú
    # Los registros afectados conservan toda su información salvo Lat/Lon.
    bad_lat = (df["Latitud"] < PERU_LAT[0]) | (df["Latitud"] > PERU_LAT[1])
    bad_lon = (df["Longitud"] < PERU_LON[0]) | (df["Longitud"] > PERU_LON[1])
    bad_coords = bad_lat | bad_lon
    report["coordenadas_invalidas"] = int(bad_coords.sum())
    df.loc[bad_coords, ["Latitud", "Longitud"]] = np.nan

    # 4. Estandarización de categóricas físicas
    cat_cols = ["Tez", "Fenotipo", "Ojos", "Sangre", "Boca", "Nariz", "Cabello", "Contextura"]
    for col in cat_cols:
        if col not in df.columns:
            continue
        try:
            df[col] = df[col].str.title().str.strip()
            df[col] = df[col].replace("Sin Información", np.nan)
        except AttributeError as e:
            # Columna presente pero no es texto (p. ej. vino numérica): se
            # registra y se sigue, en vez de tumbar toda la limpieza.
            logger.warning("Columna '%s' no pudo estandarizarse como texto: %s", col, e)

    report["registros_finales"] = len(df)
    logger.info("Reporte de limpieza: %s", report)
    return df, report


# ---------------------------------------------------------------------------
# Métricas descriptivas
# ---------------------------------------------------------------------------

@log_step
def get_summary(df: pd.DataFrame) -> dict:
    """
    Calcula los KPIs principales del dataset filtrado.

    Returns
    -------
    dict con claves:
        total, pct_aparecidos, pct_menores, mediana_horas_denuncia

    Raises
    ------
    ValueError
        Si faltan columnas indispensables para calcular los KPIs.
    """
    require_columns(df, ["Aparecido", "EDAD", "Horas para Denunciar"], context="get_summary")

    total = len(df)
    if total == 0:
        return {
            "total": 0,
            "pct_aparecidos": 0.0,
            "pct_menores": 0.0,
            "mediana_horas_denuncia": 0.0,
        }

    mediana_horas = df["Horas para Denunciar"].median()

    return {
        "total": total,
        "pct_aparecidos": round(df["Aparecido"].sum() / total * 100, 1),
        "pct_menores": round((df["EDAD"] < 18).sum() / total * 100, 1),
        # Si en el subconjunto filtrado no hay ninguna hora válida, median()
        # da NaN: se reporta 0.0 en vez de mostrar "nan h" en el KPI.
        "mediana_horas_denuncia": round(mediana_horas, 1) if pd.notna(mediana_horas) else 0.0,
    }
