

import pandas as pd

from utils import log_step, require_columns

# ---------------------------------------------------------------------------
# Léxico curado (dominio: circunstancias de desaparición de personas)
# ---------------------------------------------------------------------------
# Escala de intensidad: ±1 (leve) a ±2 (fuerte). Las claves van sin tilde
# porque el texto se normaliza (tildes removidas) antes de comparar.
# La ñ se conserva tal cual (no se considera una tilde a remover).

_NEGATIVE_LEXICON = {
    "violencia": -2, "violento": -2, "violenta": -2, "maltrato": -2,
    "abuso": -2, "abusivo": -2, "abusiva": -2, "secuestro": -2,
    "secuestrado": -2, "secuestrada": -2, "amenaza": -2, "amenazado": -2,
    "amenazada": -2, "golpiza": -2, "golpeado": -2, "golpeada": -2,
    "agresion": -2, "agresivo": -2, "agresiva": -2, "trata": -2,
    "explotacion": -2, "forzado": -2, "forzada": -2, "herido": -2,
    "herida": -2, "lesiones": -2, "fallecido": -2, "fallecida": -2,
    "muerte": -2, "suicidio": -2, "suicida": -2, "autolesion": -2,
    "conflicto": -1, "discusion": -1, "pelea": -1, "huyo": -1,
    "fuga": -1, "drogas": -1, "alcohol": -1, "depresion": -1,
    "riesgo": -1, "peligro": -1, "peligroso": -1, "peligrosa": -1,
    "sospechoso": -1, "sospechosa": -1, "abandono": -1, "abandonado": -1,
    "abandonada": -1, "problema": -1, "problemas": -1, "enfermo": -1,
    "enferma": -1, "crisis": -1, "desconocido": -1, "desconocida": -1,
}

_POSITIVE_LEXICON = {
    "encontrado": 2, "encontrada": 2, "sano": 2, "sana": 2, "salvo": 2,
    "salva": 2, "localizado": 2, "localizada": 2, "regreso": 2,
    "recuperado": 2, "recuperada": 2, "resuelto": 2, "resuelta": 2,
    "aparecio": 2, "bien": 1, "tranquilo": 1, "tranquila": 1,
    "voluntaria": 1, "voluntario": 1, "contento": 1, "contenta": 1,
    "feliz": 1, "saludable": 1, "estable": 1, "seguro": 1, "segura": 1,
    "acompañado": 1, "acompañada": 1, "cuidado": 1, "protegido": 1,
    "protegida": 1, "normal": 1, "volvio": 1,
}

_LEXICON = {**_NEGATIVE_LEXICON, **_POSITIVE_LEXICON}

_NEGATION_WORDS = {"no", "sin", "nunca", "jamas", "tampoco", "ni"}
_NEGATION_WINDOW = 5  # palabras de alcance hacia atrás

# Tildes a remover (la ñ NO se toca: no es una tilde, es otra letra).
_ACCENT_MAP = str.maketrans("áéíóúü", "aeiouu")

# Columnas sobre las que tiene sentido aplicar este análisis. 'Vestimenta'
# se excluye a propósito: es descripción física/ropa, sin carga emocional
# real que analizar.
SENTIMENT_ELIGIBLE_COLUMNS = ["Circunstancias", "Otras observaciones"]


def _tokenize(text: str) -> list[str]:
    """Minúsculas + sin tildes (preservando ñ) + separación simple por palabras."""
    text = text.lower().translate(_ACCENT_MAP)
    return [w.strip(".,;:()¿?¡!\"'") for w in text.split()]


def sentiment_score(text: str) -> float:
    """
    Score heurístico de tono para un texto en español, normalizado por
    cantidad de palabras (para no sesgar a favor de textos largos).

    Manejo de negación (asimétrico, a propósito):
    - Negar una palabra NEGATIVA ("no hubo violencia") neutraliza su
      aporte (pasa a 0): la ausencia de un riesgo no es un evento
      positivo, solo deja de ser negativo.
    - Negar una palabra POSITIVA ("no fue encontrado") invierte su
      signo a negativo: la ausencia de una resolución sí es mala
      noticia.
    """
    if not isinstance(text, str) or not text.strip():
        return 0.0

    tokens = _tokenize(text)
    if not tokens:
        return 0.0

    total = 0.0
    for i, tok in enumerate(tokens):
        weight = _LEXICON.get(tok, 0)
        if weight == 0:
            continue

        window = tokens[max(0, i - _NEGATION_WINDOW):i]
        negated = any(w in _NEGATION_WORDS for w in window)
        if negated:
            weight = -weight if weight > 0 else 0

        total += weight

    return round(total / len(tokens), 4)


def sentiment_label(score: float, threshold: float = 0.02) -> str:
    """Bucketiza el score normalizado en Positivo / Neutral / Negativo."""
    if score > threshold:
        return "Positivo"
    if score < -threshold:
        return "Negativo"
    return "Neutral"


@log_step
def add_sentiment(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Agrega dos columnas al DataFrame: '{col}_sentimiento' (score
    numérico) y '{col}_sentimiento_label' (Positivo/Neutral/Negativo).

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
    df[f"{col}_sentimiento"] = df[col].apply(sentiment_score)
    df[f"{col}_sentimiento_label"] = df[f"{col}_sentimiento"].apply(sentiment_label)
    return df
