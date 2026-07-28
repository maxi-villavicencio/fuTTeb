/* ==========================================================================
   Bet Analyzer AI — Esquema de base de datos
   Script 03: Índices para consultas frecuentes

   Debe ejecutarse DESPUÉS de 01 y 02.

   Criterio: el engine consulta sobre todo por equipo, por partido y por
   fecha (ventanas de "últimos N partidos"). Indexamos:
     - Las foreign keys (aceleran los JOIN y evitan escaneos).
     - Las columnas de filtrado temporal (kickoff_at) y de agrupación.
   Nota: las claves primarias ya generan un índice clustered automático, y las
   restricciones UNIQUE (MatchStatistics, Markets, Extras) ya crean su índice;
   por eso aquí NO se repiten.
   ========================================================================== */

USE BetAnalyzerAI;
GO

/* ----- Seasons: buscar temporadas por competición ----- */
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Seasons_competition_id')
    CREATE INDEX IX_Seasons_competition_id
        ON dbo.Seasons (competition_id);
GO

/* ----- Matches: filtros y JOIN más habituales ----- */
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Matches_competition_id')
    CREATE INDEX IX_Matches_competition_id
        ON dbo.Matches (competition_id);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Matches_season_id')
    CREATE INDEX IX_Matches_season_id
        ON dbo.Matches (season_id);
GO

-- Ventanas temporales: "partidos ordenados por fecha".
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Matches_kickoff_at')
    CREATE INDEX IX_Matches_kickoff_at
        ON dbo.Matches (kickoff_at);
GO

-- "Últimos N partidos de un equipo" (como local o como visitante).
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Matches_home_team_id')
    CREATE INDEX IX_Matches_home_team_id
        ON dbo.Matches (home_team_id, kickoff_at);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Matches_away_team_id')
    CREATE INDEX IX_Matches_away_team_id
        ON dbo.Matches (away_team_id, kickoff_at);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Matches_referee_id')
    CREATE INDEX IX_Matches_referee_id
        ON dbo.Matches (referee_id);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Matches_venue_id')
    CREATE INDEX IX_Matches_venue_id
        ON dbo.Matches (venue_id);
GO

/* ----- MatchStatistics: el acceso más caliente del sistema -----
   (match_id, team_id) ya está cubierto por la restricción UNIQUE.
   Falta el acceso "todas las estadísticas de un equipo" para promedios. */
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_MatchStatistics_team_id')
    CREATE INDEX IX_MatchStatistics_team_id
        ON dbo.MatchStatistics (team_id);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_MatchStatistics_match_id')
    CREATE INDEX IX_MatchStatistics_match_id
        ON dbo.MatchStatistics (match_id);
GO

/* ----- MatchStatisticExtras: acceso por fila de estadística y por métrica ----- */
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_MatchStatisticExtras_match_stat_id')
    CREATE INDEX IX_MatchStatisticExtras_match_stat_id
        ON dbo.MatchStatisticExtras (match_stat_id);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_MatchStatisticExtras_metric_key')
    CREATE INDEX IX_MatchStatisticExtras_metric_key
        ON dbo.MatchStatisticExtras (metric_key);
GO

/* ----- MatchOdds: consultas por partido y por mercado ----- */
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_MatchOdds_match_id')
    CREATE INDEX IX_MatchOdds_match_id
        ON dbo.MatchOdds (match_id);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_MatchOdds_market_id')
    CREATE INDEX IX_MatchOdds_market_id
        ON dbo.MatchOdds (market_id);
GO

PRINT 'Script 03 completado: índices creados.';
GO
