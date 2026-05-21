-- ============================================================
--   NETTOYAGE : suppression des colonnes web inutiles
-- ============================================================
-- À exécuter dans SSMS sur CSJ-SQL-TEST → base CardAvo
-- APRÈS le déploiement du backend refactoré.
--
-- Supprime les colonnes ajoutées à tort par l'app web qui font
-- doublon avec des champs legacy déjà présents.
--
-- Suppressions :
--   - actif          → utilise actpass (legacy 'A'/'P')
--   - annee_barreau  → utilise dateinscbarr (legacy)
--   - villerref      → utilise villeref (legacy)
--   - adresse_courante → jointure Adresses via adrcour
--   - taxes          → champs séparés cNoTax1/cNoTax2 dans une autre BDD
--   - attente        → champ non utilisé (surveil reste, distinct)
--
-- Conservées :
--   - id, type_code, web_password_hash, created_at, updated_at
-- ============================================================

USE [CardAvo];
GO

PRINT '=== Nettoyage des colonnes web dupliquées sur dbo.Avocats ===';
GO

-- Drop des contraintes DEFAULT avant de pouvoir DROP les colonnes
DECLARE @sql NVARCHAR(MAX) = N'';
SELECT @sql = @sql + N'ALTER TABLE dbo.Avocats DROP CONSTRAINT [' + dc.name + N'];' + CHAR(10)
FROM sys.default_constraints dc
JOIN sys.columns c ON c.default_object_id = dc.object_id
WHERE c.object_id = OBJECT_ID('dbo.Avocats')
  AND c.name IN (N'actif', N'attente', N'annee_barreau', N'taxes',
                 N'villerref', N'adresse_courante');
IF LEN(@sql) > 0
BEGIN
    PRINT N'Suppression des contraintes DEFAULT :';
    PRINT @sql;
    EXEC sp_executesql @sql;
END
ELSE
    PRINT N'  · aucune contrainte DEFAULT à supprimer';
GO

-- Drop des colonnes
IF COL_LENGTH('dbo.Avocats', 'actif') IS NOT NULL
BEGIN
    ALTER TABLE dbo.Avocats DROP COLUMN actif;
    PRINT '  - actif supprimée';
END
ELSE PRINT '  · actif déjà absente';
GO

IF COL_LENGTH('dbo.Avocats', 'attente') IS NOT NULL
BEGIN
    ALTER TABLE dbo.Avocats DROP COLUMN attente;
    PRINT '  - attente supprimée';
END
ELSE PRINT '  · attente déjà absente';
GO

IF COL_LENGTH('dbo.Avocats', 'annee_barreau') IS NOT NULL
BEGIN
    ALTER TABLE dbo.Avocats DROP COLUMN annee_barreau;
    PRINT '  - annee_barreau supprimée';
END
ELSE PRINT '  · annee_barreau déjà absente';
GO

IF COL_LENGTH('dbo.Avocats', 'taxes') IS NOT NULL
BEGIN
    ALTER TABLE dbo.Avocats DROP COLUMN taxes;
    PRINT '  - taxes supprimée';
END
ELSE PRINT '  · taxes déjà absente';
GO

IF COL_LENGTH('dbo.Avocats', 'villerref') IS NOT NULL
BEGIN
    ALTER TABLE dbo.Avocats DROP COLUMN villerref;
    PRINT '  - villerref supprimée';
END
ELSE PRINT '  · villerref déjà absente';
GO

IF COL_LENGTH('dbo.Avocats', 'adresse_courante') IS NOT NULL
BEGIN
    ALTER TABLE dbo.Avocats DROP COLUMN adresse_courante;
    PRINT '  - adresse_courante supprimée';
END
ELSE PRINT '  · adresse_courante déjà absente';
GO

PRINT '';
PRINT '✅ Nettoyage terminé.';
PRINT '   La table Avocats utilise désormais uniquement les colonnes legacy';
PRINT '   + 4 colonnes web (id, type_code, created_at, updated_at, web_password_hash).';
GO

-- Vérification finale
SELECT TOP 3 code, type_code, nom, prenom, actpass, dateinscbarr, villeref, adrcour
FROM dbo.Avocats
ORDER BY code;
