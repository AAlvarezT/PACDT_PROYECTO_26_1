"""
Patitas - Portada.

Punto de entrada de la aplicacion. Presenta la plataforma con un hero, los
indicadores reales, la explicacion de como funciona, historias de exito y
los reportes mas recientes. Desde aqui el usuario entiende el valor y pasa
a publicar o a explorar el tablon.

Ejecutar con:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from ui import styles, components
from src.services import anuncios_service, metrics_service
from src.utils.errors import PatitasError

st.set_page_config(
    page_title="Patitas — De vuelta a casa",
    page_icon="🐾",
    layout="wide",
)

styles.aplicar(st)

# --- Datos para el hero y las estadisticas ---------------------------------
try:
    anuncios = anuncios_service.listar_anuncios(limite=500)
    kpis = metrics_service.indicadores(metrics_service.anuncios_a_dataframe(anuncios))
    hay_conexion = True
except PatitasError:
    anuncios, kpis, hay_conexion = [], {"total": 0, "reunidos": 0, "perdidos": 0, "encontrados": 0}, False

# --- Hero ------------------------------------------------------------------
styles.hero(st, total=kpis["total"], reunidos=kpis["reunidos"])

if not hay_conexion:
    st.warning(
        "No se pudo conectar con la base de datos. Revisa el archivo .env y "
        "que el esquema este aplicado en Supabase."
    )

# --- Estadisticas ----------------------------------------------------------
styles.seccion(st, "La comunidad en numeros", "Cada reporte acerca a una mascota a su hogar")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Reportes totales", kpis["total"])
c2.metric("Buscando hogar", kpis["perdidos"] + kpis["encontrados"])
c3.metric("Reencuentros", kpis["reunidos"])
c4.metric("Tasa de reunion", f"{kpis.get('tasa_reunion', 0)} %")

# --- Como funciona ---------------------------------------------------------
styles.seccion(st, "Como funciona", "Tres pasos simples para ayudar")
p1, p2, p3 = st.columns(3)
with p1:
    components.paso(st, 1, "ti-camera", "Publica",
                    "Reporta a tu mascota perdida o una que encontraste, con foto, "
                    "zona y datos de contacto. Toma menos de dos minutos.")
with p2:
    components.paso(st, 2, "ti-share", "Difunde",
                    "Comparte el reporte en WhatsApp, Facebook, X o Telegram, o "
                    "imprime un cartel con codigo QR para tu barrio.")
with p3:
    components.paso(st, 3, "ti-home-heart", "Reune",
                    "Cuando la mascota vuelve a casa, marca el reporte como "
                    "reunido y celebra el reencuentro con la comunidad.")

# --- Confianza -------------------------------------------------------------
styles.seccion(st, "Una plataforma en la que confiar")
t1, t2, t3 = st.columns(3)
with t1:
    components.confianza(st, "ti-shield-check", "Contacto directo y seguro entre vecinos")
with t2:
    components.confianza(st, "ti-eye-check", "Cada reporte muestra zona y fecha verificables")
with t3:
    components.confianza(st, "ti-heart-handshake", "Sin costo: ayudar nunca deberia costar")

# --- Reportes recientes ----------------------------------------------------
if anuncios:
    styles.seccion(st, "Reportes recientes", "Las ultimas mascotas que necesitan ayuda")
    recientes = anuncios[:3]
    cols = st.columns(3)
    for col, anuncio in zip(cols, recientes):
        with col:
            components.tarjeta_anuncio(st, anuncio)

# --- Historias de exito ----------------------------------------------------
styles.seccion(st, "Historias con final feliz", "Lo que hace posible la comunidad")
h1, h2 = st.columns(2)
with h1:
    components.historia(
        st,
        "Publique a mi perro un viernes en la noche y para el domingo un vecino "
        "de dos cuadras ya lo habia reconocido por la foto. Gracias a todos.",
        "Maria, San Miguel",
    )
with h2:
    components.historia(
        st,
        "Encontre un gato asustado en la puerta de mi edificio. Lo publique y en "
        "horas apareció su familia. Sin esta red habria sido imposible.",
        "Jorge, Surco",
    )

components.pie_pagina(st)
