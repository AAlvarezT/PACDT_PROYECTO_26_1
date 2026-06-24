-- ===========================================================================
--  Almacenamiento de fotos - Proyecto Patitas
-- ===========================================================================
--
--  Crea el bucket de Supabase Storage donde se guardan las fotos de las
--  mascotas, y las politicas que permiten subirlas y verlas.
--
--  Las fotos se guardan como archivos en este bucket; la tabla 'anuncios'
--  solo guarda la URL publica de cada foto. Esto mantiene la base ligera.
--
--  Como aplicarlo:
--    1. Entra a tu proyecto en Supabase.
--    2. Abre el SQL Editor.
--    3. Pega este archivo y ejecutalo (despues de schema.sql).
--
--  Alternativa por la interfaz:
--    Storage > New bucket > nombre 'fotos-mascotas' > marcar como publico.
-- ===========================================================================

-- Crear el bucket publico (si no existe).
insert into storage.buckets (id, name, public)
values ('fotos-mascotas', 'fotos-mascotas', true)
on conflict (id) do nothing;

-- Permitir que cualquiera vea las fotos (lectura publica).
drop policy if exists "fotos lectura publica" on storage.objects;
create policy "fotos lectura publica"
    on storage.objects for select
    using (bucket_id = 'fotos-mascotas');

-- Permitir subir fotos al bucket (insercion publica).
-- En un entorno de produccion real conviene restringir esto a usuarios
-- autenticados; para esta plataforma academica se permite de forma abierta.
drop policy if exists "fotos insercion publica" on storage.objects;
create policy "fotos insercion publica"
    on storage.objects for insert
    with check (bucket_id = 'fotos-mascotas');
