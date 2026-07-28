/* ==========================================================================
   Bet Analyzer AI — Datos de PRUEBA (seed de desarrollo)
   Script 05: Poblado con partidos ficticios pero realistas de la
              Liga Profesional Argentina (temporada 2025).

   ⚠️  DATOS DE PRUEBA, NO REALES. Sirven solo para desarrollar y probar el
       engine hasta que carguemos datos reales. Los valores son plausibles
       (rangos típicos de la liga) pero inventados.

   Contenido:
     - 1 competición (Liga Profesional Argentina) y 1 temporada (2025).
     - 8 equipos.
     - 20 partidos.
     - 40 filas en MatchStatistics (2 por partido, una por equipo).

   Idempotente: todo se inserta con NOT EXISTS sobre external_ref (y sobre
   (match_id, team_id) en las estadísticas), así que re-ejecutar NO duplica.

   Orden de inserción (respeta las FKs):
     Competición -> Temporada -> Equipos -> Partidos -> Estadísticas.

   Nota de diseño para el engine: los córners tienen una TENDENCIA CONSISTENTE
   por equipo, para que haya un patrón real que detectar:
       Altos:  River (~7-8), Racing (~7), Vélez (~6-7)
       Medios: Boca (~5-6), Estudiantes (~5)
       Bajos:  Lanús (~4-5), San Lorenzo (~2-4), Independiente (~3-4)
   ========================================================================== */

USE BetAnalyzerAI;
GO

/* --------------------------------------------------------------------------
   1. Competición
   -------------------------------------------------------------------------- */
IF NOT EXISTS (SELECT 1 FROM dbo.Competitions WHERE external_ref = N'TEST-LPF')
    INSERT INTO dbo.Competitions (name, country, type, external_ref)
    VALUES (N'Liga Profesional Argentina', N'Argentina', N'liga', N'TEST-LPF');
GO

/* --------------------------------------------------------------------------
   2. Temporada 2025 (cuelga de la competición)
   -------------------------------------------------------------------------- */
IF NOT EXISTS (SELECT 1 FROM dbo.Seasons WHERE external_ref = N'TEST-LPF-2025')
    INSERT INTO dbo.Seasons (competition_id, name, start_date, end_date, is_current, external_ref)
    SELECT c.id, N'2025', '2025-01-20', '2025-12-15', 1, N'TEST-LPF-2025'
    FROM dbo.Competitions c
    WHERE c.external_ref = N'TEST-LPF';
GO

/* --------------------------------------------------------------------------
   3. Equipos (8). Se cargan en una tabla temporal y se insertan los que falten.
   -------------------------------------------------------------------------- */
IF OBJECT_ID('tempdb..#TeamSeed') IS NOT NULL DROP TABLE #TeamSeed;
CREATE TABLE #TeamSeed
(
    name         NVARCHAR(150),
    short_name   NVARCHAR(50),
    country      NVARCHAR(100),
    external_ref NVARCHAR(100)
);

INSERT INTO #TeamSeed (name, short_name, country, external_ref) VALUES
    (N'Club Atlético River Plate',    N'River',        N'Argentina', N'TEST-TEAM-RIV'),
    (N'Club Atlético Boca Juniors',   N'Boca',         N'Argentina', N'TEST-TEAM-BOC'),
    (N'Club Atlético San Lorenzo',    N'San Lorenzo',  N'Argentina', N'TEST-TEAM-SLO'),
    (N'Club Atlético Lanús',          N'Lanús',        N'Argentina', N'TEST-TEAM-LAN'),
    (N'Racing Club',                  N'Racing',       N'Argentina', N'TEST-TEAM-RAC'),
    (N'Club Atlético Independiente',  N'Independiente',N'Argentina', N'TEST-TEAM-IND'),
    (N'Estudiantes de La Plata',      N'Estudiantes',  N'Argentina', N'TEST-TEAM-EST'),
    (N'Club Atlético Vélez Sarsfield',N'Vélez',        N'Argentina', N'TEST-TEAM-VEL');

