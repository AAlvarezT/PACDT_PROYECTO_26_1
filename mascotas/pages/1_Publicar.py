"""
Pagina: Publicar.

Formulario donde una persona reporta una mascota perdida o encontrada.
Al enviarlo, valida los datos, crea el anuncio en la base y ofrece pasar
directamente a la pagina de difusion para compartirlo.
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

st.markdown(
    "Completa los datos de la mascota. Mientras mas detalles, mas facil sera "
    "que alguien la reconozca."
)

# Etiquetas legibles para los menus, manteniendo el valor interno simple.
ETIQUETAS_ESPECIE = {"perro": "Perro", "gato": "Gato", "otro": "Otra"}
ETIQUETAS_SEXO = {"macho": "Macho", "hembra": "Hembra", "desconocido": "No lo se"}
ETIQUETAS_TAMANO = {"pequeno": "Pequeno", "mediano": "Mediano", "grande": "Grande"}
ETIQUETAS_ESTADO = {"perdido": "La perdi", "encontrado": "La encontre"}


with st.form("formulario_anuncio", clear_on_submit=False):
    st.markdown("#### Sobre el caso")
    col1, col2 = st.columns(2)
    with col1:
        estado = st.radio(
            "Que paso",
            options=list(ETIQUETAS_ESTADO.keys()),
            format_func=lambda v: ETIQUETAS_ESTADO[v],
            horizontal=True,
        )
    with col2:
        especie = st.selectbox(
            "Especie",
            options=ESPECIES,
            format_func=lambda v: ETIQUETAS_ESPECIE.get(v, v),
        )

    st.markdown("#### Datos de la mascota")
    col3, col4 = st.columns(2)
    with col3:
        nombre = st.text_input("Nombre (si lo tiene)")
        raza = st.text_input("Raza")
        sexo = st.selectbox(
            "Sexo",
            options=SEXOS,
            format_func=lambda v: ETIQUETAS_SEXO.get(v, v),
        )
    with col4:
        color = st.text_input("Color")
        tamano = st.selectbox(
            "Tamano",
            options=[""] + list(TAMANOS),
            format_func=lambda v: ETIQUETAS_TAMANO.get(v, "Sin especificar") if v else "Sin especificar",
        )

    st.markdown("#### Donde y cuando")
    col5, col6 = st.columns(2)
    with col5:
        distrito = st.selectbox("Distrito", options=DISTRITOS)
    with col6:
        fecha_evento = st.date_input("Fecha del hecho", value=None)
    referencia = st.text_input(
        "Referencia del lugar",
        placeholder="Cerca de que punto se vio por ultima vez",
    )

    st.markdown("#### Descripcion y foto")
    descripcion = st.text_area(
        "Descripcion",
        placeholder="Senas particulares, comportamiento, collar, etc.",
        height=120,
    )
    foto_archivo = st.file_uploader(
        "Sube una foto (JPG, PNG o WEBP, hasta 5 MB)",
        type=["jpg", "jpeg", "png", "webp"],
    )
    foto_url_manual = st.text_input(
        "O pega el enlace de una foto (opcional)",
        placeholder="https://...",
    )

    st.markdown("#### Recompensa")
    col7, col8 = st.columns(2)
    with col7:
        tiene_recompensa = st.checkbox("Ofrezco recompensa")
    with col8:
        monto = st.number_input(
            "Monto en soles (opcional)", min_value=0, step=10, value=0
        )

    st.markdown("#### Tus datos de contacto")
    contacto_nombre = st.text_input("Tu nombre")
    col9, col10 = st.columns(2)
    with col9:
        telefono = st.text_input("Telefono o WhatsApp")
    with col10:
        email = st.text_input("Correo (opcional)")

    enviado = st.form_submit_button("Publicar reporte", type="primary")


if enviado:
    # Si el usuario subio una foto, primero se sube a Storage y se obtiene
    # su URL publica. Si solo pego un enlace, se usa ese.
    foto_url = foto_url_manual.strip()
    if foto_archivo is not None:
        try:
            foto_url = storage.subir_foto(
                contenido=foto_archivo.getvalue(),
                tipo_mime=foto_archivo.type,
            )
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
        st.success("Reporte publicado. Gracias por ayudar.")
        # Guarda el id en la sesion para enlazar con la pagina de difusion.
        st.session_state["ultimo_anuncio_id"] = fila.get("id")
        st.markdown(
            "Ahora puedes ir a la pagina **Difundir** (menu de la izquierda) "
            "para compartir este reporte en redes sociales."
        )
    except ValidationError as exc:
        st.error(f"Revisa el formulario: {exc}")
    except PatitasError as exc:
        st.error(f"No se pudo publicar: {exc}")

components.pie_pagina(st)
