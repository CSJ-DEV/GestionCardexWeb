-- ============================================================
--   MIGRATION ADRESSES : alignement legacy
-- ============================================================
-- À exécuter UNE SEULE FOIS dans la base CardAvo sur CSJ-SQL-TEST.
-- Le script est idempotent (re-exécution sans risque).
--
-- Choix d'architecture :
--   - PK = `RowId` legacy (uniqueidentifier) — pas de doublon avec un
--     nouveau `id`. Le frontend reçoit `RowId` sous l'alias JSON `id`.
--   - Liaison Adresses → Avocats : colonne `code` (legacy). Pas de
--     colonne `avocat_id` dupliquée.
--   - Email : colonne unique `adremail` legacy (la colonne `email`
--     ajoutée par erreur est supprimée si présente).
--
-- Colonnes web ajoutées (uniquement pour l'audit) :
--   - created_at
--   - updated_at
-- ============================================================

USE [CardAvo];
GO

PRINT '=== Nettoyage : suppression des colonnes dupliquées ===';
GO

-- Drop des contraintes DEFAULT avant de DROP les colonnes
DECLARE @sql NVARCHAR(MAX) = N'';
SELECT @sql = @sql + N'ALTER TABLE dbo.Adresses DROP CONSTRAINT [' + dc.name + N'];' + CHAR(10)
FROM sys.default_constraints dc
JOIN sys.columns c ON c.default_object_id = dc.object_id
WHERE c.object_id = OBJECT_ID('dbo.Adresses')
  AND c.name IN (N'id', N'avocat_id', N'email');
IF LEN(@sql) > 0
BEGIN
    PRINT N'Suppression des contraintes DEFAULT :';
    PRINT @sql;
    EXEC sp_executesql @sql;
END
GO

-- Drop index sur id/avocat_id si présents
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UX_Adresses_id' AND object_id = OBJECT_ID('dbo.Adresses'))
    DROP INDEX UX_Adresses_id ON dbo.Adresses;
GO
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Adresses_avocat_id' AND object_id = OBJECT_ID('dbo.Adresses'))
    DROP INDEX IX_Adresses_avocat_id ON dbo.Adresses;
GO

-- Drop des colonnes
IF COL_LENGTH('dbo.Adresses', 'id') IS NOT NULL
BEGIN
    ALTER TABLE dbo.Adresses DROP COLUMN id;
    PRINT '  - id supprimée (doublon de RowId)';
END
ELSE PRINT '  · id déjà absente';
GO

IF COL_LENGTH('dbo.Adresses', 'avocat_id') IS NOT NULL
BEGIN
    ALTER TABLE dbo.Adresses DROP COLUMN avocat_id;
    PRINT '  - avocat_id supprimée (liaison via code legacy)';
END
ELSE PRINT '  · avocat_id déjà absente';
GO

IF COL_LENGTH('dbo.Adresses', 'email') IS NOT NULL
BEGIN
    ALTER TABLE dbo.Adresses DROP COLUMN email;
    PRINT '  - email supprimée (doublon de adremail)';
END
ELSE PRINT '  · email déjà absente';
GO

-- ============================================================
--          Ajout des colonnes web minimales (audit)
-- ============================================================
PRINT '';
PRINT '=== Ajout des colonnes d''audit web ===';

IF COL_LENGTH('dbo.Adresses', 'created_at') IS NULL
BEGIN
    ALTER TABLE dbo.Adresses ADD created_at NVARCHAR(30) NULL;
    PRINT '  + created_at ajoutée';
END
ELSE PRINT '  · created_at déjà présente';
GO

IF COL_LENGTH('dbo.Adresses', 'updated_at') IS NULL
BEGIN
    ALTER TABLE dbo.Adresses ADD updated_at NVARCHAR(30) NULL;
    PRINT '  + updated_at ajoutée';
END
ELSE PRINT '  · updated_at déjà présente';
GO

-- Backfill dates
DECLARE @now NVARCHAR(30) = CONVERT(NVARCHAR(30), SYSUTCDATETIME(), 126);
UPDATE dbo.Adresses SET created_at = @now WHERE created_at IS NULL;
UPDATE dbo.Adresses SET updated_at = @now WHERE updated_at IS NULL;
GO

-- ============================================================
--                       VÉRIFICATION
-- ============================================================
PRINT '';
PRINT '=== Structure finale ===';
SELECT
    c.name AS colonne,
    TYPE_NAME(c.user_type_id) AS type,
    c.max_length AS longueur,
    c.is_nullable AS nullable
FROM sys.columns c
WHERE c.object_id = OBJECT_ID('dbo.Adresses')
ORDER BY c.column_id;
GO

PRINT '';
PRINT '✅ Migration Adresses terminée.';
GO