INSERT INTO dbo.Teams (name, short_name, country, external_ref)
SELECT ts.name, ts.short_name, ts.country, ts.external_ref
FROM #TeamSeed ts
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.Teams t WHERE t.external_ref = ts.external_ref
);
GO

/* --------------------------------------------------------------------------
   4. Partidos + estadísticas: definición completa en una tabla temporal.
      Cada fila describe un partido con TODOS los números de ambos equipos.
      Prefijo de columnas: h_ = local (home), a_ = visitante (away).
      La posesión (h_poss + a_poss) suma ~100.00.
   -------------------------------------------------------------------------- */
IF OBJECT_ID('tempdb..#FixtureSeed') IS NOT NULL DROP TABLE #FixtureSeed;
CREATE TABLE #FixtureSeed
(
    ext_ref   NVARCHAR(100),
    matchday  INT,
    kickoff   DATETIME2(0),
    home_ref  NVARCHAR(100),
    away_ref  NVARCHAR(100),
    h_goals   INT, a_goals   INT,
    h_corners INT, a_corners INT,
    h_yellow  INT, a_yellow  INT,
    h_red     INT, a_red     INT,
    h_shots   INT, a_shots   INT,
    h_sot     INT, a_sot     INT,     -- tiros al arco (shots on target)
    h_poss    DECIMAL(5,2), a_poss DECIMAL(5,2),
    h_fouls   INT, a_fouls   INT
);

INSERT INTO #FixtureSeed
    (ext_ref, matchday, kickoff, home_ref, away_ref,
     h_goals, a_goals, h_corners, a_corners, h_yellow, a_yellow, h_red, a_red,
     h_shots, a_shots, h_sot, a_sot, h_poss, a_poss, h_fouls, a_fouls)
