"""
Modelo de datos de un anuncio de mascota.

Un Anuncio representa una mascota perdida o encontrada, sin importar si
lo publico una persona en la plataforma o si vino del scraping de un
sitio externo. El campo 'origen' distingue ambos casos.

La clase es el contrato de datos entre las capas: el formulario de
Streamlit y el scraper construyen Anuncios, los servicios los guardan y
leen, y la base de datos refleja sus campos. Centralizar la forma del
dato aqui evita inconsistencias.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date, datetime

# --- Valores permitidos para los campos categoricos ---
# Tenerlos aqui como constantes evita errores de tipeo y permite que los
# menus de la interfaz y las validaciones usen la misma fuente de verdad.

ESPECIES = ("perro", "gato", "otro")
ESTADOS = ("perdido", "encontrado", "reunido")
SEXOS = ("macho", "hembra", "desconocido")
TAMANOS = ("pequeno", "mediano", "grande")
ORIGENES = ("usuario", "scraping")


@dataclass
class Anuncio:
    """Una mascota perdida o encontrada."""

    # Identidad y origen
    id: str | None = None
    origen: str = "usuario"          # usuario | scraping
    fuente: str = ""                 # nombre del sitio si origen = scraping
    url_original: str = ""           # enlace al anuncio original (scraping)

    # Datos de la mascota
    nombre: str = ""
    especie: str = "otro"            # perro | gato | otro
    raza: str = ""
    color: str = ""
    sexo: str = "desconocido"        # macho | hembra | desconocido
    tamano: str = ""                 # pequeno | mediano | grande

    # Estado del caso
    estado: str = "perdido"          # perdido | encontrado | reunido

    # Ubicacion y fecha del hecho
    distrito: str = ""
    referencia_lugar: str = ""       # cerca de que punto se vio por ultima vez
    fecha_evento: str | None = None  # fecha en que se perdio o encontro (ISO)

    # Contenido
    descripcion: str = ""
    foto_url: str = ""
    tiene_recompensa: bool = False
    monto_recompensa: float | None = None

    # Contacto de quien publica
    contacto_nombre: str = ""
    contacto_telefono: str = ""
    contacto_email: str = ""

    # Metadatos
    fecha_publicacion: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    vistas: int = 0

    def to_dict(self) -> dict:
        """Convierte el anuncio en un diccionario listo para la base."""
        datos = asdict(self)
        # La base genera el id; no se envia si aun no existe.
        if datos.get("id") is None:
            datos.pop("id", None)
        # url_original tiene una restriccion de unicidad. Los anuncios de
        # usuario no tienen enlace de origen, asi que se guarda NULL en lugar
        # de una cadena vacia: PostgreSQL permite multiples NULL, pero solo
        # una cadena vacia repetida. El "or ''" protege contra valores None.
        if not (self.url_original or "").strip():
            datos["url_original"] = None
        return datos

    @classmethod
    def from_dict(cls, datos: dict) -> "Anuncio":
        """Construye un Anuncio a partir de una fila de la base."""
        campos_validos = {f for f in cls.__dataclass_fields__}
        filtrado = {k: v for k, v in datos.items() if k in campos_validos}
        return cls(**filtrado)

    @property
    def titulo(self) -> str:
        """Titulo corto y legible para mostrar en listados."""
        nombre = self.nombre.strip() or self.especie.capitalize()
        verbo = {
            "perdido": "perdido",
            "encontrado": "encontrado",
            "reunido": "reunido",
        }.get(self.estado, "")
        lugar = f" en {self.distrito}" if self.distrito else ""
        return f"{nombre} {verbo}{lugar}".strip()
