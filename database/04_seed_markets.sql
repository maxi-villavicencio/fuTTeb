/* ==========================================================================
   Bet Analyzer AI — Esquema de base de datos
   Script 04: Datos semilla de la tabla Markets (mercados de la v1)

   Debe ejecutarse DESPUÉS de 01, 02 y 03.

   Inserta los 4 mercados de análisis de la v1. El 'code' es el puente estable
   con los plugins del engine (engine/markets/<code>/) y es UNIQUE, por lo que
   volver a ejecutar este script NO duplica filas (cada INSERT está protegido
   con NOT EXISTS por code).
   ========================================================================== */

USE BetAnalyzerAI;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.Markets WHERE code = N'goals')
    INSERT INTO dbo.Markets (code, name, description)
    VALUES (N'goals',   N'Goles',   N'Mercado de goles del partido (totales, over/under, etc.).');
GO

IF NOT EXISTS (SELECT 1 FROM dbo.Markets WHERE code = N'corners')
    INSERT INTO dbo.Markets (code, name, description)
    VALUES (N'corners', N'Córners', N'Mercado de córners del partido.');
GO

IF NOT EXISTS (SELECT 1 FROM dbo.Markets WHERE code = N'cards')
    INSERT INTO dbo.Markets (code, name, description)
    VALUES (N'cards',   N'Tarjetas', N'Mercado de tarjetas (amarillas y rojas) del partido.');
GO

IF NOT EXISTS (SELECT 1 FROM dbo.Markets WHERE code = N'btts')
    INSERT INTO dbo.Markets (code, name, description)
    VALUES (N'btts',    N'Ambos equipos marcan (BTTS)', N'Mercado "Both Teams To Score": ambos equipos anotan al menos un gol.');
GO

PRINT 'Script 04 completado: mercados semilla insertados (goals, corners, cards, btts).';
GO

-- Comprobación rápida (opcional): listar los mercados cargados.
SELECT id, code, name FROM dbo.Markets ORDER BY id;
GO