VALUES
    -- Fecha 1
    (N'TEST-M-001', 1, '2025-02-01T21:30:00', N'TEST-TEAM-RIV', N'TEST-TEAM-BOC', 2,1, 8,5, 2,3, 0,0, 15, 9, 6,3, 55.5,44.5, 12,14),
    (N'TEST-M-002', 1, '2025-02-02T17:00:00', N'TEST-TEAM-RAC', N'TEST-TEAM-SLO', 1,0, 7,3, 1,2, 0,0, 13, 7, 5,2, 58.0,42.0, 10,13),
    (N'TEST-M-003', 1, '2025-02-02T19:15:00', N'TEST-TEAM-LAN', N'TEST-TEAM-IND', 1,1, 5,3, 3,2, 0,0, 11,10, 4,4, 49.5,50.5, 15,13),
    (N'TEST-M-004', 1, '2025-02-03T21:00:00', N'TEST-TEAM-EST', N'TEST-TEAM-VEL', 0,2, 5,6, 3,2, 0,1,  9,14, 2,6, 47.0,53.0, 16,11),
    -- Fecha 2
    (N'TEST-M-005', 2, '2025-02-08T21:30:00', N'TEST-TEAM-BOC', N'TEST-TEAM-RAC', 1,1, 6,6, 2,3, 0,0, 12,12, 4,5, 51.5,48.5, 13,12),
    (N'TEST-M-006', 2, '2025-02-09T17:00:00', N'TEST-TEAM-SLO', N'TEST-TEAM-LAN', 2,0, 4,4, 2,3, 0,0, 12, 8, 5,2, 53.0,47.0, 11,14),
    (N'TEST-M-007', 2, '2025-02-09T19:15:00', N'TEST-TEAM-IND', N'TEST-TEAM-EST', 0,1, 3,5, 3,2, 0,0,  8,12, 2,5, 46.5,53.5, 14,10),
    (N'TEST-M-008', 2, '2025-02-10T21:00:00', N'TEST-TEAM-VEL', N'TEST-TEAM-RIV', 2,2, 7,7, 2,2, 0,0, 13,15, 5,6, 50.0,50.0, 12,12),
    -- Fecha 3
    (N'TEST-M-009', 3, '2025-02-15T21:30:00', N'TEST-TEAM-RIV', N'TEST-TEAM-RAC', 3,1, 8,6, 1,4, 0,1, 17,10, 7,4, 57.5,42.5,  9,16),
    (N'TEST-M-010', 3, '2025-02-16T17:00:00', N'TEST-TEAM-BOC', N'TEST-TEAM-SLO', 2,0, 6,2, 2,2, 0,0, 14, 7, 6,2, 56.0,44.0, 12,13),
    (N'TEST-M-011', 3, '2025-02-16T19:15:00', N'TEST-TEAM-LAN', N'TEST-TEAM-EST', 1,2, 5,5, 3,2, 0,0, 11,13, 4,5, 48.5,51.5, 15,11),
    (N'TEST-M-012', 3, '2025-02-17T21:00:00', N'TEST-TEAM-IND', N'TEST-TEAM-VEL', 1,1, 4,6, 3,3, 0,0, 10,13, 3,5, 45.5,54.5, 13,12),
    -- Fecha 4
    (N'TEST-M-013', 4, '2025-02-22T21:30:00', N'TEST-TEAM-RAC', N'TEST-TEAM-LAN', 2,1, 7,4, 2,4, 0,1, 14,10, 5,4, 54.5,45.5, 11,15),
    (N'TEST-M-014', 4, '2025-02-23T17:00:00', N'TEST-TEAM-SLO', N'TEST-TEAM-IND', 0,0, 4,3, 3,3, 0,0,  9, 9, 3,2, 50.5,49.5, 13,13),
    (N'TEST-M-015', 4, '2025-02-23T19:15:00', N'TEST-TEAM-EST', N'TEST-TEAM-RIV', 1,1, 5,7, 2,1, 0,0, 10,15, 4,6, 47.5,52.5, 14,10),
    (N'TEST-M-016', 4, '2025-02-24T21:00:00', N'TEST-TEAM-VEL', N'TEST-TEAM-BOC', 2,1, 7,5, 2,3, 0,0, 14,11, 6,4, 55.0,45.0, 12,13),
    -- Fecha 5
    (N'TEST-M-017', 5, '2025-03-01T21:30:00', N'TEST-TEAM-RIV', N'TEST-TEAM-IND', 3,0, 8,3, 1,3, 0,0, 18, 7, 7,2, 60.0,40.0,  9,15),
    (N'TEST-M-018', 5, '2025-03-02T17:00:00', N'TEST-TEAM-BOC', N'TEST-TEAM-EST', 1,0, 6,5, 2,2, 0,0, 13,10, 5,3, 52.5,47.5, 12,12),
    (N'TEST-M-019', 5, '2025-03-02T19:15:00', N'TEST-TEAM-RAC', N'TEST-TEAM-VEL', 2,2, 7,6, 3,2, 0,1, 14,13, 5,5, 53.5,46.5, 12,13),
    (N'TEST-M-020', 5, '2025-03-03T21:00:00', N'TEST-TEAM-LAN', N'TEST-TEAM-SLO', 1,0, 5,3, 2,3, 0,0, 12, 8, 4,2, 51.0,49.0, 14,13);

/* --------------------------------------------------------------------------
   4.a Insertar los partidos (resuelve competición, temporada y equipos por ref)

   IMPORTANTE: desde aquí y hasta el final del bloque NO hay GO. La tabla
   temporal #FixtureSeed se crea y se consume dentro del MISMO lote, para que
   no dependa de que la temporal "sobreviva" a un GO (eso hacía que partidos y
   estadísticas quedaran en 0).
   -------------------------------------------------------------------------- */
INSERT INTO dbo.Matches
    (competition_id, season_id, matchday, kickoff_at, home_team_id, away_team_id, status, external_ref)
SELECT c.id, s.id, f.matchday, f.kickoff, ht.id, at.id, N'jugado', f.ext_ref
FROM #FixtureSeed f
JOIN dbo.Competitions c ON c.external_ref = N'TEST-LPF'
JOIN dbo.Seasons      s ON s.external_ref = N'TEST-LPF-2025'
JOIN dbo.Teams       ht ON ht.external_ref = f.home_ref
JOIN dbo.Teams       at ON at.external_ref = f.away_ref
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.Matches m WHERE m.external_ref = f.ext_ref
);

