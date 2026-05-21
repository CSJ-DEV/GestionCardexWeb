-- ============================================================
--   MIGRATION ADRESSES : ajout des colonnes web minimales
-- ============================================================
-- À exécuter UNE SEULE FOIS dans la base CardAvo sur CSJ-SQL-TEST.
-- Le script est idempotent (re-exécution sans risque).
--
-- La jointure Adresses ↔ Avocats reste sur la colonne legacy `code`.
-- On n'ajoute QUE les colonnes nécessaires aux API REST modernes :
--   - id          → UUID pour identifier l'adresse côté web
--   - RowId       → uniqueidentifier legacy (si absent)
--   - created_at  → audit web
--   - updated_at  → audit web
--
-- PAS de avocat_id : la liaison se fait via `code`.
-- ============================================================

USE [CardAvo];
GO

PRINT '=== Ajout des colonnes web minimales à dbo.Adresses ===';

-- 1. id (UUID app, clé naturelle REST)
IF COL_LENGTH('dbo.Adresses', 'id') IS NULL
BEGIN
    ALTER TABLE dbo.Adresses ADD id NVARCHAR(36) NULL;
    PRINT '  + colonne id ajoutée';
END
ELSE PRINT '  · id déjà présente';
GO

-- 2. RowId (legacy uniqueidentifier — si absent)
IF COL_LENGTH('dbo.Adresses', 'RowId') IS NULL
BEGIN
    ALTER TABLE dbo.Adresses ADD [RowId] NVARCHAR(36) NULL;
    PRINT '  + colonne RowId ajoutée';
END
ELSE PRINT '  · RowId déjà présente';
GO

-- 3. created_at
IF COL_LENGTH('dbo.Adresses', 'created_at') IS NULL
BEGIN
    ALTER TABLE dbo.Adresses ADD created_at NVARCHAR(30) NULL;
    PRINT '  + colonne created_at ajoutée';
END
ELSE PRINT '  · created_at déjà présente';
GO

-- 4. updated_at
IF COL_LENGTH('dbo.Adresses', 'updated_at') IS NULL
BEGIN
    ALTER TABLE dbo.Adresses ADD updated_at NVARCHAR(30) NULL;
    PRINT '  + colonne updated_at ajoutée';
END
ELSE PRINT '  · updated_at déjà présente';
GO

-- ============================================================
--                   BACKFILL DES VALEURS
-- ============================================================
PRINT '';
PRINT '=== Backfill des UUIDs et dates ===';

UPDATE dbo.Adresses
SET id = LOWER(CONVERT(NVARCHAR(36), NEWID()))
WHERE id IS NULL;
PRINT CONCAT('  + ', @@ROWCOUNT, ' adresses ont reçu un UUID');
GO

UPDATE dbo.Adresses
SET [RowId] = LOWER(CONVERT(NVARCHAR(36), NEWID()))
WHERE [RowId] IS NULL;
PRINT CONCAT('  + ', @@ROWCOUNT, ' adresses ont reçu un RowId');
GO

DECLARE @now NVARCHAR(30) = CONVERT(NVARCHAR(30), SYSUTCDATETIME(), 126);
UPDATE dbo.Adresses SET created_at = @now WHERE created_at IS NULL;
PRINT CONCAT('  + ', @@ROWCOUNT, ' adresses ont reçu created_at');
UPDATE dbo.Adresses SET updated_at = @now WHERE updated_at IS NULL;
PRINT CONCAT('  + ', @@ROWCOUNT, ' adresses ont reçu updated_at');
GO

-- Index unique sur id pour les lookups rapides
IF NOT EXISTS (SELECT 1 FROM sys.indexes
               WHERE name = 'UX_Adresses_id' AND object_id = OBJECT_ID('dbo.Adresses'))
BEGIN
    CREATE UNIQUE NONCLUSTERED INDEX UX_Adresses_id ON dbo.Adresses(id) WHERE id IS NOT NULL;
    PRINT '  + index UX_Adresses_id créé';
END
ELSE PRINT '  · index UX_Adresses_id déjà présent';
GO

-- Vérification finale
PRINT '';
PRINT '=== Vérification ===';
SELECT
    COUNT(*) AS total_adresses,
    SUM(CASE WHEN id IS NULL THEN 1 ELSE 0 END) AS sans_uuid,
    SUM(CASE WHEN courant = 'O' THEN 1 ELSE 0 END) AS courantes
FROM dbo.Adresses;

PRINT '';
PRINT '✅ Migration Adresses terminée.';
GO
