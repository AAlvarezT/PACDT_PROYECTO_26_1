"""
Servicio de metricas.

Calcula los indicadores y agregaciones que muestra el panel de analisis.
Trabaja sobre los anuncios y las difusiones ya cargados, usando pandas
para las agrupaciones. Mantener este calculo separado de la interfaz
permite probarlo y reutilizarlo.
"""

from __future__ import annotations

import logging

import pandas as pd

from src.models.anuncio import Anuncio

log = logging.getLogger("patitas")


def anuncios_a_dataframe(anuncios: list[Anuncio]) -> pd.DataFrame:
    """Convierte una lista de anuncios en un DataFrame para analizar."""
    if not anuncios:
        return pd.DataFrame()
    df = pd.DataFrame([a.to_dict() for a in anuncios])
    # Asegura tipos de fecha utiles para las series temporales.
    if "fecha_publicacion" in df.columns:
        df["fecha_publicacion"] = pd.to_datetime(
            df["fecha_publicacion"], errors="coerce"
        )
    return df


def indicadores(df: pd.DataFrame) -> dict[str, float | int]:
    """
    Calcula los indicadores principales (tarjetas del panel).

    Devuelve un diccionario con totales y la tasa de reunion, que es el
    porcentaje de mascotas que volvieron con su familia.
    """
    if df.empty:
        return {
            "total": 0,
            "perdidos": 0,
            "encontrados": 0,
            "reunidos": 0,
            "tasa_reunion": 0.0,
        }

    total = len(df)
    por_estado = df["estado"].value_counts()
    reunidos = int(por_estado.get("reunido", 0))

    return {
        "total": total,
        "perdidos": int(por_estado.get("perdido", 0)),
        "encontrados": int(por_estado.get("encontrado", 0)),
        "reunidos": reunidos,
        "tasa_reunion": round(100 * reunidos / total, 1) if total else 0.0,
    }


def conteo_por_columna(df: pd.DataFrame, columna: str) -> pd.DataFrame:
    """
    Cuenta cuantos anuncios hay por cada valor de una columna.

    Util para los graficos de barras (por distrito, por especie, etc.).
    Devuelve un DataFrame con las columnas [columna, 'cantidad'].
    """
    if df.empty or columna not in df.columns:
        return pd.DataFrame(columns=[columna, "cantidad"])
    conteo = (
        df[columna]
        .fillna("Sin dato")
        .replace("", "Sin dato")
        .value_counts()
        .reset_index()
    )
    conteo.columns = [columna, "cantidad"]
    return conteo


def serie_temporal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa los anuncios por dia de publicacion.

    Devuelve un DataFrame con las columnas ['fecha', 'cantidad'] para
    dibujar la tendencia de publicaciones en el tiempo.
    """
    if df.empty or "fecha_publicacion" not in df.columns:
        return pd.DataFrame(columns=["fecha", "cantidad"])
    serie = (
        df.dropna(subset=["fecha_publicacion"])
        .assign(fecha=lambda d: d["fecha_publicacion"].dt.date)
        .groupby("fecha")
        .size()
        .reset_index(name="cantidad")
        .sort_values("fecha")
    )
    return serie


def difusiones_por_canal(difusiones: list[dict]) -> pd.DataFrame:
    """
    Cuenta cuantas veces se compartio por cada red social.

    Devuelve un DataFrame con las columnas ['canal', 'cantidad'].
    """
    if not difusiones:
        return pd.DataFrame(columns=["canal", "cantidad"])
    df = pd.DataFrame(difusiones)
    conteo = df["canal"].value_counts().reset_index()
    conteo.columns = ["canal", "cantidad"]
    return conteo