/* --------------------------------------------------------------------------
   4.b Estadísticas del EQUIPO LOCAL (is_home = 1)
       goals_conceded del local = goles del visitante.
   -------------------------------------------------------------------------- */
INSERT INTO dbo.MatchStatistics
    (match_id, team_id, opponent_team_id, is_home,
     goals, goals_conceded, corners, yellow_cards, red_cards,
     shots, shots_on_target, possession, fouls)
SELECT m.id, ht.id, at.id, 1,
       f.h_goals, f.a_goals, f.h_corners, f.h_yellow, f.h_red,
       f.h_shots, f.h_sot, f.h_poss, f.h_fouls
FROM #FixtureSeed f
JOIN dbo.Matches m  ON m.external_ref = f.ext_ref
JOIN dbo.Teams  ht  ON ht.external_ref = f.home_ref
JOIN dbo.Teams  at  ON at.external_ref = f.away_ref
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.MatchStatistics x
    WHERE x.match_id = m.id AND x.team_id = ht.id
);

/* --------------------------------------------------------------------------
   4.c Estadísticas del EQUIPO VISITANTE (is_home = 0)
       goals_conceded del visitante = goles del local.
   -------------------------------------------------------------------------- */
INSERT INTO dbo.MatchStatistics
    (match_id, team_id, opponent_team_id, is_home,
     goals, goals_conceded, corners, yellow_cards, red_cards,
     shots, shots_on_target, possession, fouls)
SELECT m.id, at.id, ht.id, 0,
       f.a_goals, f.h_goals, f.a_corners, f.a_yellow, f.a_red,
       f.a_shots, f.a_sot, f.a_poss, f.a_fouls
FROM #FixtureSeed f
JOIN dbo.Matches m  ON m.external_ref = f.ext_ref
JOIN dbo.Teams  ht  ON ht.external_ref = f.home_ref
JOIN dbo.Teams  at  ON at.external_ref = f.away_ref
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.MatchStatistics x
    WHERE x.match_id = m.id AND x.team_id = at.id
);
GO

/* ==========================================================================
   5. AMPLIACIÓN: partidos generados para tener MUESTRA SUFICIENTE
   --------------------------------------------------------------------------
   Objetivo: que CADA equipo tenga al menos 10 partidos de local y 10 de
   visitante (el engine ahora exige 8 para marcar el índice como confiable).

   Cómo: cada equipo hospeda a cada uno de los otros 7 equipos DOS veces
   (doble ronda de local). Eso da 8 x 7 x 2 = 112 partidos generados; cada
   equipo queda con 14 partidos de local y 14 de visitante (más los 20
   originales). Se mantiene la TENDENCIA de córners por equipo (River/Racing/
   Vélez generan más; San Lorenzo/Independiente menos) mediante un "nivel"
   base por equipo, con una variación determinista según el número de partido.

   Todo va en UN SOLO LOTE (sin GO) porque usa tablas temporales. Las fechas
   se generan con DATEADD (no literales), así que no dependen del idioma.
   Idempotente: cada partido tiene un external_ref único 'TEST-G-XXX-YYY-n'.
   -------------------------------------------------------------------------- */

-- Nivel base de córners que GENERA cada equipo (tendencia consistente).
IF OBJECT_ID('tempdb..#TeamBase') IS NOT NULL DROP TABLE #TeamBase;
CREATE TABLE #TeamBase (external_ref NVARCHAR(100), lvl INT);
INSERT INTO #TeamBase (external_ref, lvl) VALUES
    (N'TEST-TEAM-RIV', 7),
    (N'TEST-TEAM-RAC', 6),
    (N'TEST-TEAM-VEL', 6),
    (N'TEST-TEAM-BOC', 5),
    (N'TEST-TEAM-EST', 5),
    (N'TEST-TEAM-LAN', 4),
    (N'TEST-TEAM-SLO', 3),
    (N'TEST-TEAM-IND', 3);

