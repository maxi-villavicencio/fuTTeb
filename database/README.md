# Database — Bet Analyzer AI

Artefactos relacionados con la base de datos **SQL Server**: scripts SQL de
creación de esquema, migraciones, datos de referencia (seeds) y documentación
del modelo de datos.

> En esta fase de scaffolding la carpeta está vacía a propósito: **no hay
> modelos ni tablas todavía**. La conexión (SQLAlchemy + pyodbc) ya está
> preparada en el backend y en el engine, pero el esquema se definirá más
> adelante.

Contenido previsto:

- `schema/`      → scripts DDL (creación de tablas, índices, vistas).
- `migrations/`  → cambios versionados del esquema.
- `seeds/`       → datos iniciales / de referencia.
