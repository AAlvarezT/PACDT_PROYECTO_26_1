# Análisis de Personas Desaparecidas en Perú — RENIPED

Análisis de datos de personas desaparecidas registradas en el sistema RENIPED
de la Policía Nacional del Perú. Desarrollado como proyecto integrador del curso
**Programación Avanzada para la Ciencia de Datos** (170107) — Universidad del Pacífico, 2026-01.

El dataset utilizado fue publicado por Aybar-Flores et al. (2026), *"Uncovering Disappearance Dynamics in Peru: A Two-Stage Multimodal Framework for Behavioral Segmentation and Voluntariness Prediction in Missing-Person Reports"*, Springer Nature Switzerland. DOI: https://doi.org/10.1007/978-3-032-20752-4_1. Disponible en https://github.com/yoce3/MissingPersonAnalisys.

## Estructura del repositorio

```
PACDT_PROYECTO_26_1/
├── data/
│   └── data_raw.csv                 # Dataset de entrada
├── src/
│   ├── app.py                       # Aplicación Streamlit (entrada principal)
│   ├── processing.py                # Carga, limpieza y métricas descriptivas
│   ├── viz.py                       # Funciones de visualización
│   ├── utils.py                     # Decoradores (logging, manejo de errores) y stopwords
│   ├── topics.py                    # Topic modeling: TF-IDF + K-Means
│   ├── sentiment.py                 # Análisis de sentimientos: RoBERTuito (pysentimiento)
│   └── sentiment_lexicon_legacy.py  # Versión heurística anterior, solo de referencia
├── docs/
│   ├── parcial.pdf                  # Documento técnico — entrega parcial
│   └── final.pdf                    # Documento técnico — entrega final
├── requirements.txt
└── README.md
```

## Instalación y ejecución local

**1. Clonar el repositorio**

```bash
git clone https://github.com/AAlvarezT/PACDT_PROYECTO_26_1.git
cd PACDT_PROYECTO_26_1
```

**2. Crear entorno virtual**

```bash
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

**3. Instalar dependencias**

```bash
pip install -r requirements.txt
```

> El análisis de sentimientos usa `pysentimiento`, que depende de `torch`. Por
> default, `pip` instala la versión de `torch` con soporte CUDA y arrastra
> ~2.7 GB de librerías nvidia que no sirven para nada sin GPU. Para evitarlo,
> agrega esta línea al inicio de `requirements.txt`, antes de `torch`:
> ```
> --extra-index-url https://download.pytorch.org/whl/cpu
> ```
> El topic modeling usa `scikit-learn` (TF-IDF + K-Means); si no estaba ya en
> `requirements.txt`, agrégalo también.

**4. Ejecutar la app**

```bash
streamlit run src/app.py
```

La app abre en `http://localhost:8501`. La primera vez que se usa el análisis
de sentimientos, descarga el modelo RoBERTuito (~435 MB) desde Hugging Face
Hub — necesita internet. Si la descarga falla o falta la librería, el
dashboard sigue funcionando igual, solo sin esa sección.

## Notas de despliegue (Streamlit Community Cloud)

`torch` + `transformers` + el modelo de sentimiento (~435 MB) pueden acercarse
al límite de 1 GB de RAM que garantiza el plan gratuito de Streamlit Community
Cloud. Si la app se cae por recursos al desplegarla ahí, Streamlit tiene un
formulario de aumento de recursos para proyectos educativos.

El archivo `app.log` (generado por el logging de `utils.py`) no se versiona;
agrégalo a `.gitignore`.

## Fuente de datos

**RENIPED** — Registro Nacional de Información de Personas Desaparecidas  
Policía Nacional del Perú  
https://desaparecidosenperu.policia.gob.pe/
