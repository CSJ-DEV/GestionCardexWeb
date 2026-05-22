/* =====================================================================
   ALTER_INFOMEGA_INHPRA_PROD.sql
   ---------------------------------------------------------------------
   Ajoute aux tables legacy `infomega` et `inhpra` les colonnes nécessaires
   à l'app web (id/avocat_id/created_at/updated_at, etc.) si absentes.

   Reproduit la même approche que pour Avocats / Adresses :
   - On garde les colonnes legacy intactes (lien via `code`).
   - On ajoute les colonnes app web pour permettre les requêtes ORM.

   Caractéristiques :
   - 100% idempotent : peut être ré-exécuté sans risque.
   - Backfille `avocat_id` à partir de `code` via jointure sur Avocats.

   À exécuter dans SSMS sur la base CardAvo.
   ===================================================================== */

SET NOCOUNT ON;
SET XACT_ABORT ON;

USE CardAvo;
GO

PRINT '';
PRINT '=== ALTER infomega + inhpra : ajout colonnes app web ===';
PRINT '';

/* ---------- infomega ---------- */
PRINT '-- dbo.infomega --';

IF COL_LENGTH('dbo.infomega', 'id') IS NULL
BEGIN
    PRINT '  [ADD] infomega.id (varchar(36))';
    ALTER TABLE dbo.infomega ADD id VARCHAR(36) NULL;
END
ELSE PRINT '  [OK]  infomega.id existe déjà';

IF COL_LENGTH('dbo.infomega', 'avocat_id') IS NULL
BEGIN
    PRINT '  [ADD] infomega.avocat_id (varchar(36))';
    ALTER TABLE dbo.infomega ADD avocat_id VARCHAR(36) NULL;
END
ELSE PRINT '  [OK]  infomega.avocat_id existe déjà';

IF COL_LENGTH('dbo.infomega', 'tous_districts') IS NULL
BEGIN
    PRINT '  [ADD] infomega.tous_districts (bit)';
    ALTER TABLE dbo.infomega ADD tous_districts BIT NOT NULL CONSTRAINT DF_infomega_tous_districts DEFAULT 0;
END
ELSE PRINT '  [OK]  infomega.tous_districts existe déjà';

IF COL_LENGTH('dbo.infomega', 'created_at') IS NULL
BEGIN
    PRINT '  [ADD] infomega.created_at (datetime2(0))';
    ALTER TABLE dbo.infomega ADD created_at DATETIME2(0) NULL;
END
ELSE PRINT '  [OK]  infomega.created_at existe déjà';

IF COL_LENGTH('dbo.infomega', 'updated_at') IS NULL
BEGIN
    PRINT '  [ADD] infomega.updated_at (datetime2(0))';
    ALTER TABLE dbo.infomega ADD updated_at DATETIME2(0) NULL;
END
ELSE PRINT '  [OK]  infomega.updated_at existe déjà';
GO

/* Backfill : id (uniqueidentifier) + avocat_id (depuis Avocats) */
PRINT '  [BACKFILL] infomega.id pour les lignes existantes sans id';
UPDATE dbo.infomega
SET id = LOWER(CONVERT(VARCHAR(36), NEWID()))
WHERE id IS NULL OR LTRIM(RTRIM(id)) = '';

PRINT '  [BACKFILL] infomega.avocat_id <- Avocats.id via code';
UPDATE m
SET avocat_id = a.id
FROM dbo.infomega m
JOIN dbo.Avocats  a ON a.code COLLATE DATABASE_DEFAULT = m.code COLLATE DATABASE_DEFAULT
WHERE (m.avocat_id IS NULL OR LTRIM(RTRIM(m.avocat_id)) = '')
  AND a.id IS NOT NULL;

PRINT '  [BACKFILL] infomega.created_at / updated_at <- datemodif (ou Now)';
UPDATE dbo.infomega
SET created_at = COALESCE(created_at, datemodif, SYSDATETIME())
WHERE created_at IS NULL;