-- Generar los 112 partidos con sus estadísticas ya calculadas.
IF OBJECT_ID('tempdb..#GenFixtures') IS NOT NULL DROP TABLE #GenFixtures;
;WITH reps AS (
    SELECT 1 AS r UNION ALL SELECT 2       -- dos veces como local cada par
),
pares AS (
    SELECT h.external_ref AS home_ref,
           a.external_ref AS away_ref,
           RIGHT(h.external_ref, 3) AS home_code,
           RIGHT(a.external_ref, 3) AS away_code,
           h.lvl AS home_lvl,
           a.lvl AS away_lvl,
           r.r   AS rep,
           ROW_NUMBER() OVER (ORDER BY h.external_ref, a.external_ref, r.r) AS seq
    FROM #TeamBase h
    CROSS JOIN #TeamBase a
    CROSS JOIN reps r
    WHERE h.external_ref <> a.external_ref
),
calc AS (
    SELECT p.*,
           N'TEST-G-' + p.home_code + N'-' + p.away_code + N'-' + CAST(p.rep AS NVARCHAR(1)) AS ext_ref,
           DATEADD(DAY, p.seq, CAST('2025-03-10T20:00:00' AS DATETIME2(0))) AS kickoff,
           -- córners: nivel del equipo + boost de local (+1) + variación (-2..+2)
           (p.home_lvl + 1 + ((p.seq * 3) % 5) - 2) AS hc_raw,
           (p.away_lvl +      ((p.seq * 7) % 5) - 2) AS ac_raw,
           -- goles, tarjetas y faltas: valores plausibles y deterministas
           ((p.seq * 5)  % 4)              AS h_goals,
           ((p.seq * 11) % 3)              AS a_goals,
           (1 + (p.seq % 4))               AS h_yellow,
           (1 + ((p.seq * 3) % 4))         AS a_yellow,
           (CASE WHEN p.seq % 13 = 0 THEN 1 ELSE 0 END) AS h_red,
           (CASE WHEN p.seq % 17 = 0 THEN 1 ELSE 0 END) AS a_red,
           (9  + (p.seq % 8))              AS h_fouls,
           (10 + ((p.seq * 2) % 8))        AS a_fouls,
           -- posesión del local: 50 + dif. de nivel + boost + variación
           (50 + (p.home_lvl - p.away_lvl) + 2 + ((p.seq % 5) - 2)) AS h_poss_raw
    FROM pares p
)
SELECT
    ext_ref,
    kickoff,
    home_ref,
    away_ref,
    -- córners recortados a un rango realista [1, 10]
    CASE WHEN hc_raw < 1 THEN 1 WHEN hc_raw > 10 THEN 10 ELSE hc_raw END AS h_corners,
    CASE WHEN ac_raw < 1 THEN 1 WHEN ac_raw > 10 THEN 10 ELSE ac_raw END AS a_corners,
    h_goals, a_goals, h_yellow, a_yellow, h_red, a_red, h_fouls, a_fouls,
    -- posesión del local recortada a [35, 65]; la del visitante = 100 - local
    CAST(CASE WHEN h_poss_raw < 35 THEN 35 WHEN h_poss_raw > 65 THEN 65 ELSE h_poss_raw END AS DECIMAL(5,2)) AS h_poss
INTO #GenFixtures
FROM calc;

-- 5.a Insertar los partidos generados
INSERT INTO dbo.Matches
    (competition_id, season_id, matchday, kickoff_at, home_team_id, away_team_id, status, external_ref)
SELECT c.id, s.id, NULL, g.kickoff, ht.id, at.id, N'jugado', g.ext_ref
FROM #GenFixtures g
JOIN dbo.Competitions c ON c.external_ref = N'TEST-LPF'
JOIN dbo.Seasons      s ON s.external_ref = N'TEST-LPF-2025'
JOIN dbo.Teams       ht ON ht.external_ref = g.home_ref
JOIN dbo.Teams       at ON at.external_ref = g.away_ref
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.Matches m WHERE m.external_ref = g.ext_ref
);

