/* ==========================================================================
   Bet Analyzer AI — Esquema de base de datos
   Script 01: Creación de tablas (SIN foreign keys)

   Motor:  SQL Server (instancia MAXI\SQLEXPRESS)
   Base:   BetAnalyzerAI (ya creada)

   Traducción del diseño conceptual aprobado en docs/database-design.md.
   Principio clave: se guardan HECHOS CRUDOS, nunca derivados.
     - El marcador y BTTS NO son columnas: se derivan de MatchStatistics.
     - MatchStatistics está en formato "largo": una fila por equipo y partido.

   Notas técnicas:
     - Claves primarias enteras autoincrementales (IDENTITY).
     - Texto en NVARCHAR (soporta Unicode: acentos, ñ...).
     - Fechas en DATE / DATETIME2 (no el viejo DATETIME).
     - Booleanos en BIT. Decimales en DECIMAL.
     - Se usa IF NOT EXISTS para que re-ejecutar el script no falle.
     - external_ref permite cargas idempotentes desde la fuente externa.
   ========================================================================== */

USE BetAnalyzerAI;
GO

/* --------------------------------------------------------------------------
   1. Competitions — Competiciones / torneos
   -------------------------------------------------------------------------- */
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Competitions')
BEGIN
    CREATE TABLE dbo.Competitions
    (
        id           INT            IDENTITY(1,1) NOT NULL,  -- PK surrogate
        name         NVARCHAR(150)  NOT NULL,               -- nombre de la competición
        country      NVARCHAR(100)  NULL,                   -- país/región
        type         NVARCHAR(50)   NULL,                   -- liga, copa, internacional...
        external_ref NVARCHAR(100)  NULL,                   -- id en la fuente externa
        created_at   DATETIME2(3)   NOT NULL
            CONSTRAINT DF_Competitions_created_at DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT PK_Competitions PRIMARY KEY (id)
    );
END
GO

/* --------------------------------------------------------------------------
   2. Seasons — Temporadas (pertenecen a una competición)
   -------------------------------------------------------------------------- */
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Seasons')
BEGIN
    CREATE TABLE dbo.Seasons
    (
        id             INT            IDENTITY(1,1) NOT NULL,
        competition_id INT            NOT NULL,             -- FK -> Competitions
        name           NVARCHAR(100)  NOT NULL,             -- "2025", "Apertura 2025"
        start_date     DATE           NULL,                 -- inicio de la temporada
        end_date       DATE           NULL,                 -- fin (NULL si está en curso)
        is_current     BIT            NOT NULL
            CONSTRAINT DF_Seasons_is_current DEFAULT (0),   -- marca la temporada activa
        external_ref   NVARCHAR(100)  NULL,
        CONSTRAINT PK_Seasons PRIMARY KEY (id)
    );
END
GO

/* --------------------------------------------------------------------------
   3. Teams — Equipos
   -------------------------------------------------------------------------- */
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Teams')
BEGIN
    CREATE TABLE dbo.Teams
    (
        id           INT            IDENTITY(1,1) NOT NULL,
        name         NVARCHAR(150)  NOT NULL,               -- nombre oficial/largo
        short_name   NVARCHAR(50)   NULL,                   -- nombre corto ("River")
        country      NVARCHAR(100)  NULL,
        external_ref NVARCHAR(100)  NULL,
        created_at   DATETIME2(3)   NOT NULL
            CONSTRAINT DF_Teams_created_at DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT PK_Teams PRIMARY KEY (id)
    );
END
GO

/* --------------------------------------------------------------------------
   4. Referees — Árbitros
   -------------------------------------------------------------------------- */
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Referees')
BEGIN
    CREATE TABLE dbo.Referees
    (
        id           INT            IDENTITY(1,1) NOT NULL,
        name         NVARCHAR(150)  NOT NULL,
        country      NVARCHAR(100)  NULL,
        external_ref NVARCHAR(100)  NULL,
        created_at   DATETIME2(3)   NOT NULL
            CONSTRAINT DF_Referees_created_at DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT PK_Referees PRIMARY KEY (id)
    );
END
GO

/* --------------------------------------------------------------------------
   5. Venues — Estadios (parte de la v1; puede quedar vacía)
   -------------------------------------------------------------------------- */
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Venues')
BEGIN
    CREATE TABLE dbo.Venues
    (
        id           INT            IDENTITY(1,1) NOT NULL,
        name         NVARCHAR(150)  NOT NULL,               -- nombre del estadio
        city         NVARCHAR(100)  NULL,
        capacity     INT            NULL,                   -- capacidad (opcional)
        external_ref NVARCHAR(100)  NULL,
        CONSTRAINT PK_Venues PRIMARY KEY (id)
    );
END
GO

/* --------------------------------------------------------------------------
   6. Matches — Partidos (evento central)
      El marcador NO vive aquí: los goles son un hecho crudo por equipo y
      se guardan en MatchStatistics.
   -------------------------------------------------------------------------- */
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Matches')
BEGIN
    CREATE TABLE dbo.Matches
    (
        id             INT            IDENTITY(1,1) NOT NULL,
        competition_id INT            NOT NULL,             -- FK -> Competitions
        season_id      INT            NOT NULL,             -- FK -> Seasons
        matchday       INT            NULL,                 -- jornada/ronda (opcional)
        kickoff_at     DATETIME2(0)   NOT NULL,             -- fecha y hora de inicio (UTC)
        home_team_id   INT            NOT NULL,             -- FK -> Teams (local)
        away_team_id   INT            NOT NULL,             -- FK -> Teams (visitante)
        referee_id     INT            NULL,                 -- FK -> Referees (nullable)
        venue_id       INT            NULL,                 -- FK -> Venues (nullable)
        status         NVARCHAR(30)   NULL,                 -- programado, jugado, suspendido...
        external_ref   NVARCHAR(100)  NULL,                 -- id en la fuente (carga idempotente)
        created_at     DATETIME2(3)   NOT NULL
            CONSTRAINT DF_Matches_created_at DEFAULT (SYSUTCDATETIME()),
        updated_at     DATETIME2(3)   NULL,                 -- última actualización de la carga
        CONSTRAINT PK_Matches PRIMARY KEY (id)
    );
