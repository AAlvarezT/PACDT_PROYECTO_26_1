"""
processing.py
Carga, limpieza documentada y métricas descriptivas del dataset RENIPED.
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Bounding box aproximado del territorio peruano
PERU_LAT = (-18.5, -0.5)
PERU_LON = (-81.5, -68.5)


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------

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
    """
    df = pd.read_csv(path)

    # Fechas en formato ISO (YYYY-MM-DD)
    df["Fecha Denuncia"]    = pd.to_datetime(df["Fecha Denuncia"],    errors="coerce")
    df["Fecha Hecho"]       = pd.to_datetime(df["Fecha Hecho"],       errors="coerce")
    df["Fecha de Aparición"]= pd.to_datetime(df["Fecha de Aparición"],errors="coerce")

    # Fecha de nacimiento en formato DD/MM/YYYY
    df["Fecha Nacimiento"] = pd.to_datetime(
        df["Fecha Nacimiento"], format="%d/%m/%Y", errors="coerce"
    )

    # Extracción de región: primer segmento de 'Lugar Hecho'
    # Formato original: "REGION-PROVINCIA-DISTRITO- DIRECCION"
    df["region"] = (
        df["Lugar Hecho"]
        .str.split("-")
        .str[0]
        .str.strip()
        .str.title()
    )

    # Forzar numérico en columnas de horas (pueden venir como string)
    df["Horas para Aparecer"]   = pd.to_numeric(df["Horas para Aparecer"],   errors="coerce")
    df["Horas para Denunciar"]  = pd.to_numeric(df["Horas para Denunciar"],  errors="coerce")
    df["Latitud"]               = pd.to_numeric(df["Latitud"],               errors="coerce")
    df["Longitud"]              = pd.to_numeric(df["Longitud"],              errors="coerce")
    df["EDAD"]                  = pd.to_numeric(df["EDAD"],                  errors="coerce")

    # Auxiliares temporales para las series
    df["anio_hecho"] = df["Fecha Hecho"].dt.year
    df["mes_hecho"]  = df["Fecha Hecho"].dt.to_period("M").dt.to_timestamp()

    return df


# ---------------------------------------------------------------------------
# Limpieza documentada
# ---------------------------------------------------------------------------

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
    """
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
        if col in df.columns:
            df[col] = df[col].str.title().str.strip()
            df[col] = df[col].replace("Sin Información", np.nan)

    report["registros_finales"] = len(df)
    return df, report


# ---------------------------------------------------------------------------
# Métricas descriptivas
# ---------------------------------------------------------------------------

def get_summary(df: pd.DataFrame) -> dict:
    """
    Calcula los KPIs principales del dataset filtrado.

    Returns
    -------
    dict con claves:
        total, pct_aparecidos, pct_menores, mediana_horas_denuncia
    """
    total = len(df)
    if total == 0:
        return {
            "total": 0,
            "pct_aparecidos": 0.0,
            "pct_menores": 0.0,
            "mediana_horas_denuncia": 0.0,
        }

    return {
        "total": total,
        "pct_aparecidos": round(df["Aparecido"].sum() / total * 100, 1),
        "pct_menores": round((df["EDAD"] < 18).sum() / total * 100, 1),
        "mediana_horas_denuncia": round(df["Horas para Denunciar"].median(), 1),
    }