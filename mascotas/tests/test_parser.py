"""
Pruebas del parser de texto.

No requieren red ni base de datos: validan la deteccion de especie,
estado, distrito y recompensa de forma aislada.

Ejecutar con:
    pytest tests/test_parser.py -v
"""

from src.integrations import parser


def test_es_relevante_detecta_anuncio():
    assert parser.es_relevante("Se perdio mi perrito en Surco")
    assert parser.es_relevante("Encontrado gato en Barranco")


def test_es_relevante_descarta_irrelevante():
    assert not parser.es_relevante("Alguien vende croquetas baratas?")


def test_detectar_especie():
    assert parser.detectar_especie("mi perrito Rocky") == "perro"
    assert parser.detectar_especie("una gatita blanca") == "gato"
    assert parser.detectar_especie("se perdio mi conejo") == "otro"


def test_detectar_estado_encontrado():
    assert parser.detectar_estado("encontrado cerca al parque") == "encontrado"


def test_detectar_estado_perdido_por_defecto():
    assert parser.detectar_estado("se perdio en Lince") == "perdido"
    # Sin senales claras, asume perdido (caso mas urgente).
    assert parser.detectar_estado("texto sin pistas") == "perdido"


def test_detectar_distrito():
    assert parser.detectar_distrito("perdido en La Molina ayer") == "La Molina"
    assert parser.detectar_distrito("sin ubicacion") == ""


def test_detectar_recompensa():
    assert parser.detectar_recompensa("ofrezco recompensa") is True
    assert parser.detectar_recompensa("sin nada a cambio") is False


def test_limpiar_texto_recorta():
    largo = "a " * 300
    assert len(parser.limpiar_texto(largo)) <= 280