UPDATE dbo.infomega
SET updated_at = COALESCE(updated_at, datemodif, created_at, SYSDATETIME())
WHERE updated_at IS NULL;
GO


/* ---------- inhpra ---------- */
PRINT '';
PRINT '-- dbo.inhpra --';

IF COL_LENGTH('dbo.inhpra', 'uuid') IS NULL
BEGIN
    PRINT '  [ADD] inhpra.uuid (varchar(36))';
    ALTER TABLE dbo.inhpra ADD uuid VARCHAR(36) NULL;
END
ELSE PRINT '  [OK]  inhpra.uuid existe déjà';

IF COL_LENGTH('dbo.inhpra', 'avocat_id') IS NULL
BEGIN
    PRINT '  [ADD] inhpra.avocat_id (varchar(36))';
    ALTER TABLE dbo.inhpra ADD avocat_id VARCHAR(36) NULL;
END
ELSE PRINT '  [OK]  inhpra.avocat_id existe déjà';

IF COL_LENGTH('dbo.inhpra', 'created_at') IS NULL
BEGIN
    PRINT '  [ADD] inhpra.created_at (datetime2(0))';
    ALTER TABLE dbo.inhpra ADD created_at DATETIME2(0) NULL;
END
ELSE PRINT '  [OK]  inhpra.created_at existe déjà';

IF COL_LENGTH('dbo.inhpra', 'updated_at') IS NULL
BEGIN
    PRINT '  [ADD] inhpra.updated_at (datetime2(0))';
    ALTER TABLE dbo.inhpra ADD updated_at DATETIME2(0) NULL;
END
ELSE PRINT '  [OK]  inhpra.updated_at existe déjà';
GO

/* Backfill */
PRINT '  [BACKFILL] inhpra.uuid pour les lignes existantes sans uuid';
UPDATE dbo.inhpra
SET uuid = LOWER(CONVERT(VARCHAR(36), NEWID()))
WHERE uuid IS NULL OR LTRIM(RTRIM(uuid)) = '';

PRINT '  [BACKFILL] inhpra.avocat_id <- Avocats.id via code';
UPDATE i
SET avocat_id = a.id
FROM dbo.inhpra  i
JOIN dbo.Avocats a ON a.code COLLATE DATABASE_DEFAULT = i.code COLLATE DATABASE_DEFAULT
WHERE (i.avocat_id IS NULL OR LTRIM(RTRIM(i.avocat_id)) = '')
  AND a.id IS NOT NULL;

PRINT '  [BACKFILL] inhpra.created_at / updated_at <- SYSDATETIME()';
UPDATE dbo.inhpra
SET created_at = COALESCE(created_at, SYSDATETIME())
WHERE created_at IS NULL;

UPDATE dbo.inhpra
SET updated_at = COALESCE(updated_at, created_at, SYSDATETIME())
WHERE updated_at IS NULL;
GO


/* =====================================================================
   VÉRIFICATION FINALE
   ===================================================================== */
PRINT '';
PRINT '=== Vérification ===';

SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    CHARACTER_MAXIMUM_LENGTH AS max_len
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dbo'
  AND (
        (TABLE_NAME = 'infomega' AND COLUMN_NAME IN ('id','avocat_id','tous_districts','created_at','updated_at')) OR
        (TABLE_NAME = 'inhpra'   AND COLUMN_NAME IN ('uuid','avocat_id','created_at','updated_at'))
      )
ORDER BY TABLE_NAME, COLUMN_NAME;

SELECT 'infomega' AS table_name, COUNT(*) AS total, SUM(CASE WHEN avocat_id IS NOT NULL THEN 1 ELSE 0 END) AS with_avocat_id FROM dbo.infomega
UNION ALL
SELECT 'inhpra',   COUNT(*),    SUM(CASE WHEN avocat_id IS NOT NULL THEN 1 ELSE 0 END) FROM dbo.inhpra;
GO
