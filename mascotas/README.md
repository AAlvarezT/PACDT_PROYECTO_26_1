# Patitas — De vuelta a casa

Plataforma para reportar mascotas perdidas y encontradas en Lima, y ayudar a
difundir cada caso en redes sociales para que mas personas puedan reconocerlas.

Proyecto del curso Programacion Avanzada para la Ciencia de Datos.

## Que hace

- Las personas publican un reporte de su mascota (perdida o encontrada) con
  foto, zona, descripcion y datos de contacto.
- La plataforma genera un mensaje listo para compartir y enlaces directos a
  WhatsApp, Facebook, X y Telegram, ademas de un codigo QR para carteles.
- Un panel de analisis muestra indicadores y graficos: estados, distritos,
  especies, evolucion en el tiempo y por que red se difunde mas.
- Opcionalmente, un scraper recolecta anuncios de sitios publicos y los suma
  al tablon, marcados como datos externos.

## Arquitectura

El proyecto esta organizado en capas. Las paginas de la interfaz nunca hablan
con la base de datos directamente: siempre pasan por la capa de servicios.
Esto mantiene el codigo ordenado, testeable y facil de cambiar.

```
Presentacion (Streamlit)        app.py, pages/, ui/
        |
Servicios (logica de negocio)   src/services/
        |
Persistencia                    src/database/  ->  Supabase (PostgreSQL)
        |
Fuente externa                  src/integrations/ (scraping)
```

## Estructura de carpetas

```
patitas/
├── app.py                      Pagina de inicio
├── .env                        Credenciales
├── .env.example                Plantilla de configuracion
├── requirements.txt
├── README.md
│
├── .streamlit/
│   └── config.toml             Tema visual (colores de marca)
│
├── pages/                      Paginas de la aplicacion
│   ├── 1_Publicar.py           Formulario de reporte
│   ├── 2_Tablon.py             Lista con filtros y mapa
│   ├── 3_Difundir.py           Compartir en redes y generar QR
│   └── 4_Analisis.py           Indicadores y graficos
│
├── src/
│   ├── config.py               Configuracion leida del .env
│   │
│   ├── models/
│   │   └── anuncio.py          Modelo de datos de un anuncio
│   │
│   ├── database/
│   │   ├── connection.py       Cliente unico de Supabase
│   │   ├── schema.sql          Tablas anuncios y difusiones
│   │   └── check_connection.py Verifica el setup
│   │
│   ├── services/
│   │   ├── anuncios_service.py  Crear, listar, filtrar anuncios
│   │   ├── difusion_service.py  Enlaces de compartir, QR, registro
│   │   └── metrics_service.py   Calculo de indicadores
│   │
│   ├── integrations/
│   │   ├── parser.py           Deteccion de especie, estado, distrito
│   │   ├── extractors.py       Lectores por sitio (petperu, generico)
│   │   ├── scraper.py          Descarga de sitios publicos
│   │   └── run_scraper.py      Ejecuta el scraping
│   │
│   └── utils/
│       ├── decorators.py       timer, retry, logged
│       ├── errors.py           Excepciones del proyecto
│       └── geo.py              Distritos de Lima y coordenadas
│
├── ui/
│   ├── theme.py                Paleta de colores
│   ├── styles.py               CSS de marca
│   └── components.py           Tarjeta de anuncio, mapa, pie
│
└── tests/
    ├── test_parser.py          Pruebas del parser
    └── test_services.py        Pruebas de los servicios
```

## Base de datos

Dos tablas relacionadas:

- `anuncios`: cada mascota perdida o encontrada. El campo `origen` distingue si
  la publico un usuario o si vino del scraping.
- `difusiones`: registro de cada vez que un anuncio se comparte en una red.
  Se relaciona con `anuncios` por clave foranea, lo que permite analizar que
  canales difunden mas.

El esquema completo, con indices y politicas de seguridad, esta en
`src/database/schema.sql`.

## Instalacion

Requiere Python 3.10 o superior y una cuenta gratuita de Supabase.

### 1. Instalar dependencias

```
pip install -r requirements.txt
```

### 2. Configurar credenciales

El archivo `.env` ya viene con la URL y la clave de Supabase. Si necesitas
cambiarlas, editalo:

```
SUPABASE_URL=https://TU-PROYECTO.supabase.co
SUPABASE_KEY=tu-clave-publica
```

El `.env` esta en `.gitignore`, asi que las credenciales no se suben al
repositorio. La plantilla publica es `.env.example`.

### 3. Crear las tablas en Supabase

1. Entra a tu proyecto en Supabase.
2. Abre el SQL Editor.
3. Copia y ejecuta el contenido de `src/database/schema.sql`.
4. Luego ejecuta `src/database/storage_setup.sql` para crear el bucket de
   fotos. (Tambien puedes crearlo desde la interfaz: Storage > New bucket >
   nombre `fotos-mascotas` > marcar como publico.)

### 4. Verificar la conexion

```
python -m src.database.check_connection
```

Muestra el numero de filas de cada tabla si todo esta bien.

## Uso

### Ejecutar la aplicacion

```
streamlit run app.py
```

Se abre en el navegador. Usa el menu de la izquierda para navegar entre
Publicar, Tablon, Difundir y Analisis.

### Recolectar anuncios de sitios publicos (opcional)

1. En `.env`, completa `SCRAPER_URLS` con URLs publicas separadas por coma.
   Revisa el robots.txt y los terminos de cada sitio antes de incluirlo.
2. Ejecuta:

```
python -m src.integrations.run_scraper
```

Los anuncios se guardan en la tabla `anuncios` marcados como origen scraping.

## Pruebas

```
pytest tests/ -v
```

Las pruebas no requieren conexion a la base: validan la deteccion de texto, la
validacion de anuncios, la generacion de mensajes y enlaces, y el calculo de
indicadores de forma aislada.

## Decisiones de diseno

**Difundir sin APIs de pago.** Para compartir en redes no se usan las APIs
oficiales de Facebook o X (de pago o con aprobacion lenta), sino enlaces de
comparticion: URLs que abren la red con el mensaje ya cargado. No requieren
credenciales, son gratuitas y funcionan de inmediato.

**Capas desacopladas.** La interfaz usa servicios, los servicios usan la base.
Cambiar de base de datos o agregar una fuente de datos no obliga a tocar la
interfaz.

**Indexar, no copiar.** El scraper guarda una referencia al anuncio externo
(su enlace y datos minimos), no una copia del contenido. La plataforma dirige
a la fuente original.

**Fotos en Storage, no en la tabla.** Las fotos se guardan en Supabase Storage
(almacenamiento de archivos del proyecto) y la tabla solo guarda su URL
publica. Guardar binarios grandes dentro de las filas inflaria la base y
ralentizaria las consultas.

**Configuracion por entorno.** Ninguna credencial vive en el codigo; todo se
lee del `.env`.

## Calidad del codigo

- Decoradores reutilizables (`timer`, `retry`, `logged`) en `src/utils`.
- Manejo de errores con excepciones propias y mensajes claros.
- Estructura modular por responsabilidad, no por entidad.
- Pruebas unitarias de la logica que no depende de servicios externos.
