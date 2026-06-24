"""
Tema visual de la aplicacion.

Define la paleta de colores y algunas constantes de diseno que usan los
componentes. Tener los colores en un solo lugar mantiene la coherencia
visual y facilita ajustar la identidad de la marca.

Paleta inspirada en los carteles de mascotas perdidas: verde pino,
ambar miel y coral, sobre un fondo color papel.
"""

from __future__ import annotations

# Colores de marca
PINO = "#782A16"        # verde principal
PINO_OSCURO = "#502715"
MIEL = "#E0A422"        # ambar de acento
CORAL = "#E2674A"       # coral para alertas y estado perdido
PAPEL = "#D8C9A4"       # fondo claro
CREMA = "#CDC6B7"       # superficies secundarias
TINTA = "#2A2722"       # texto principal
GRIS = "#6E685C"        # texto secundario

# Colores por estado del anuncio, para etiquetas y graficos.
COLOR_ESTADO = {
    "perdido": CORAL,
    "encontrado": MIEL,
    "reunido": PINO,
}

# Etiquetas legibles para mostrar al usuario.
ETIQUETA_ESTADO = {
    "perdido": "Perdido",
    "encontrado": "Encontrado",
    "reunido": "Reunido con su familia",
}

ETIQUETA_ESPECIE = {
    "perro": "Perro",
    "gato": "Gato",
    "otro": "Otra mascota",
}

# Iconos de marca para los canales de difusion (nombres de la libreria
# de iconos de Streamlit no se usan aqui; se manejan con texto en la UI).
NOMBRE_CANAL = {
    "whatsapp": "WhatsApp",
    "facebook": "Facebook",
    "x": "X (Twitter)",
    "telegram": "Telegram",
}
