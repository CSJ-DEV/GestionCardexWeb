-- ============================================================
--   MIGRATION : ajout des colonnes web à la table Avocats
-- ============================================================
-- À exécuter UNE SEULE FOIS dans la base CardAvo sur CSJ-SQL-TEST.
-- Le script est idempotent (re-exécution sans risque).
--
-- Ajoute les 10 colonnes utilisées par l'app web GestionCardex à la
-- table Avocats legacy (issue de l'ancienne application VB), puis
-- "backfille" l'UUID `id` et les dates pour les lignes existantes.
-- ============================================================

USE [CardAvo];
GO

PRINT '=== Ajout des colonnes web à dbo.Avocats ===';

-- 0. type_code (type de code avocat — A=avocat, N=notaire, P=stagiaire)
IF COL_LENGTH('dbo.Avocats', 'type_code') IS NULL
BEGIN
    ALTER TABLE dbo.Avocats ADD type_code NVARCHAR(1) NOT NULL CONSTRAINT DF_Avocats_type_code DEFAULT 'A';
    PRINT '  + colonne type_code ajoutée (defaut=A)';
END
ELSE PRINT '  · type_code déjà présente';
GO

-- 1. id (UUID app — clé naturelle pour les API REST)
IF COL_LENGTH('dbo.Avocats', 'id') IS NULL
BEGIN
    ALTER TABLE dbo.Avocats ADD id NVARCHAR(36) NULL;
    PRINT '  + colonne id ajoutée';
END
ELSE PRINT '  · id déjà présente';
GO

-- 2. actif (statut actif/inactif)
IF COL_LENGTH('dbo.Avocats', 'actif') IS NULL
BEGIN
    ALTER TABLE dbo.Avocats ADD actif BIT NOT NULL CONSTRAINT DF_Avocats_actif DEFAULT 1;
    PRINT '  + colonne actif ajoutée (defaut=1)';
END
ELSE PRINT '  · actif déjà présente';
GO

-- 3. attente
IF COL_LENGTH('dbo.Avocats', 'attente') IS NULL
BEGIN
    ALTER TABLE dbo.Avocats ADD attente BIT NOT NULL CONSTRAINT DF_Avocats_attente DEFAULT 0;
    PRINT '  + colonne attente ajoutée (defaut=0)';
END
ELSE PRINT '  · attente déjà présente';
GO

-- 4. annee_barreau
IF COL_LENGTH('dbo.Avocats', 'annee_barreau') IS NULL
BEGIN
    ALTER TABLE dbo.Avocats ADD annee_barreau NVARCHAR(10) NULL;
    PRINT '  + colonne annee_barreau ajoutée';
END
ELSE PRINT '  · annee_barreau déjà présente';
GO

-- 5. taxes
IF COL_LENGTH('dbo.Avocats', 'taxes') IS NULL
BEGIN
    ALTER TABLE dbo.Avocats ADD taxes NVARCHAR(20) NULL;
    PRINT '  + colonne taxes ajoutée';
END
ELSE PRINT '  · taxes déjà présente';
GO

-- 6. web_password_hash (mot de passe extranet)
IF COL_LENGTH('dbo.Avocats', 'web_password_hash') IS NULL
BEGIN
    ALTER TABLE dbo.Avocats ADD web_password_hash NVARCHAR(100) NULL;
    PRINT '  + colonne web_password_hash ajoutée';
END
ELSE PRINT '  · web_password_hash déjà présente';
GO

-- 7. villerref (variante moderne — alias de villeref)
IF COL_LENGTH('dbo.Avocats', 'villerref') IS NULL
BEGIN
    ALTER TABLE dbo.Avocats ADD villerref NVARCHAR(40) NULL;
    PRINT '  + colonne villerref ajoutée';
END
ELSE PRINT '  · villerref déjà présente';
GO

-- 8. adresse_courante (snapshot JSON de l'adresse principale)
IF COL_LENGTH('dbo.Avocats', 'adresse_courante') IS NULL
BEGIN
    ALTER TABLE dbo.Avocats ADD adresse_courante NVARCHAR(MAX) NULL;
    PRINT '  + colonne adresse_courante ajoutée';
END
ELSE PRINT '  · adresse_courante déjà présente';
GO

-- 9. created_at
IF COL_LENGTH('dbo.Avocats', 'created_at') IS NULL
BEGIN
    ALTER TABLE dbo.Avocats ADD created_at NVARCHAR(30) NULL;
    PRINT '  + colonne created_at ajoutée';
END
ELSE PRINT '  · created_at déjà présente';
GO

-- 10. updated_at
IF COL_LENGTH('dbo.Avocats', 'updated_at') IS NULL
BEGIN
    ALTER TABLE dbo.Avocats ADD updated_at NVARCHAR(30) NULL;
    PRINT '  + colonne updated_at ajoutée';
END
ELSE PRINT '  · updated_at déjà présente';
GO

-- ============================================================
--                   BACKFILL DES VALEURS
-- ============================================================
PRINT '';
PRINT '=== Backfill des UUIDs et dates pour les avocats existants ===';

-- UUID pour chaque avocat
UPDATE dbo.Avocats
SET id = LOWER(CONVERT(NVARCHAR(36), NEWID()))
WHERE id IS NULL;
PRINT CONCAT('  + ', @@ROWCOUNT, ' avocats ont reçu un UUID');
GO

-- Dates ISO 8601 pour created_at / updated_at
DECLARE @now NVARCHAR(30) = CONVERT(NVARCHAR(30), SYSUTCDATETIME(), 126);

UPDATE dbo.Avocats SET created_at = @now WHERE created_at IS NULL;
PRINT CONCAT('  + ', @@ROWCOUNT, ' avocats ont reçu created_at');

UPDATE dbo.Avocats SET updated_at = @now WHERE updated_at IS NULL;
PRINT CONCAT('  + ', @@ROWCOUNT, ' avocats ont reçu updated_at');
GO

-- Index unique filtré sur id (pour rechercher rapidement par UUID)
IF NOT EXISTS (SELECT 1 FROM sys.indexes
               WHERE name = 'UX_Avocats_id' AND object_id = OBJECT_ID('dbo.Avocats'))
BEGIN
    CREATE UNIQUE NONCLUSTERED INDEX UX_Avocats_id ON dbo.Avocats(id) WHERE id IS NOT NULL;
    PRINT '  + index UX_Avocats_id créé';
END
ELSE PRINT '  · index UX_Avocats_id déjà présent';
GO

-- ============================================================
--                       VÉRIFICATION
-- ============================================================
PRINT '';
PRINT '=== Vérification ===';
SELECT
    COUNT(*) AS total_avocats,
    SUM(CASE WHEN id IS NULL THEN 1 ELSE 0 END) AS sans_uuid,
    SUM(CASE WHEN actif = 1 THEN 1 ELSE 0 END) AS actifs,
    SUM(CASE WHEN actif = 0 THEN 1 ELSE 0 END) AS inactifs
FROM dbo.Avocats;

PRINT '';
PRINT '✅ Migration terminée. Rechargez l''app web — l''onglet Avocats devrait fonctionner.';
GO
