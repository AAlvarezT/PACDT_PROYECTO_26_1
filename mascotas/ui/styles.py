"""
Estilos CSS personalizados.

Streamlit permite inyectar CSS para afinar la apariencia mas alla del
tema base. Aqui se define el CSS de la marca y una funcion para
aplicarlo desde cualquier pagina. Se mantiene contenido para no competir
con el tema de .streamlit/config.toml, solo lo necesario para que las
tarjetas y los encabezados se vean cuidados.
"""

from __future__ import annotations

from ui import theme

CSS = f"""
<style>
/* Tipografias de marca */
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif;
}}

h1, h2, h3 {{
    font-family: 'Fraunces', serif;
    color: {theme.PINO_OSCURO};
}}

/* Encabezado de marca en la parte superior de las paginas */
.marca {{
    display: flex;
    align-items: baseline;
    gap: 0.6rem;
    margin-bottom: 0.2rem;
}}
.marca .nombre {{
    font-family: 'Fraunces', serif;
    font-size: 1.9rem;
    font-weight: 600;
    color: {theme.PINO};
    line-height: 1;
}}
.marca .lema {{
    font-size: 0.95rem;
    color: {theme.GRIS};
}}

/* Tarjeta de anuncio */
.tarjeta {{
    background: #FFFFFF;
    border: 1px solid {theme.CREMA};
    border-radius: 14px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.9rem;
}}
.tarjeta .titulo {{
    font-family: 'Fraunces', serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: {theme.TINTA};
    margin-bottom: 0.25rem;
}}
.tarjeta .meta {{
    font-size: 0.85rem;
    color: {theme.GRIS};
    margin-bottom: 0.5rem;
}}
.tarjeta .descripcion {{
    font-size: 0.92rem;
    color: {theme.TINTA};
    line-height: 1.5;
}}

/* Etiqueta de estado */
.etiqueta {{
    display: inline-block;
    padding: 0.15rem 0.6rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #FFFFFF;
}}

/* Pie discreto */
.pie {{
    color: {theme.GRIS};
    font-size: 0.82rem;
    text-align: center;
    margin-top: 2rem;
}}
</style>
"""


def aplicar(st) -> None:
    """Inyecta el CSS de marca. Llamar al inicio de cada pagina."""
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado_marca(st, subtitulo: str = "") -> None:
    """Dibuja el encabezado de marca con el nombre y el lema."""
    st.markdown(
        f"""
        <div class="marca">
            <span class="nombre">Patitas</span>
            <span class="lema">De vuelta a casa</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if subtitulo:
        st.markdown(f"#### {subtitulo}")
