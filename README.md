# Análisis de Personas Desaparecidas en Perú — RENIPED

Análisis de datos de personas desaparecidas registradas en el sistema RENIPED
de la Policía Nacional del Perú. Desarrollado como proyecto integrador del curso
**Programación Avanzada para la Ciencia de Datos** (170107) — Universidad del Pacífico, 2026-01.

El dataset utilizado fue publicado por Aybar-Flores et al. (2026), *"Uncovering Disappearance Dynamics in Peru: A Two-Stage Multimodal Framework for Behavioral Segmentation and Voluntariness Prediction in Missing-Person Reports"*, Springer Nature Switzerland. DOI: https://doi.org/10.1007/978-3-032-20752-4_1. Disponible en https://github.com/yoce3/MissingPersonAnalisys.

## Estructura del repositorio

```
PACDT_PROYECTO_26_1/
├── data/
│   └── data_raw.csv            # Dataset de entrada
├── src/
│   ├── app.py                  # Aplicación Streamlit (entrada principal)
│   ├── processing.py           # Carga, limpieza y métricas descriptivas
│   └── viz.py                  # Funciones de visualización
├── docs/
│   └── parcial.pdf             # Documento técnico — entrega parcial
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

**4. Ejecutar la app**

```bash
streamlit run src/app.py
```

La app abre en `http://localhost:8501`.

## Fuente de datos

**RENIPED** — Registro Nacional de Información de Personas Desaparecidas  
Policía Nacional del Perú  
https://desaparecidosenperu.policia.gob.pe/
