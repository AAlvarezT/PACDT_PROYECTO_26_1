"""
Identidad visual de la aplicacion.

Define la paleta de color, las etiquetas legibles y los iconos por estado.
Tener todo esto en un solo lugar mantiene la coherencia y facilita ajustar
la marca sin tocar las paginas.

La paleta busca transmitir confianza y cercania: un verde pino como color
principal, ambar miel como acento calido y coral para las alertas, sobre
un fondo color papel.
"""

from __future__ import annotations

# --- Colores de marca ---
PINO = "#14755C"
PINO_OSCURO = "#0C4D3C"
MIEL = "#F2A03D"
CORAL = "#E9603F"
PAPEL = "#FBF8F2"
CREMA = "#F3ECDD"
TINTA = "#20251F"
GRIS = "#6B6B61"
BORDE = "#E7DFCE"

# --- Color por estado del anuncio ---
COLOR_ESTADO = {
    "perdido": CORAL,
    "encontrado": MIEL,
    "reunido": PINO,
}

# --- Etiquetas legibles ---
ETIQUETA_ESTADO = {
    "perdido": "Perdido",
    "encontrado": "Encontrado",
    "reunido": "En casa",
}

ETIQUETA_ESPECIE = {
    "perro": "Perro",
    "gato": "Gato",
    "otro": "Mascota",
}

# Iconos de la fuente Tabler (se cargan por CDN en el CSS).
ICONO_ESTADO = {
    "perdido": "ti-alert-triangle",
    "encontrado": "ti-eye",
    "reunido": "ti-home-heart",
}

ICONO_ESPECIE = {
    "perro": "ti-dog",
    "gato": "ti-cat",
    "otro": "ti-paw",
}

NOMBRE_CANAL = {
    "whatsapp": "WhatsApp",
    "facebook": "Facebook",
    "x": "X (Twitter)",
    "telegram": "Telegram",
}

ICONO_CANAL = {
    "whatsapp": "ti-brand-whatsapp",
    "facebook": "ti-brand-facebook",
    "x": "ti-brand-x",
    "telegram": "ti-brand-telegram",
}
