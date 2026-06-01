# Análisis de Personas Desaparecidas en Perú — RENIPED
### Entrega Parcial 

**Integrantes:**
- [Jose Carlos Salinas] — [jc.salinasma@alum.up.edu.pe]
- [Arturo Alvarez de la Torre] — [aa.alvarez....@alum.up.edu.pe]
- [Gianella Mayra Silvestre Nina] — [gm.silvestreni@alum.up.edu.pe]
- [Jose Luis Atto Pintado] — [jl.attopi@alum.up.edu.pe]
- [Alyssa Antuanette Trujillo Cruzado] — [aa.trujillocr@alum.up.edu.pe]
---

## 1. Dataset: RENIPED

El **Registro Nacional de Información de Personas Desaparecidas (RENIPED)** es el sistema oficial de la Policía Nacional del Perú para el registro y seguimiento de denuncias de desaparición a nivel nacional. Los datos son de acceso público a través del portal institucional (https://desaparecidosenperu.policia.gob.pe/) y no tienen restricción de uso para fines informativos o académicos.

El dataset utilizado fue publicado por Aybar-Flores et al. (2026), *"Uncovering Disappearance Dynamics in Peru: A Two-Stage Multimodal Framework for Behavioral Segmentation and Voluntariness Prediction in Missing-Person Reports"*, Springer Nature Switzerland. DOI: https://doi.org/10.1007/978-3-032-20752-4_1. El dataset y el código asociado están disponibles en https://github.com/yoce3/MissingPersonAnalisys. Cada registro corresponde a una denuncia formal de desaparición e incluye información sobre la persona desaparecida, las circunstancias del hecho, características físicas, ubicación geográfica y el estado de resolución del caso.

Las variables utilizadas en el análisis se agrupan en las siguientes categorías:

| Categoría | Variables |
|---|---|
| Demográficas | `EDAD`, `PAIS DE NACIMIENTO` |
| Temporales | `Fecha Hecho`, `Fecha Denuncia`, `Horas para Denunciar`, `Horas para Aparecer` |
| Geográficas | `Lugar Hecho`, `Latitud`, `Longitud` |
| Estado del caso | `Aparecido`, `Fecha de Aparición` |
| Características físicas | `Tez`, `Fenotipo`, `Cabello`, `Contextura`, `Estatura`, `Ojos`, `Sangre` |
| Texto libre | `Circunstancias`, `Vestimenta`, `Otras observaciones` |

---

## 2. Procesamiento y limpieza

El pipeline de procesamiento se implementó en `src/processing.py` con las funciones `load_data()` y `clean_data()`. Se aplicaron los siguientes pasos:

### 2.1 Extracción de región

La variable `Lugar Hecho` contiene la dirección completa de la desaparición concatenada con guiones:

```
LIMA-LIMA-MIRAFLORES- AV. LARCO 345
```

Para el análisis geográfico agregado se extrajo el primer segmento como variable `region`:

```python
df["region"] = df["Lugar Hecho"].str.split("-").str[0].str.strip().str.title()
```

Esto permitió agrupar los casos a nivel de departamento, revelando que Lima concentra el 36.3% del total de registros, seguida por Cusco (6.8%) y Arequipa (5.3%).

### 2.2 Coordenadas fuera del territorio peruano

Al revisar los campos `Latitud` y `Longitud` se identificaron **4 registros** con coordenadas geográficamente imposibles para el Perú (latitudes positivas o longitudes fuera del rango continental). Estos errores corresponden a fallas en el geocodificado de la dirección de origen.

Se aplicó un bounding box geográfico y se anularon únicamente las coordenadas de los registros afectados, conservando el resto de su información:

```python
PERU_LAT = (-18.5, -0.5)
PERU_LON = (-81.5, -68.5)

bad_coords = (df["Latitud"] < PERU_LAT[0]) | (df["Latitud"] > PERU_LAT[1]) | \
             (df["Longitud"] < PERU_LON[0]) | (df["Longitud"] > PERU_LON[1])

df.loc[bad_coords, ["Latitud", "Longitud"]] = np.nan
```

### 2.3 Valores negativos en Horas para Aparecer

La variable `Horas para Aparecer` debería contener únicamente valores positivos, representando el tiempo transcurrido desde la desaparición hasta la reaparición. Se encontraron **109 registros** con valores negativos, producto de inconsistencias en el orden de las fechas registradas en el sistema fuente.

Dado que el resto de los campos de estos registros son válidos, se optó por anular solo el campo afectado en lugar de eliminar la fila completa:

```python
df.loc[df["Horas para Aparecer"] < 0, "Horas para Aparecer"] = np.nan
```

### 2.4 Duplicados y estandarización

Se eliminaron **16 registros duplicados** detectados tras la carga. Las variables de características físicas (`Tez`, `Fenotipo`, `Cabello`, `Contextura`, entre otras) se estandarizaron a formato título, y las entradas con valor `"Sin Información"` fueron tratadas como datos faltantes.

---

## 3. Dashboard — prototipo Streamlit

La aplicación se desarrolló en Streamlit y está organizada en un panel lateral de filtros globales y tres pestañas de visualización.

### 3.1 Controles del usuario

Todos los filtros del sidebar afectan en tiempo real al conjunto de datos visualizado:

| Control | Tipo | Descripción |
|---|---|---|
| Rango de edad | Slider [0–100] | Restringe los registros por edad de la persona desaparecida |
| Estado de aparición | Selectbox | Filtra entre todos los casos, solo aparecidos o solo no aparecidos |
| Top N regiones | Slider [5–15] | Controla cuántos departamentos se muestran en el gráfico de barras |
| Nube de palabras sobre | Selectbox | Selecciona la columna de texto a analizar |

### 3.2 Pestaña "Explorar"

**Histograma de edad por estado de aparición:** muestra la distribución etaria de los casos segmentada por si la persona apareció o no. Permite observar que los menores de 18 años son el grupo mayoritario y que la distribución de aparecidos y no aparecidos es similar en todos los rangos de edad, sugiriendo que la edad no es un factor determinante en la resolución del caso.

**Casos por mes:** serie temporal con el recuento de denuncias por mes según la fecha del hecho. Permite identificar tendencias y posibles estacionalidades en los registros.

**Tabla filtrada:** vista tabular de los registros activos según los filtros aplicados, con opción de descarga en formato CSV.

### 3.3 Pestaña "Análisis"

**Estado de aparición (donut):** muestra la proporción global de casos resueltos frente a pendientes, actualizada dinámicamente con los filtros.

**Distribución de horas hasta aparecer (box plot):** aplicado únicamente sobre los casos resueltos, permite visualizar la dispersión del tiempo de resolución. La mediana se ubica alrededor de los 7 días, con una larga cola de casos que tardaron semanas o meses.

**Top N departamentos:** barras horizontales ordenadas de mayor a menor frecuencia. Lima domina el ranking, pero departamentos como Cusco y Arequipa presentan frecuencias más altas de lo que su peso poblacional sugeriría.

**Mapa geográfico:** distribución espacial de los casos sobre el mapa del Perú, con puntos de color verde para casos aparecidos y rojo para no aparecidos.

### 3.4 Pestaña "Texto"

**Nube de palabras:** generada sobre las columnas de texto libre del dataset. En `Circunstancias` los términos más frecuentes revelan los contextos más comunes de desaparición. En `Vestimenta` permiten construir un perfil rápido de la indumentaria reportada. El usuario puede alternar entre columnas desde el sidebar.
