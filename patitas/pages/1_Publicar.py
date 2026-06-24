"""
Pagina: Publicar.

Formulario para reportar una mascota perdida o encontrada. Esta organizado
en bloques claros para reducir la friccion: primero lo esencial (que paso,
especie, zona, foto y contacto) y luego los detalles opcionales en un
desplegable. Al enviar, sube la foto a Storage, crea el anuncio y propone
difundirlo.
"""

from __future__ import annotations

import streamlit as st

from ui import styles, components
from src.models.anuncio import Anuncio, ESPECIES, SEXOS, TAMANOS
from src.services import anuncios_service
from src.database import storage
from src.utils.geo import DISTRITOS
from src.utils.errors import ValidationError, PatitasError

st.set_page_config(page_title="Publicar — Patitas", page_icon="🐾", layout="centered")
styles.aplicar(st)
styles.encabezado_marca(st, "Publicar un reporte")

components.confianza(
    st, "ti-clock-bolt",
    "Solo te tomara un par de minutos. Mientras mas detalles, mas facil sera reconocerla.",
)
st.markdown("")

ETIQUETAS_ESPECIE = {"perro": "Perro", "gato": "Gato", "otro": "Otra"}
ETIQUETAS_SEXO = {"macho": "Macho", "hembra": "Hembra", "desconocido": "No lo se"}
ETIQUETAS_TAMANO = {"pequeno": "Pequeno", "mediano": "Mediano", "grande": "Grande"}
ETIQUETAS_ESTADO = {"perdido": "La perdi", "encontrado": "La encontre"}

with st.form("formulario_anuncio", clear_on_submit=False):
    # --- Lo esencial -------------------------------------------------------
    st.markdown("#### Lo esencial")
    col1, col2 = st.columns(2)
    with col1:
        estado = st.radio(
            "Que paso", options=list(ETIQUETAS_ESTADO.keys()),
            format_func=lambda v: ETIQUETAS_ESTADO[v], horizontal=True,
        )
    with col2:
        especie = st.selectbox(
            "Especie", options=ESPECIES,
            format_func=lambda v: ETIQUETAS_ESPECIE.get(v, v),
        )

    col3, col4 = st.columns(2)
    with col3:
        distrito = st.selectbox("Distrito", options=DISTRITOS)
    with col4:
        fecha_evento = st.date_input("Fecha del hecho", value=None)

    descripcion = st.text_area(
        "Descripcion",
        placeholder="Senas particulares, color, comportamiento, collar, donde se vio por ultima vez...",
        height=110,
    )
    foto_archivo = st.file_uploader(
        "Foto de la mascota (JPG, PNG o WEBP, hasta 5 MB)",
        type=["jpg", "jpeg", "png", "webp"],
    )

    # --- Contacto ----------------------------------------------------------
    st.markdown("#### Como te contactan")
    col5, col6 = st.columns(2)
    with col5:
        telefono = st.text_input("Telefono o WhatsApp", placeholder="999 888 777")
    with col6:
        contacto_nombre = st.text_input("Tu nombre")
    email = st.text_input("Correo (opcional)")

    # --- Detalles opcionales ----------------------------------------------
    with st.expander("Agregar mas detalles (opcional)"):
        cda, cdb = st.columns(2)
        with cda:
            nombre = st.text_input("Nombre de la mascota")
            raza = st.text_input("Raza")
            sexo = st.selectbox(
                "Sexo", options=SEXOS,
                format_func=lambda v: ETIQUETAS_SEXO.get(v, v),
            )
        with cdb:
            color = st.text_input("Color")
            tamano = st.selectbox(
                "Tamano", options=[""] + list(TAMANOS),
                format_func=lambda v: ETIQUETAS_TAMANO.get(v, "Sin especificar") if v else "Sin especificar",
            )
            referencia = st.text_input("Referencia del lugar", placeholder="Cerca de...")
        foto_url_manual = st.text_input("O pega el enlace de una foto", placeholder="https://...")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            tiene_recompensa = st.checkbox("Ofrezco recompensa")
        with col_r2:
            monto = st.number_input("Monto en soles", min_value=0, step=10, value=0)

    enviado = st.form_submit_button("Publicar reporte", type="primary")


if enviado:
    # La foto se sube primero; si falla, no se crea el anuncio.
    foto_url = (foto_url_manual or "").strip()
    if foto_archivo is not None:
        try:
            foto_url = storage.subir_foto(foto_archivo.getvalue(), foto_archivo.type)
        except ValidationError as exc:
            st.error(f"Problema con la foto: {exc}")
            st.stop()
        except PatitasError as exc:
            st.error(f"No se pudo subir la foto: {exc}")
            st.stop()

    anuncio = Anuncio(
        origen="usuario",
        estado=estado,
        especie=especie,
        nombre=nombre.strip(),
        raza=raza.strip(),
        color=color.strip(),
        sexo=sexo,
        tamano=tamano,
        distrito=distrito,
        referencia_lugar=referencia.strip(),
        fecha_evento=fecha_evento.isoformat() if fecha_evento else None,
        descripcion=descripcion.strip(),
        foto_url=foto_url,
        tiene_recompensa=tiene_recompensa,
        monto_recompensa=float(monto) if (tiene_recompensa and monto) else None,
        contacto_nombre=contacto_nombre.strip(),
        contacto_telefono=telefono.strip(),
        contacto_email=email.strip(),
    )

    try:
        fila = anuncios_service.crear_anuncio(anuncio)
        st.session_state["ultimo_anuncio_id"] = fila.get("id")
        st.success("Reporte publicado. Gracias por ayudar.")
        st.balloons()
        components.confianza(
            st, "ti-share",
            "Ahora ve a la pagina Difundir (menu de la izquierda) para compartirlo en redes.",
        )
    except ValidationError as exc:
        st.error(f"Revisa el formulario: {exc}")
    except PatitasError as exc:
        st.error(f"No se pudo publicar: {exc}")

components.pie_pagina(st)