END
GO

/* --------------------------------------------------------------------------
   7. MatchStatistics — Estadísticas CRUDAS por partido y equipo
      Formato largo: una fila por equipo por partido (2 filas por partido).
      La localía es un atributo (is_home), no una columna home_/away_.
      Restricción de integridad: (match_id, team_id) único.
      Los conteos son NULL-ables porque una fuente puede no proveerlos todos.
   -------------------------------------------------------------------------- */
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'MatchStatistics')
BEGIN
    CREATE TABLE dbo.MatchStatistics
    (
        id               INT           IDENTITY(1,1) NOT NULL,
        match_id         INT           NOT NULL,           -- FK -> Matches
        team_id          INT           NOT NULL,           -- FK -> Teams (dueño de la fila)
        opponent_team_id INT           NULL,               -- FK -> Teams (rival)
        is_home          BIT           NOT NULL,           -- ¿jugó de local?
        goals            INT           NULL,               -- goles anotados
        goals_conceded   INT           NULL,               -- goles recibidos
        corners          INT           NULL,               -- córners a favor
        yellow_cards     INT           NULL,               -- tarjetas amarillas
        red_cards        INT           NULL,               -- tarjetas rojas
        shots            INT           NULL,               -- tiros totales
        shots_on_target  INT           NULL,               -- tiros al arco
        possession       DECIMAL(5,2)  NULL,               -- posesión % (0.00 - 100.00)
        fouls            INT           NULL,               -- faltas cometidas
        created_at       DATETIME2(3)  NOT NULL
            CONSTRAINT DF_MatchStatistics_created_at DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT PK_MatchStatistics PRIMARY KEY (id),
        -- Un equipo no puede tener dos filas de estadísticas en el mismo partido:
        CONSTRAINT UQ_MatchStatistics_match_team UNIQUE (match_id, team_id)
    );
END
GO

/* --------------------------------------------------------------------------
   8. MatchStatisticExtras — Métricas extra (clave-valor / EAV)
      BORRADOR TEMPORAL para experimentar con variables nuevas.
      Regla de proyecto: ninguna variable usada en producción puede quedar
      aquí de forma permanente; debe promoverse a columna en MatchStatistics.
   -------------------------------------------------------------------------- */
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'MatchStatisticExtras')
BEGIN
    CREATE TABLE dbo.MatchStatisticExtras
    (
        id            INT             IDENTITY(1,1) NOT NULL,
        match_stat_id INT             NOT NULL,             -- FK -> MatchStatistics
        metric_key    NVARCHAR(100)   NOT NULL,             -- nombre de la métrica ("xg"...)
        metric_value  DECIMAL(18,6)   NULL,                 -- valor numérico
        CONSTRAINT PK_MatchStatisticExtras PRIMARY KEY (id),
        -- Una misma métrica no se repite para la misma fila de estadística:
        CONSTRAINT UQ_MatchStatisticExtras_stat_key UNIQUE (match_stat_id, metric_key)
    );
END
GO

/* --------------------------------------------------------------------------
   9. Markets — Catálogo de mercados (goals, corners, cards, btts...)
      code coincide con el nombre del plugin del engine.
   -------------------------------------------------------------------------- */
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Markets')
BEGIN
    CREATE TABLE dbo.Markets
    (
        id          INT            IDENTITY(1,1) NOT NULL,
        code        NVARCHAR(50)   NOT NULL,               -- código estable ("goals")
        name        NVARCHAR(100)  NOT NULL,               -- nombre visible ("Goles")
        description NVARCHAR(300)  NULL,
        CONSTRAINT PK_Markets PRIMARY KEY (id),
        CONSTRAINT UQ_Markets_code UNIQUE (code)           -- code único
    );
END
GO

/* --------------------------------------------------------------------------
   10. MatchOdds — Cuotas por partido y mercado
       Formato largo: una fila por partido x mercado x línea x casa.
       En v1 puede quedar vacía (aún no ingerimos odds).
   -------------------------------------------------------------------------- */
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'MatchOdds')
BEGIN
    CREATE TABLE dbo.MatchOdds
    (
        id          INT            IDENTITY(1,1) NOT NULL,
        match_id    INT            NOT NULL,               -- FK -> Matches
        market_id   INT            NOT NULL,               -- FK -> Markets
        bookmaker   NVARCHAR(100)  NULL,                   -- casa de apuestas
        selection   NVARCHAR(50)   NULL,                   -- "Over", "Under", "Yes", "No"...
        line        DECIMAL(5,2)   NULL,                   -- línea (2.5, 3.5...); NULL si no aplica
        odds_value  DECIMAL(10,3)  NULL,                   -- cuota decimal ofrecida
        captured_at DATETIME2(3)   NULL,                   -- momento de captura de la cuota
        CONSTRAINT PK_MatchOdds PRIMARY KEY (id)
    );
END
GO

PRINT 'Script 01 completado: tablas creadas (sin foreign keys).';
GO