-- 5.b Estadísticas del equipo LOCAL (is_home = 1)
--     shots = córners*2 + 5 ; tiros al arco = goles + 2 (siempre <= shots)
INSERT INTO dbo.MatchStatistics
    (match_id, team_id, opponent_team_id, is_home,
     goals, goals_conceded, corners, yellow_cards, red_cards,
     shots, shots_on_target, possession, fouls)
SELECT m.id, ht.id, at.id, 1,
       g.h_goals, g.a_goals, g.h_corners, g.h_yellow, g.h_red,
       g.h_corners * 2 + 5, g.h_goals + 2, g.h_poss, g.h_fouls
FROM #GenFixtures g
JOIN dbo.Matches m  ON m.external_ref = g.ext_ref
JOIN dbo.Teams  ht  ON ht.external_ref = g.home_ref
JOIN dbo.Teams  at  ON at.external_ref = g.away_ref
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.MatchStatistics x
    WHERE x.match_id = m.id AND x.team_id = ht.id
);

-- 5.c Estadísticas del equipo VISITANTE (is_home = 0)
INSERT INTO dbo.MatchStatistics
    (match_id, team_id, opponent_team_id, is_home,
     goals, goals_conceded, corners, yellow_cards, red_cards,
     shots, shots_on_target, possession, fouls)
SELECT m.id, at.id, ht.id, 0,
       g.a_goals, g.h_goals, g.a_corners, g.a_yellow, g.a_red,
       g.a_corners * 2 + 5, g.a_goals + 2, CAST(100 AS DECIMAL(5,2)) - g.h_poss, g.a_fouls
FROM #GenFixtures g
JOIN dbo.Matches m  ON m.external_ref = g.ext_ref
JOIN dbo.Teams  ht  ON ht.external_ref = g.home_ref
JOIN dbo.Teams  at  ON at.external_ref = g.away_ref
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.MatchStatistics x
    WHERE x.match_id = m.id AND x.team_id = at.id
);
GO

/* --------------------------------------------------------------------------
   Limpieza de tablas temporales
   -------------------------------------------------------------------------- */
IF OBJECT_ID('tempdb..#TeamSeed')    IS NOT NULL DROP TABLE #TeamSeed;
IF OBJECT_ID('tempdb..#FixtureSeed') IS NOT NULL DROP TABLE #FixtureSeed;
IF OBJECT_ID('tempdb..#TeamBase')    IS NOT NULL DROP TABLE #TeamBase;
IF OBJECT_ID('tempdb..#GenFixtures') IS NOT NULL DROP TABLE #GenFixtures;
GO

/* --------------------------------------------------------------------------
   Verificación rápida (opcional)
   -------------------------------------------------------------------------- */
PRINT 'Script 05 completado: datos de prueba insertados.';

SELECT
    (SELECT COUNT(*) FROM dbo.Teams           WHERE external_ref LIKE 'TEST-TEAM-%') AS equipos,
    (SELECT COUNT(*) FROM dbo.Matches         WHERE external_ref LIKE 'TEST-%')       AS partidos,
    (SELECT COUNT(*) FROM dbo.MatchStatistics
         WHERE match_id IN (SELECT id FROM dbo.Matches WHERE external_ref LIKE 'TEST-%')) AS filas_estadisticas;

-- Partidos por equipo separando local/visitante (deben ser >= 10 cada uno):
SELECT t.short_name AS equipo,
       SUM(CASE WHEN ms.is_home = 1 THEN 1 ELSE 0 END) AS partidos_local,
       SUM(CASE WHEN ms.is_home = 0 THEN 1 ELSE 0 END) AS partidos_visitante,
       CAST(AVG(CAST(ms.corners AS DECIMAL(5,2))) AS DECIMAL(5,2)) AS corners_promedio
FROM dbo.MatchStatistics ms
JOIN dbo.Teams t ON t.id = ms.team_id
WHERE ms.match_id IN (SELECT id FROM dbo.Matches WHERE external_ref LIKE 'TEST-%')
GROUP BY t.short_name
ORDER BY corners_promedio DESC;
GO
