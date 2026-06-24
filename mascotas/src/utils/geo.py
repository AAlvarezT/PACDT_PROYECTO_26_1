"""
Datos geograficos de los distritos de Lima.

Contiene la lista de distritos y las coordenadas aproximadas (centro
del distrito) que usa el mapa del tablon. Como los anuncios guardan el
distrito por nombre y no por coordenadas exactas, estas sirven para
ubicar cada anuncio en el mapa de forma aproximada.
"""

from __future__ import annotations

# Centro aproximado de cada distrito (latitud, longitud).
# Fuente: coordenadas publicas de referencia de Lima Metropolitana.
DISTRITOS_COORDS: dict[str, tuple[float, float]] = {
    "Miraflores": (-12.1211, -77.0297),
    "San Isidro": (-12.0972, -77.0365),
    "Surco": (-12.1450, -76.9933),
    "Santiago de Surco": (-12.1450, -76.9933),
    "Barranco": (-12.1490, -77.0210),
    "San Borja": (-12.1080, -77.0030),
    "La Molina": (-12.0790, -76.9440),
    "Jesus Maria": (-12.0740, -77.0490),
    "Magdalena": (-12.0970, -77.0720),
    "Pueblo Libre": (-12.0760, -77.0630),
    "Lince": (-12.0880, -77.0360),
    "San Miguel": (-12.0770, -77.0920),
    "Surquillo": (-12.1120, -77.0170),
    "Chorrillos": (-12.1700, -77.0250),
    "Los Olivos": (-11.9750, -77.0700),
    "Comas": (-11.9380, -77.0480),
    "Ate": (-12.0260, -76.9180),
    "La Victoria": (-12.0670, -77.0170),
    "Brena": (-12.0560, -77.0500),
    "Rimac": (-12.0270, -77.0290),
    "Callao": (-12.0560, -77.1180),
    "Bellavista": (-12.0620, -77.1010),
    "San Juan de Lurigancho": (-11.9930, -77.0060),
    "San Juan de Miraflores": (-12.1560, -76.9700),
    "Villa El Salvador": (-12.2130, -76.9380),
    "Independencia": (-11.9880, -77.0530),
    "Carabayllo": (-11.8970, -77.0360),
    "Puente Piedra": (-11.8650, -77.0760),
    "El Agustino": (-12.0420, -76.9990),
    "Lima": (-12.0464, -77.0428),
}

# Lista simple de nombres, util para menus desplegables y deteccion.
DISTRITOS = tuple(DISTRITOS_COORDS.keys())


def coords_de(distrito: str) -> tuple[float, float] | None:
    """Devuelve las coordenadas de un distrito, o None si no se conoce."""
    return DISTRITOS_COORDS.get(distrito)
