/* ==========================================================================
   Bet Analyzer AI — Migración de esquema
   Script 06: columnas nuevas en MatchStatistics para datos reales (API-Football)

   Motivo: la carga real desde API-Football trae más estadísticas que el seed.
   Se agregan como COLUMNAS TIPADAS solo las que vamos a usar o promover:

     - expected_goals (xG): lo usaremos en el engine -> columna DECIMAL.
     - offsides: métrica simple y candidata a mercado futuro -> columna INT.

   DECISIÓN DE DISEÑO (documentada):
   El resto de campos que devuelve la API y que HOY no usa el engine
   (Shots off Goal, Blocked Shots, Shots insidebox/outsidebox, Total passes,
   Passes accurate, Passes %, Goalkeeper Saves, goals_prevented) NO se agregan
   como columnas: se guardan en la tabla MatchStatisticExtras (clave-valor),
   que es el "borrador" para métricas experimentales. Regla del proyecto: si
   alguna de esas métricas pasa a usarse en producción, se PROMUEVE a columna
   tipada aquí. Así MatchStatistics no se llena de columnas sin uso.

   Idempotente: cada columna se agrega solo si no existe (IF NOT EXISTS sobre
   sys.columns). No toca datos existentes ni el seed.
   ========================================================================== */

USE BetAnalyzerAI;
GO

/* --- expected_goals (xG) ------------------------------------------------- */
IF NOT EXISTS (
    SELECT 1 FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.MatchStatistics') AND name = 'expected_goals'
)
BEGIN
    ALTER TABLE dbo.MatchStatistics ADD expected_goals DECIMAL(5,2) NULL;
    PRINT 'Columna expected_goals agregada.';
END
ELSE
    PRINT 'La columna expected_goals ya existe; no se hace nada.';
GO

/* --- offsides ------------------------------------------------------------ */
IF NOT EXISTS (
    SELECT 1 FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.MatchStatistics') AND name = 'offsides'
)
BEGIN
    ALTER TABLE dbo.MatchStatistics ADD offsides INT NULL;
    PRINT 'Columna offsides agregada.';
END
ELSE
    PRINT 'La columna offsides ya existe; no se hace nada.';
GO

PRINT 'Script 06 completado.';
GO
