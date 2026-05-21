-- ============================================================
--   MIGRATION : ajout des colonnes web à la table Adresses
-- ============================================================
-- À exécuter UNE SEULE FOIS dans la base CardAvo sur CSJ-SQL-TEST.
-- Le script est idempotent (re-exécution sans risque).
--
-- Ajoute les colonnes utilisées par l'app web qui ne sont pas
-- présentes dans la table Adresses legacy (issue de l'app VB).
--
-- Colonnes ajoutées :
--   - id (UUID app, clé naturelle REST)
--   - RowId (uniqueidentifier, legacy)
--   - avocat_id (FK logique → Avocats.id)
--   - created_at, updated_at
-- ============================================================

USE [CardAvo];
GO

PRINT '=== Ajout des colonnes web à dbo.Adresses ===';

-- 1. id (UUID app — clé naturelle pour les API REST)
IF COL_LENGTH('dbo.Adresses', 'id') IS NULL
BEGIN
    ALTER TABLE dbo.Adresses ADD id NVARCHAR(36) NULL;
    PRINT '  + colonne id ajoutée';
END
ELSE PRINT '  · id déjà présente';
GO

-- 2. RowId (uniqueidentifier, exigé par le legacy)
IF COL_LENGTH('dbo.Adresses', 'RowId') IS NULL
BEGIN
    ALTER TABLE dbo.Adresses ADD [RowId] NVARCHAR(36) NULL;
    PRINT '  + colonne RowId ajoutée';
END
ELSE PRINT '  · RowId déjà présente';
GO

-- 3. avocat_id (FK logique vers Avocats.id)
IF COL_LENGTH('dbo.Adresses', 'avocat_id') IS NULL
BEGIN
    ALTER TABLE dbo.Adresses ADD avocat_id NVARCHAR(36) NULL;
    PRINT '  + colonne avocat_id ajoutée';
END
ELSE PRINT '  · avocat_id déjà présente';
GO

-- 4. created_at
IF COL_LENGTH('dbo.Adresses', 'created_at') IS NULL
BEGIN
    ALTER TABLE dbo.Adresses ADD created_at NVARCHAR(30) NULL;
    PRINT '  + colonne created_at ajoutée';
END
ELSE PRINT '  · created_at déjà présente';
GO

-- 5. updated_at
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
PRINT '=== Backfill des UUIDs et liaisons pour les adresses existantes ===';

-- UUID id pour chaque adresse
UPDATE dbo.Adresses
SET id = LOWER(CONVERT(NVARCHAR(36), NEWID()))
WHERE id IS NULL;
PRINT CONCAT('  + ', @@ROWCOUNT, ' adresses ont reçu un UUID `id`');
GO

-- UUID RowId pour chaque adresse (si pas déjà fixé)
UPDATE dbo.Adresses
SET [RowId] = LOWER(CONVERT(NVARCHAR(36), NEWID()))
WHERE [RowId] IS NULL;
PRINT CONCAT('  + ', @@ROWCOUNT, ' adresses ont reçu un RowId');
GO

-- Lier chaque adresse à son avocat via le `code` legacy
UPDATE A
SET A.avocat_id = AV.id
FROM dbo.Adresses A
JOIN dbo.Avocats AV ON AV.code = A.code
WHERE A.avocat_id IS NULL AND AV.id IS NOT NULL;
PRINT CONCAT('  + ', @@ROWCOUNT, ' adresses liées à leur avocat (avocat_id)');
GO

-- Dates ISO 8601 pour created_at / updated_at
DECLARE @now NVARCHAR(30) = CONVERT(NVARCHAR(30), SYSUTCDATETIME(), 126);

UPDATE dbo.Adresses SET created_at = @now WHERE created_at IS NULL;
PRINT CONCAT('  + ', @@ROWCOUNT, ' adresses ont reçu created_at');

UPDATE dbo.Adresses SET updated_at = @now WHERE updated_at IS NULL;
PRINT CONCAT('  + ', @@ROWCOUNT, ' adresses ont reçu updated_at');
GO

-- Index unique filtré sur id pour les recherches rapides
IF NOT EXISTS (SELECT 1 FROM sys.indexes
               WHERE name = 'UX_Adresses_id' AND object_id = OBJECT_ID('dbo.Adresses'))
BEGIN
    CREATE UNIQUE NONCLUSTERED INDEX UX_Adresses_id ON dbo.Adresses(id) WHERE id IS NOT NULL;
    PRINT '  + index UX_Adresses_id créé';
END
ELSE PRINT '  · index UX_Adresses_id déjà présent';
GO

-- Index sur avocat_id pour les requêtes ORM
IF NOT EXISTS (SELECT 1 FROM sys.indexes
               WHERE name = 'IX_Adresses_avocat_id' AND object_id = OBJECT_ID('dbo.Adresses'))
BEGIN
    CREATE NONCLUSTERED INDEX IX_Adresses_avocat_id ON dbo.Adresses(avocat_id);
    PRINT '  + index IX_Adresses_avocat_id créé';
END
ELSE PRINT '  · index IX_Adresses_avocat_id déjà présent';
GO

-- ============================================================
--                       VÉRIFICATION
-- ============================================================
PRINT '';
PRINT '=== Vérification ===';
SELECT
    COUNT(*) AS total_adresses,
    SUM(CASE WHEN id IS NULL THEN 1 ELSE 0 END) AS sans_uuid,
    SUM(CASE WHEN avocat_id IS NULL THEN 1 ELSE 0 END) AS sans_avocat_id,
    SUM(CASE WHEN courant = 'O' THEN 1 ELSE 0 END) AS courantes
FROM dbo.Adresses;

PRINT '';
PRINT '✅ Migration Adresses terminée.';
GO
