/* ==========================================================================
   Bet Analyzer AI — Esquema de base de datos
   Script 02: Foreign keys (relaciones entre tablas)

   Debe ejecutarse DESPUÉS de 01_create_tables.sql.
   Cada FK se agrega con IF NOT EXISTS para que re-ejecutar no falle.

   Nota sobre acciones referenciales:
     - No se usan cascadas de borrado. Los datos crudos son históricos y no
       deben borrarse en cascada por accidente. Los borrados se harán de forma
       controlada. Además, Matches referencia Teams por DOS columnas
       (home/away), lo que provocaría "multiple cascade paths" en SQL Server;
       por eso se deja NO ACTION (comportamiento por defecto).
   ========================================================================== */

USE BetAnalyzerAI;
GO

/* ----- Seasons.competition_id -> Competitions.id ----- */
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Seasons_Competitions')
    ALTER TABLE dbo.Seasons
        ADD CONSTRAINT FK_Seasons_Competitions
        FOREIGN KEY (competition_id) REFERENCES dbo.Competitions (id);
GO

/* ----- Matches.competition_id -> Competitions.id ----- */
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Matches_Competitions')
    ALTER TABLE dbo.Matches
        ADD CONSTRAINT FK_Matches_Competitions
        FOREIGN KEY (competition_id) REFERENCES dbo.Competitions (id);
GO

/* ----- Matches.season_id -> Seasons.id ----- */
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Matches_Seasons')
    ALTER TABLE dbo.Matches
        ADD CONSTRAINT FK_Matches_Seasons
        FOREIGN KEY (season_id) REFERENCES dbo.Seasons (id);
GO

/* ----- Matches.home_team_id -> Teams.id ----- */
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Matches_HomeTeam')
    ALTER TABLE dbo.Matches
        ADD CONSTRAINT FK_Matches_HomeTeam
        FOREIGN KEY (home_team_id) REFERENCES dbo.Teams (id);
GO

/* ----- Matches.away_team_id -> Teams.id ----- */
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Matches_AwayTeam')
    ALTER TABLE dbo.Matches
        ADD CONSTRAINT FK_Matches_AwayTeam
        FOREIGN KEY (away_team_id) REFERENCES dbo.Teams (id);
GO

/* ----- Matches.referee_id -> Referees.id (nullable) ----- */
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Matches_Referees')
    ALTER TABLE dbo.Matches
        ADD CONSTRAINT FK_Matches_Referees
        FOREIGN KEY (referee_id) REFERENCES dbo.Referees (id);
GO

/* ----- Matches.venue_id -> Venues.id (nullable) ----- */
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Matches_Venues')
    ALTER TABLE dbo.Matches
        ADD CONSTRAINT FK_Matches_Venues
        FOREIGN KEY (venue_id) REFERENCES dbo.Venues (id);
GO

/* ----- MatchStatistics.match_id -> Matches.id ----- */
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_MatchStatistics_Matches')
    ALTER TABLE dbo.MatchStatistics
        ADD CONSTRAINT FK_MatchStatistics_Matches
        FOREIGN KEY (match_id) REFERENCES dbo.Matches (id);
GO

/* ----- MatchStatistics.team_id -> Teams.id ----- */
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_MatchStatistics_Team')
    ALTER TABLE dbo.MatchStatistics
        ADD CONSTRAINT FK_MatchStatistics_Team
        FOREIGN KEY (team_id) REFERENCES dbo.Teams (id);
GO

/* ----- MatchStatistics.opponent_team_id -> Teams.id ----- */
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_MatchStatistics_Opponent')
    ALTER TABLE dbo.MatchStatistics
        ADD CONSTRAINT FK_MatchStatistics_Opponent
        FOREIGN KEY (opponent_team_id) REFERENCES dbo.Teams (id);
GO

/* ----- MatchStatisticExtras.match_stat_id -> MatchStatistics.id ----- */
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_MatchStatisticExtras_Stat')
    ALTER TABLE dbo.MatchStatisticExtras
        ADD CONSTRAINT FK_MatchStatisticExtras_Stat
        FOREIGN KEY (match_stat_id) REFERENCES dbo.MatchStatistics (id);
GO

/* ----- MatchOdds.match_id -> Matches.id ----- */
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_MatchOdds_Matches')
    ALTER TABLE dbo.MatchOdds
        ADD CONSTRAINT FK_MatchOdds_Matches
        FOREIGN KEY (match_id) REFERENCES dbo.Matches (id);
GO

/* ----- MatchOdds.market_id -> Markets.id ----- */
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_MatchOdds_Markets')
    ALTER TABLE dbo.MatchOdds
        ADD CONSTRAINT FK_MatchOdds_Markets
        FOREIGN KEY (market_id) REFERENCES dbo.Markets (id);
GO

PRINT 'Script 02 completado: foreign keys creadas.';
GO
