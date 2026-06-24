-- ===========================================================================
--  Esquema de base de datos - Proyecto Patitas
--  Curso: Programacion Avanzada para la Ciencia de Datos
-- ===========================================================================
--
--  Dos tablas relacionadas:
--
--    anuncios    Una mascota perdida o encontrada. El origen puede ser un
--                usuario que publica en la plataforma o el scraping de un
--                sitio externo.
--
--    difusiones  Registro de cada vez que un anuncio se comparte en una red
--                social. Se relaciona con anuncios por clave foranea, lo que
--                permite analizar que canales difunden mas.
--
--  Como aplicarlo:
--    1. Entra a tu proyecto en Supabase.
--    2. Abre el SQL Editor.
--    3. Pega este archivo completo y ejecutalo.
--
--  Nota: este esquema reemplaza la tabla 'external_posts' de versiones
--  anteriores. Si la tienes y no la necesitas, puedes eliminarla con:
--      drop table if exists external_posts;
-- ===========================================================================

create extension if not exists "uuid-ossp";

-- ---------------------------------------------------------------------------
-- Tabla 1: anuncios
-- ---------------------------------------------------------------------------
create table if not exists anuncios (
    id                 uuid primary key default uuid_generate_v4(),

    -- Origen del anuncio
    origen             text not null default 'usuario',  -- usuario | scraping
    fuente             text,                              -- sitio si es scraping
    url_original       text,                              -- enlace original

    -- Datos de la mascota
    nombre             text,
    especie            text default 'otro',               -- perro | gato | otro
    raza               text,
    color              text,
    sexo               text default 'desconocido',        -- macho | hembra | desconocido
    tamano             text,                              -- pequeno | mediano | grande

    -- Estado del caso
    estado             text not null default 'perdido',   -- perdido | encontrado | reunido

    -- Ubicacion y fecha del hecho
    distrito           text,
    referencia_lugar   text,
    fecha_evento       date,

    -- Contenido
    descripcion        text,
    foto_url           text,
    tiene_recompensa   boolean default false,
    monto_recompensa   numeric,

    -- Contacto de quien publica
    contacto_nombre    text,
    contacto_telefono  text,
    contacto_email     text,

    -- Metadatos
    fecha_publicacion  timestamptz default now(),
    vistas             integer default 0,

    -- Un mismo anuncio externo no se indexa dos veces.
    -- Para anuncios de usuarios url_original es NULL y PostgreSQL permite
    -- multiples valores NULL en una restriccion unica.
    constraint anuncios_url_unica unique (url_original)
);

-- Indices para acelerar los filtros mas usados en el tablon y el analisis.
create index if not exists idx_anuncios_estado    on anuncios (estado);
create index if not exists idx_anuncios_especie   on anuncios (especie);
create index if not exists idx_anuncios_distrito  on anuncios (distrito);
create index if not exists idx_anuncios_origen    on anuncios (origen);
create index if not exists idx_anuncios_fecha     on anuncios (fecha_publicacion);

-- ---------------------------------------------------------------------------
-- Tabla 2: difusiones  (relacionada con anuncios)
-- ---------------------------------------------------------------------------
create table if not exists difusiones (
    id              uuid primary key default uuid_generate_v4(),
    anuncio_id      uuid not null references anuncios(id) on delete cascade,
    canal           text not null,            -- whatsapp | facebook | x | telegram
    fecha_difusion  timestamptz default now()
);

create index if not exists idx_difusiones_anuncio on difusiones (anuncio_id);
create index if not exists idx_difusiones_canal   on difusiones (canal);

-- ---------------------------------------------------------------------------
-- Seguridad a nivel de fila (RLS)
-- ---------------------------------------------------------------------------
-- En esta plataforma cualquier persona puede publicar y consultar anuncios
-- sin iniciar sesion, por lo que se permite lectura e insercion publicas.
-- En un entorno de produccion real conviene anadir autenticacion.

alter table anuncios   enable row level security;
alter table difusiones enable row level security;

drop policy if exists "anuncios lectura publica" on anuncios;
create policy "anuncios lectura publica"
    on anuncios for select using (true);

drop policy if exists "anuncios insercion publica" on anuncios;
create policy "anuncios insercion publica"
    on anuncios for insert with check (true);

drop policy if exists "anuncios actualizacion publica" on anuncios;
create policy "anuncios actualizacion publica"
    on anuncios for update using (true);

drop policy if exists "difusiones lectura publica" on difusiones;
create policy "difusiones lectura publica"
    on difusiones for select using (true);

drop policy if exists "difusiones insercion publica" on difusiones;
create policy "difusiones insercion publica"
    on difusiones for insert with check (true);
