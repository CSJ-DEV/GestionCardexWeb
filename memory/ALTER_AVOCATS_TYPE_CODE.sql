-- Ajout rapide de la colonne type_code manquante sur dbo.Avocats
-- À exécuter dans SSMS sur CSJ-SQL-TEST → base CardAvo
USE [CardAvo];
GO

IF COL_LENGTH('dbo.Avocats', 'type_code') IS NULL
BEGIN
    ALTER TABLE dbo.Avocats
    ADD type_code NVARCHAR(1) NOT NULL
        CONSTRAINT DF_Avocats_type_code DEFAULT 'A';
    PRINT '  + colonne type_code ajoutée (defaut=A)';
END
ELSE
    PRINT '  · type_code déjà présente';
GO

-- Backfill : déduire type_code à partir de la 1re lettre du code (A/P/N)
UPDATE dbo.Avocats
SET type_code = UPPER(LEFT(code, 1))
WHERE code IS NOT NULL
  AND UPPER(LEFT(code, 1)) IN ('A', 'P', 'N')
  AND type_code = 'A';  -- valeur par défaut posée par l'ALTER
PRINT CONCAT('  + ', @@ROWCOUNT, ' lignes mises à jour avec type_code déduit du code');
GO

-- Vérification
SELECT TOP 5 code, type_code, nom, prenom FROM dbo.Avocats ORDER BY code;
