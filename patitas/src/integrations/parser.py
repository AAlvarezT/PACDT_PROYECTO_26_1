"""
Extraccion de datos a partir de texto libre.

Recibe el texto de un anuncio (por ejemplo, de un sitio externo) y
detecta especie, estado, distrito y si menciona recompensa. No depende
de la red ni de la base, por lo que su logica se puede probar de forma
aislada y rapida.
"""

from __future__ import annotations

import re

from src.utils.geo import DISTRITOS

# --- Vocabulario de deteccion, ampliable sin tocar la logica ---

PALABRAS_RELEVANTES = (
    "perdido", "perdida", "extraviado", "extraviada", "se perdio",
    "encontrado", "encontrada", "se busca", "desaparecio", "hallado",
    "recompensa", "ayuda a encontrar", "visto",
)

TERMINOS_PERRO = (
    "perro", "perrito", "perrita", "perra", "cachorro", "cachorrito", "lomito",
)
TERMINOS_GATO = (
    "gato", "gatito", "gatita", "gata", "michi", "felino", "minino",
)

TERMINOS_PERDIDO = (
    "perdid", "extravi", "se perdio", "desaparec", "se busca", "busco a",
)
TERMINOS_ENCONTRADO = (
    "encontr", "hallad", "halle", "rescat", "vi a un", "esta en",
)


def limpiar_texto(texto: str) -> str:
    """Colapsa espacios en blanco y recorta el texto a 280 caracteres."""
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto[:280]


def es_relevante(texto: str) -> bool:
    """Indica si el texto parece un anuncio de mascota perdida o encontrada."""
    t = texto.lower()
    return any(palabra in t for palabra in PALABRAS_RELEVANTES)


def detectar_especie(texto: str) -> str:
    """Devuelve 'perro', 'gato' u 'otro' segun los terminos presentes."""
    t = texto.lower()
    if any(term in t for term in TERMINOS_PERRO):
        return "perro"
    if any(term in t for term in TERMINOS_GATO):
        return "gato"
    return "otro"


def detectar_estado(texto: str) -> str:
    """Devuelve 'perdido', 'encontrado' o 'perdido' por defecto."""
    t = texto.lower()
    perdido = any(term in t for term in TERMINOS_PERDIDO)
    encontrado = any(term in t for term in TERMINOS_ENCONTRADO)
    if encontrado and not perdido:
        return "encontrado"
    # Ante la ambiguedad o la falta de senales, se asume perdido, que es
    # el caso mas urgente.
    return "perdido"


def detectar_distrito(texto: str) -> str:
    """Devuelve el primer distrito de Lima encontrado, o cadena vacia."""
    for distrito in DISTRITOS:
        if re.search(rf"\b{re.escape(distrito)}\b", texto, flags=re.IGNORECASE):
            return distrito
    return ""


def detectar_recompensa(texto: str) -> bool:
    """Indica si el anuncio menciona una recompensa."""
    t = texto.lower()
    return "recompensa" in t or "gratificacion" in t or "gratificacion" in t
