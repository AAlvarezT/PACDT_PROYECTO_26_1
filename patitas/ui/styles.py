"""
Estilos y piezas visuales de la aplicacion.

Centraliza el CSS de marca y las funciones que dibujan elementos visuales
grandes y repetidos: el encabezado, el hero de la portada, los titulos de
seccion y el pie. Las paginas llaman a estas funciones en lugar de repetir
HTML, lo que mantiene una apariencia uniforme.

El CSS se inyecta una vez por pagina con aplicar(). Estiliza tanto los
componentes propios (tarjetas, etiquetas) como algunos elementos nativos
de Streamlit (barra lateral, botones, metricas) con selectores estables.
"""

from __future__ import annotations

from ui import theme

# Hoja de estilos de marca. Usa variables CSS para no repetir colores.
CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@2.47.0/dist/tabler-icons.min.css');

:root {{
    --pino: {theme.PINO};
    --pino-oscuro: {theme.PINO_OSCURO};
    --miel: {theme.MIEL};
    --coral: {theme.CORAL};
    --papel: {theme.PAPEL};
    --crema: {theme.CREMA};
    --tinta: {theme.TINTA};
    --gris: {theme.GRIS};
    --borde: {theme.BORDE};
}}

/* --- Base --- */
html, body, [class*="css"], .stApp {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: var(--tinta);
}}
.stApp {{ background: var(--papel); }}

h1, h2, h3, h4 {{
    font-family: 'Fraunces', serif;
    color: var(--pino-oscuro);
    letter-spacing: -0.01em;
}}

/* Reduce el ancho del contenido para una lectura comoda */
.block-container {{ padding-top: 2.2rem; max-width: 1180px; }}

/* --- Barra lateral --- */
section[data-testid="stSidebar"] {{
    background: #FFFFFF;
    border-right: 1px solid var(--borde);
}}
section[data-testid="stSidebar"] .block-container {{ padding-top: 1.5rem; }}

/* --- Botones --- */
.stButton > button {{
    border-radius: 10px;
    border: 1px solid var(--borde);
    background: #FFFFFF;
    color: var(--tinta);
    font-weight: 600;
    padding: 0.5rem 1rem;
    transition: all 0.15s ease;
}}
.stButton > button:hover {{
    border-color: var(--pino);
    color: var(--pino);
}}
.stButton > button[kind="primary"] {{
    background: var(--pino);
    border-color: var(--pino);
    color: #FFFFFF;
}}
.stButton > button[kind="primary"]:hover {{
    background: var(--pino-oscuro);
    color: #FFFFFF;
}}

/* --- Enlaces tipo boton (link_button) --- */
.stLinkButton > a {{
    border-radius: 10px !important;
    font-weight: 600 !important;
}}

/* --- Metricas --- */
[data-testid="stMetric"] {{
    background: #FFFFFF;
    border: 1px solid var(--borde);
    border-radius: 14px;
    padding: 1rem 1.2rem;
}}
[data-testid="stMetricValue"] {{
    font-family: 'Fraunces', serif;
    color: var(--pino-oscuro);
}}

/* --- Encabezado de marca --- */
.marca {{ display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.3rem; }}
.marca .logo {{
    width: 38px; height: 38px; border-radius: 11px;
    background: var(--pino); color: #FFFFFF;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.25rem;
}}
.marca .nombre {{
    font-family: 'Fraunces', serif; font-size: 1.55rem;
    font-weight: 600; color: var(--pino); line-height: 1;
}}
.marca .lema {{ font-size: 0.9rem; color: var(--gris); }}

