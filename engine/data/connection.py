"""Conexión del engine a SQL Server.

Crea el ``Engine`` de SQLAlchemy (dialecto ``mssql+pyodbc``) que usan los
repositorios. La cadena de conexión se obtiene por variables de entorno; el
engine NUNCA la hardcodea ni depende del backend.

Nota: este módulo es independiente del backend. Backend y engine pueden
compartir la misma base de datos, pero cada uno abre su propia conexión.
"""

# TODO: leer la cadena de conexión desde variables de entorno y crear el
# Engine de SQLAlchemy (mssql+pyodbc). Sin modelos ni tablas todavía.
