"""
sentiment.py
Análisis de sentimientos con un modelo Transformer pre-entrenado en
español: RoBERTuito, vía la librería `pysentimiento`.

"""
import pandas as pd

from utils import log_step, logger, require_columns

# Columnas sobre las que tiene sentido aplicar este análisis. 'Vestimenta'
# se excluye a propósito: es descripción física/ropa, sin carga emocional
# real que analizar.
SENTIMENT_ELIGIBLE_COLUMNS = ["Circunstancias", "Otras observaciones"]

_LABEL_MAP = {"POS": "Positivo", "NEU": "Neutral", "NEG": "Negativo"}


def load_analyzer():
    """
    Crea el analizador de sentimientos (RoBERTuito vía pysentimiento).

    A propósito NO se cachea aquí: este módulo no depende de Streamlit
    (sigue el mismo patrón que processing.py y viz.py), así que el
    cacheo del modelo en memoria (@st.cache_resource, para no
    recargarlo en cada rerun) se hace en app.py, donde sí corresponde.

    La primera llamada descarga el modelo (~435 MB) desde Hugging Face
    Hub — necesita internet la primera vez.
    """
    from pysentimiento import create_analyzer
    return create_analyzer(task="sentiment", lang="es")


@log_step
def add_sentiment(df: pd.DataFrame, col: str, analyzer) -> pd.DataFrame:
    """
    Agrega dos columnas usando el modelo ya cargado (`analyzer`, ver
    load_analyzer()):
    - '{col}_sentimiento': score continuo = P(POS) - P(NEG), en [-1, 1].
    - '{col}_sentimiento_label': Positivo / Neutral / Negativo.

    Se predice en UN solo batch (toda la lista de textos de una vez),
    no fila por fila, para aprovechar el batching interno de
    pysentimiento/transformers en vez de pagar el overhead del modelo
    en cada llamada.

    Raises
    ------
    ValueError
        Si `col` no existe en df, o no es una columna elegible para
        este análisis (ver SENTIMENT_ELIGIBLE_COLUMNS).
    """
    require_columns(df, [col], context="add_sentiment")
    if col not in SENTIMENT_ELIGIBLE_COLUMNS:
        raise ValueError(
            f"'{col}' no es una columna apta para análisis de sentimientos. "
            f"Columnas válidas: {SENTIMENT_ELIGIBLE_COLUMNS}"
        )

    df = df.copy()
    score_col, label_col = f"{col}_sentimiento", f"{col}_sentimiento_label"
    df[score_col] = pd.NA
    df[label_col] = pd.NA

    mask = df[col].notna() & (df[col].astype(str).str.strip() != "")
    if not mask.any():
        return df

    textos = df.loc[mask, col].astype(str).tolist()

    try:
        resultados = analyzer.predict(textos)
    except Exception as e:
        # Si el modelo falla a mitad de la inferencia (texto raro, OOM,
        # etc.), se loguea y se deja la columna en NA en vez de tumbar
        # toda la app: el resto del dashboard sigue funcionando igual.
        logger.exception("Fallo al predecir sentimiento para '%s': %s", col, e)
        return df

    labels = [_LABEL_MAP.get(r.output, "Neutral") for r in resultados]
    scores = [round(r.probas.get("POS", 0.0) - r.probas.get("NEG", 0.0), 4) for r in resultados]

    df.loc[mask, score_col] = scores
    df.loc[mask, label_col] = labels
    return df