/* --- Hero de la portada --- */
.hero {{
    background: var(--pino);
    border-radius: 22px;
    padding: 2.6rem 2.4rem;
    color: #FFFFFF;
    position: relative;
    overflow: hidden;
}}
.hero h1 {{ color: #FFFFFF; font-size: 2.5rem; line-height: 1.1; margin: 0 0 0.7rem; }}
.hero p {{ color: #EAF5F0; font-size: 1.08rem; max-width: 30rem; margin: 0; }}
.hero .paws {{
    position: absolute; right: -10px; bottom: -20px;
    font-size: 9rem; color: rgba(255,255,255,0.08);
}}
.hero .trust {{
    display: flex; gap: 1.3rem; margin-top: 1.6rem; flex-wrap: wrap;
}}
.hero .trust span {{
    display: inline-flex; align-items: center; gap: 0.4rem;
    font-size: 0.88rem; color: #EAF5F0;
}}
.hero .trust i {{ color: var(--miel); font-size: 1.05rem; }}

/* --- Titulo de seccion --- */
.seccion {{ margin: 2.2rem 0 1rem; }}
.seccion .t {{ font-family: 'Fraunces', serif; font-size: 1.5rem; font-weight: 600; color: var(--pino-oscuro); }}
.seccion .s {{ font-size: 0.95rem; color: var(--gris); margin-top: 0.1rem; }}

/* --- Tarjeta de mascota --- */
.tarjeta {{
    background: #FFFFFF;
    border: 1px solid var(--borde);
    border-radius: 16px;
    overflow: hidden;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    height: 100%;
}}
.tarjeta:hover {{ transform: translateY(-3px); box-shadow: 0 12px 26px rgba(20,117,92,0.10); }}
.tarjeta .foto {{
    width: 100%; height: 190px; object-fit: cover; display: block;
    background: var(--crema);
}}
.tarjeta .foto-vacia {{
    width: 100%; height: 190px; display: flex; align-items: center; justify-content: center;
    background: var(--crema); color: var(--pino);
    font-size: 3.4rem;
}}
.tarjeta .cuerpo {{ padding: 0.9rem 1.05rem 1.1rem; }}
.tarjeta .titulo {{
    font-family: 'Fraunces', serif; font-size: 1.16rem; font-weight: 600;
    color: var(--tinta); margin-bottom: 0.35rem; line-height: 1.2;
}}
.tarjeta .meta {{
    display: flex; flex-wrap: wrap; gap: 0.4rem 0.9rem;
    font-size: 0.86rem; color: var(--gris); margin-bottom: 0.6rem;
}}
.tarjeta .meta span {{ display: inline-flex; align-items: center; gap: 0.3rem; }}
.tarjeta .descripcion {{
    font-size: 0.9rem; color: #41433D; line-height: 1.5; margin-bottom: 0.85rem;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}}
.tarjeta .contacto {{
    display: inline-flex; align-items: center; gap: 0.45rem;
    background: #25D366; color: #FFFFFF; text-decoration: none;
    font-weight: 600; font-size: 0.9rem; padding: 0.5rem 0.9rem; border-radius: 10px;
}}
.tarjeta .contacto:hover {{ filter: brightness(0.95); }}

/* --- Etiqueta de estado --- */
.etiqueta {{
    display: inline-flex; align-items: center; gap: 0.35rem;
    padding: 0.22rem 0.7rem; border-radius: 999px;
    font-size: 0.78rem; font-weight: 600; color: #FFFFFF;
    margin-bottom: 0.55rem;
}}

/* --- Paso (como funciona) --- */
.paso {{
    background: #FFFFFF; border: 1px solid var(--borde); border-radius: 16px;
    padding: 1.4rem 1.3rem; height: 100%;
}}
.paso .num {{
    width: 40px; height: 40px; border-radius: 12px; background: var(--crema);
    color: var(--pino); display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; margin-bottom: 0.8rem;
}}
.paso h4 {{ margin: 0 0 0.35rem; font-size: 1.1rem; }}
.paso p {{ margin: 0; font-size: 0.92rem; color: var(--gris); line-height: 1.5; }}

/* --- Historia de exito --- */
.historia {{
    background: #FFFFFF; border: 1px solid var(--borde); border-left: 4px solid var(--miel);
    border-radius: 14px; padding: 1.2rem 1.3rem; height: 100%;
}}
.historia .cita {{ font-size: 0.96rem; color: #36382F; line-height: 1.55; font-style: italic; }}
.historia .autor {{ font-size: 0.85rem; color: var(--gris); margin-top: 0.6rem; font-weight: 600; }}

/* --- Estado vacio --- */
.vacio {{
    text-align: center; padding: 3rem 1.5rem; color: var(--gris);
    background: #FFFFFF; border: 1px dashed var(--borde); border-radius: 18px;
}}
.vacio i {{ font-size: 3rem; color: var(--pino); opacity: 0.5; }}
.vacio .t {{ font-family: 'Fraunces', serif; font-size: 1.25rem; color: var(--pino-oscuro); margin: 0.6rem 0 0.3rem; }}

/* --- Insignia de confianza --- */
.confianza {{
    display: flex; gap: 0.6rem; align-items: center;
    background: #F2F8F5; border: 1px solid #D6EAE1; border-radius: 12px;
    padding: 0.7rem 0.9rem; font-size: 0.87rem; color: var(--pino-oscuro);
}}
.confianza i {{ font-size: 1.15rem; color: var(--pino); }}

/* --- Pie --- */
.pie {{
    color: var(--gris); font-size: 0.82rem; text-align: center;
    margin-top: 2.5rem; padding-top: 1.2rem; border-top: 1px solid var(--borde);
}}
</style>
"""


def aplicar(st) -> None:
    """Inyecta el CSS de marca. Se llama al inicio de cada pagina."""
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado_marca(st, subtitulo: str = "") -> None:
    """Dibuja el encabezado con el logo, el nombre y un subtitulo opcional."""
    st.markdown(
        '<div class="marca">'
        '<span class="logo"><i class="ti ti-paw"></i></span>'
        '<span class="nombre">Patitas</span>'
        '<span class="lema">De vuelta a casa</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    if subtitulo:
        st.markdown(f"### {subtitulo}")


def hero(st, total: int, reunidos: int) -> None:
    """Dibuja el hero de la portada con titular, llamada y senales de confianza."""
    st.markdown(
        f"""
        <div class="hero">
            <i class="ti ti-paw paws"></i>
            <h1>Ayudemos a cada mascota<br>a volver a casa</h1>
            <p>Publica una mascota perdida o encontrada en minutos y difundela
            en redes para que toda tu comunidad la reconozca.</p>
            <div class="trust">
                <span><i class="ti ti-shield-check"></i> Publicar es gratis</span>
                <span><i class="ti ti-bolt"></i> Toma menos de 2 minutos</span>
                <span><i class="ti ti-users"></i> {total} reportes · {reunidos} reencuentros</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def seccion(st, titulo: str, subtitulo: str = "") -> None:
    """Dibuja un titulo de seccion con subtitulo opcional."""
    sub = f'<div class="s">{subtitulo}</div>' if subtitulo else ""
    st.markdown(
        f'<div class="seccion"><div class="t">{titulo}</div>{sub}</div>',
        unsafe_allow_html=True,
    )


def pie_pagina(st) -> None:
    """Dibuja el pie comun a todas las paginas."""
    st.markdown(
        '<div class="pie">Patitas — De vuelta a casa · '
        'Plataforma comunitaria para reunir mascotas con sus familias en Lima</div>',
        unsafe_allow_html=True,
    )
