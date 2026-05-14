-- ============================================================
--   SEED de la table Connexions — GestionCardex
-- ============================================================
-- À exécuter UNE SEULE FOIS dans la base CardAvo après la création
-- de la table Connexions (voir /app/memory/TABLES_AJOUTEES_APP.md).
--
-- Insère les 3 connexions vers le serveur CSJ-SQL-TEST :
--   • CardAvo  (principale, lecture seule côté UI)
--   • StaticPc (référentiels)
--   • Art52    (paiements / art. 52)
--
-- Script idempotent : ne réinsère pas si le name existe déjà.
--
-- ⚠️ MOT DE PASSE
--   Les 3 connexions sont créées SANS mot de passe (password_enc vide).
--   Le TI devra l'ajouter plus tard depuis l'interface :
--     1. Se connecter à l'app avec le compte ti@gestioncardex.qc
--     2. Aller dans "Connexions" (sidebar)
--     3. Cliquer "Modifier" sur chaque connexion
--     4. Saisir le mot de passe → l'app le chiffre via Fernet et stocke
--        la valeur chiffrée dans password_enc.
-- ============================================================

USE [CardAvo];
GO

-- ------------------------------------------------------------
--   1. CardAvo — connexion PRINCIPALE (is_primary = 1)
-- ------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM [dbo].[Connexions] WHERE [name] = N'CardAvo (SQL Server)')
BEGIN
    INSERT INTO [dbo].[Connexions]
        ([id], [name], [type], [server], [port], [user], [database],
         [description], [password_enc], [is_primary],
         [created_at], [updated_at])
    VALUES (
        CONVERT(NVARCHAR(36), NEWID()),
        N'CardAvo (SQL Server)',
        N'sqlserver',
        N'CSJ-SQL-TEST',
        1433,
        N'Daj',
        N'CardAvo',
        N'Base principale de l''application — Avocats, Adresses, infomega, inhpra, Mandats, AppUsers, AuditLog, Connexions. Connexion utilisée par l''app elle-même : lecture seule depuis l''UI.',
        N'',
        1,
        SYSUTCDATETIME(),
        SYSUTCDATETIME()
    );
    PRINT 'Connexion CardAvo (SQL Server) créée — is_primary = 1.';
END
ELSE
    PRINT 'Connexion CardAvo (SQL Server) déjà existante — ignoré.';
GO

-- ------------------------------------------------------------
--   2. StaticPc — référentiels (84 tables)
-- ------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM [dbo].[Connexions] WHERE [name] = N'StaticPc (SQL Server)')
BEGIN
    INSERT INTO [dbo].[Connexions]
        ([id], [name], [type], [server], [port], [user], [database],
         [description], [password_enc], [is_primary],
         [created_at], [updated_at])
    VALUES (
        CONVERT(NVARCHAR(36), NEWID()),
        N'StaticPc (SQL Server)',
        N'sqlserver',
        N'CSJ-SQL-TEST',
        1433,
        N'Daj',
        N'StaticPc',
        N'Base de référence — 84 tables (codes, listes de valeurs, paramètres). Lecture seule dans la majorité des cas.',
        N'',
        0,
        SYSUTCDATETIME(),
        SYSUTCDATETIME()
    );
    PRINT 'Connexion StaticPc (SQL Server) créée.';
END
ELSE
    PRINT 'Connexion StaticPc (SQL Server) déjà existante — ignoré.';
GO

-- ------------------------------------------------------------
--   3. Art52 — paiements / art. 52 (126 tables)
-- ------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM [dbo].[Connexions] WHERE [name] = N'Art52 (SQL Server)')
BEGIN
    INSERT INTO [dbo].[Connexions]
        ([id], [name], [type], [server], [port], [user], [database],
         [description], [password_enc], [is_primary],
         [created_at], [updated_at])
    VALUES (
        CONVERT(NVARCHAR(36), NEWID()),
        N'Art52 (SQL Server)',
        N'sqlserver',
        N'CSJ-SQL-TEST',
        1433,
        N'Daj',
        N'Art52',
        N'Base Article 52 — 126 tables (paiements, règlements, comptabilité art. 52).',
        N'',
        0,
        SYSUTCDATETIME(),
        SYSUTCDATETIME()
    );
    PRINT 'Connexion Art52 (SQL Server) créée.';
END
ELSE
    PRINT 'Connexion Art52 (SQL Server) déjà existante — ignoré.';
GO

-- ------------------------------------------------------------
--   Nettoyage optionnel : supprimer les seeds SQLite de dev
-- ------------------------------------------------------------
-- Si vous voyez d'anciennes lignes "CardAvo (SQLite local)" etc.
-- (créées en dev par le seed automatique du backend Python),
-- décommentez ces lignes pour les supprimer après votre passage en prod :
--
-- DELETE FROM [dbo].[Connexions] WHERE [name] IN (
--     N'CardAvo (SQLite local)',
--     N'StaticPc (SQLite local)',
--     N'Art52 (SQLite local)'
-- );
-- PRINT 'Anciens seeds SQLite supprimés.';
-- GO

-- ------------------------------------------------------------
--                  VÉRIFICATION
-- ------------------------------------------------------------
SELECT
    [name], [type], [server], [port], [user], [database],
    [is_primary],
    CASE WHEN LEN([password_enc]) > 0 THEN 'Oui' ELSE 'Non' END AS [Mot_de_passe_defini],
    [created_at]
FROM [dbo].[Connexions]
ORDER BY [is_primary] DESC, [name];
GO

PRINT '';
PRINT '✅ Seed terminé.';
PRINT '   Prochaines étapes :';
PRINT '     1. Se connecter en tant que ti@gestioncardex.qc';
PRINT '     2. Aller dans la page "Connexions"';
PRINT '     3. Modifier chaque connexion pour ajouter le mot de passe';
PRINT '        (chiffré automatiquement via Fernet par le backend).';
PRINT '     4. Tester chaque connexion avec le bouton ⚡ (PlugZap).';
