-- =============================================================================
--   GestionCardex — Script unique d'initialisation pour SQL Server
-- =============================================================================
--   À exécuter UNE SEULE FOIS dans la base [CardAvo] via SSMS :
--     1. Connectez-vous au serveur CSJ-SQL-TEST
--     2. Sélectionnez la base "CardAvo" dans la liste déroulante en haut
--     3. Ouvrez ce fichier (ou collez-le dans un nouvel onglet)
--     4. Cliquez "Exécuter" (F5)
--
--   Ce script :
--     • Crée les 4 tables ajoutées par l'app web :
--         AppUsers, AuditLog, Connexions, Mandats
--     • Seed les 4 comptes utilisateurs (admin / ti / editeur / lecteur)
--     • Seed les 3 connexions vers CSJ-SQL-TEST (CardAvo / StaticPc / Art52)
--
--   Le script est entièrement IDEMPOTENT : il peut être relancé sans danger,
--   il ne créera/n'insérera pas ce qui existe déjà.
-- =============================================================================

USE [CardAvo];
GO

PRINT '=== GestionCardex : initialisation de la base CardAvo ===';
PRINT '';

-- =============================================================================
--                  PARTIE 1 — CRÉATION DES 4 TABLES APP
-- =============================================================================

------------------------------------------------------------------------------
-- 1.1 — Table AppUsers : comptes utilisateurs (admin/ti/editeur/lecteur)
------------------------------------------------------------------------------
IF OBJECT_ID(N'[dbo].[AppUsers]', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[AppUsers](
        [id]            [nvarchar](36)  NOT NULL,
        [email]         [nvarchar](200) NOT NULL,
        [password_hash] [nvarchar](100) NOT NULL,
        [name]          [nvarchar](200) NULL,
        [role]          [nvarchar](20)  NOT NULL,
        [created_at]    [datetime2](7)  NOT NULL CONSTRAINT [DF_AppUsers_created_at] DEFAULT (sysutcdatetime()),
        CONSTRAINT [PK_AppUsers] PRIMARY KEY CLUSTERED ([id] ASC),
        CONSTRAINT [CK_AppUsers_role] CHECK ([role] IN (N'admin', N'ti', N'editeur', N'lecteur'))
    );
    CREATE UNIQUE NONCLUSTERED INDEX [UX_AppUsers_email] ON [dbo].[AppUsers]([email] ASC);
    PRINT '  ✓ Table AppUsers créée.';
END
ELSE
    PRINT '  · Table AppUsers déjà existante.';
GO

------------------------------------------------------------------------------
-- 1.2 — Table AuditLog : historique des modifications par avocat
------------------------------------------------------------------------------
IF OBJECT_ID(N'[dbo].[AuditLog]', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[AuditLog](
        [id]         [nvarchar](36)  NOT NULL,
        [avocat_id]  [nvarchar](36)  NOT NULL,
        [action]     [nvarchar](40)  NOT NULL,
        [user_email] [nvarchar](200) NOT NULL,
        [summary]    [nvarchar](500) NULL,
        [timestamp]  [datetime2](7)  NOT NULL CONSTRAINT [DF_AuditLog_timestamp] DEFAULT (sysutcdatetime()),
        CONSTRAINT [PK_AuditLog] PRIMARY KEY CLUSTERED ([id] ASC)
    );
    CREATE NONCLUSTERED INDEX [IX_AuditLog_avocat_ts] ON [dbo].[AuditLog]([avocat_id] ASC, [timestamp] DESC);
    PRINT '  ✓ Table AuditLog créée.';
END
ELSE
    PRINT '  · Table AuditLog déjà existante.';
GO

------------------------------------------------------------------------------
-- 1.3 — Table Connexions : catalogue des connexions BDD (admin TI uniquement)
------------------------------------------------------------------------------
IF OBJECT_ID(N'[dbo].[Connexions]', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[Connexions](
        [id]           [nvarchar](36)  NOT NULL,
        [name]         [nvarchar](100) NOT NULL,
        [type]         [nvarchar](20)  NOT NULL,
        [server]       [nvarchar](200) NOT NULL,
        [port]         [int]           NULL,
        [user]         [nvarchar](100) NULL,
        [database]     [nvarchar](100) NULL,
        [description]  [nvarchar](max) NULL,
        [password_enc] [nvarchar](500) NULL,
        [is_primary]   [bit]           NOT NULL CONSTRAINT [DF_Connexions_is_primary] DEFAULT (0),
        [created_at]   [datetime2](7)  NOT NULL CONSTRAINT [DF_Connexions_created_at] DEFAULT (sysutcdatetime()),
        [updated_at]   [datetime2](7)  NOT NULL CONSTRAINT [DF_Connexions_updated_at] DEFAULT (sysutcdatetime()),
        CONSTRAINT [PK_Connexions] PRIMARY KEY CLUSTERED ([id] ASC),
        CONSTRAINT [CK_Connexions_type] CHECK ([type] IN (N'mongodb', N'sqlserver', N'sqlite'))
    );
    CREATE UNIQUE NONCLUSTERED INDEX [UX_Connexions_name] ON [dbo].[Connexions]([name] ASC);
    PRINT '  ✓ Table Connexions créée.';
END
ELSE
    PRINT '  · Table Connexions déjà existante.';
GO

------------------------------------------------------------------------------
-- 1.4 — Table Mandats : mandats légaux (Registre 97 / Registre 98)
------------------------------------------------------------------------------
IF OBJECT_ID(N'[dbo].[Mandats]', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[Mandats](
        [id]              [nvarchar](36)  NOT NULL,
        [avocat_id]       [nvarchar](36)  NOT NULL,
        [requerant]       [nvarchar](200) NULL,
        [article]         [nvarchar](20)  NOT NULL CONSTRAINT [DF_Mandats_article] DEFAULT (N'486.3'),
        [date_ordonnance] [nvarchar](30)  NULL,
        [date_emission]   [nvarchar](30)  NULL,
        [numero]          [nvarchar](50)  NULL,
        [groupe]          [nvarchar](50)  NOT NULL CONSTRAINT [DF_Mandats_groupe] DEFAULT (N'Pratique Privée'),
        [commentaire]     [nvarchar](max) NULL,
        [usermodif]       [nvarchar](50)  NULL,
        [created_at]      [datetime2](7)  NOT NULL CONSTRAINT [DF_Mandats_created_at] DEFAULT (sysutcdatetime()),
        [updated_at]      [datetime2](7)  NOT NULL CONSTRAINT [DF_Mandats_updated_at] DEFAULT (sysutcdatetime()),
        CONSTRAINT [PK_Mandats] PRIMARY KEY CLUSTERED ([id] ASC),
        CONSTRAINT [CK_Mandats_article] CHECK ([article] IN (N'486.3', N'486.7', N'672', N'684'))
    );
    CREATE NONCLUSTERED INDEX [IX_Mandats_avocat] ON [dbo].[Mandats]([avocat_id] ASC);
    CREATE NONCLUSTERED INDEX [IX_Mandats_dates]  ON [dbo].[Mandats]([date_ordonnance] ASC);
    PRINT '  ✓ Table Mandats créée.';
END
ELSE
    PRINT '  · Table Mandats déjà existante.';
GO

PRINT '';
PRINT '=== PARTIE 1 (tables) terminée ===';
PRINT '';


-- =============================================================================
--                  PARTIE 2 — SEED DES UTILISATEURS
-- =============================================================================
-- Mots de passe initiaux (à CHANGER IMMÉDIATEMENT après 1re connexion) :
--   admin    @ gestioncardex.qc → Admin2026!
--   ti       @ gestioncardex.qc → Ti2026!
--   editeur  @ gestioncardex.qc → Editeur2026!
--   lecteur  @ gestioncardex.qc → Lecteur2026!
-- =============================================================================

-- 🔴 Administrateur
IF NOT EXISTS (SELECT 1 FROM [dbo].[AppUsers] WHERE [email] = N'admin@gestioncardex.qc')
BEGIN
    INSERT INTO [dbo].[AppUsers] ([id], [email], [password_hash], [name], [role], [created_at])
    VALUES (
        CONVERT(NVARCHAR(36), NEWID()),
        N'admin@gestioncardex.qc',
        N'$2b$12$C3ce6PhPIdDZzijSspGVUeaOmuEnDaTbJZynUsW7Ja.TJQQtb.fU2',
        N'Administrateur',
        N'admin',
        SYSUTCDATETIME()
    );
    PRINT '  ✓ User admin@gestioncardex.qc créé (mdp: Admin2026!).';
END
ELSE
    PRINT '  · User admin@gestioncardex.qc déjà existant.';
GO

-- 🟠 Technicien TI
IF NOT EXISTS (SELECT 1 FROM [dbo].[AppUsers] WHERE [email] = N'ti@gestioncardex.qc')
BEGIN
    INSERT INTO [dbo].[AppUsers] ([id], [email], [password_hash], [name], [role], [created_at])
    VALUES (
        CONVERT(NVARCHAR(36), NEWID()),
        N'ti@gestioncardex.qc',
        N'$2b$12$OgEJ0h/GaS2jNF6C5YKlxeluKYfDL74Pe4ZmgYKguACc6DJl5D6s2',
        N'Technicien TI',
        N'ti',
        SYSUTCDATETIME()
    );
    PRINT '  ✓ User ti@gestioncardex.qc créé (mdp: Ti2026!).';
END
ELSE
    PRINT '  · User ti@gestioncardex.qc déjà existant.';
GO

-- 🔵 Éditeur
IF NOT EXISTS (SELECT 1 FROM [dbo].[AppUsers] WHERE [email] = N'editeur@gestioncardex.qc')
BEGIN
    INSERT INTO [dbo].[AppUsers] ([id], [email], [password_hash], [name], [role], [created_at])
    VALUES (
        CONVERT(NVARCHAR(36), NEWID()),
        N'editeur@gestioncardex.qc',
        N'$2b$12$56GIaQsZowOctulRM4qLxu/OCgqQgz1wFHoQm9pdbZjqVXVbP8Kne',
        N'Éditeur',
        N'editeur',
        SYSUTCDATETIME()
    );
    PRINT '  ✓ User editeur@gestioncardex.qc créé (mdp: Editeur2026!).';
END
ELSE
    PRINT '  · User editeur@gestioncardex.qc déjà existant.';
GO

-- ⚪ Lecteur
IF NOT EXISTS (SELECT 1 FROM [dbo].[AppUsers] WHERE [email] = N'lecteur@gestioncardex.qc')
BEGIN
    INSERT INTO [dbo].[AppUsers] ([id], [email], [password_hash], [name], [role], [created_at])
    VALUES (
        CONVERT(NVARCHAR(36), NEWID()),
        N'lecteur@gestioncardex.qc',
        N'$2b$12$TeE83NhMvS5tTzJn6G2L2.GFsGcGMjuh9tlzXaFCv3k25/h7YEtWW',
        N'Lecteur',
        N'lecteur',
        SYSUTCDATETIME()
    );
    PRINT '  ✓ User lecteur@gestioncardex.qc créé (mdp: Lecteur2026!).';
END
ELSE
    PRINT '  · User lecteur@gestioncardex.qc déjà existant.';
GO

PRINT '';
PRINT '=== PARTIE 2 (utilisateurs) terminée ===';
PRINT '';


-- =============================================================================
--          PARTIE 3 — SEED DES CONNEXIONS (CSJ-SQL-TEST, user Daj)
-- =============================================================================
-- Les 3 connexions sont créées SANS mot de passe (password_enc vide).
-- Le TI devra ajouter le mot de passe via la page "Connexions" de l'app web :
--   bouton "Modifier" → champ "Mot de passe" → l'app le chiffre via Fernet.
-- =============================================================================

-- 🔵 CardAvo (principale, is_primary = 1)
IF NOT EXISTS (SELECT 1 FROM [dbo].[Connexions] WHERE [name] = N'CardAvo (SQL Server)')
BEGIN
    INSERT INTO [dbo].[Connexions]
        ([id], [name], [type], [server], [port], [user], [database],
         [description], [password_enc], [is_primary], [created_at], [updated_at])
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
    PRINT '  ✓ Connexion CardAvo (SQL Server) créée — is_primary = 1.';
END
ELSE
    PRINT '  · Connexion CardAvo (SQL Server) déjà existante.';
GO

-- 🔵 StaticPc (référentiels — 84 tables)
IF NOT EXISTS (SELECT 1 FROM [dbo].[Connexions] WHERE [name] = N'StaticPc (SQL Server)')
BEGIN
    INSERT INTO [dbo].[Connexions]
        ([id], [name], [type], [server], [port], [user], [database],
         [description], [password_enc], [is_primary], [created_at], [updated_at])
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
    PRINT '  ✓ Connexion StaticPc (SQL Server) créée.';
END
ELSE
    PRINT '  · Connexion StaticPc (SQL Server) déjà existante.';
GO

-- 🔵 Art52 (paiements / art. 52 — 126 tables)
IF NOT EXISTS (SELECT 1 FROM [dbo].[Connexions] WHERE [name] = N'Art52 (SQL Server)')
BEGIN
    INSERT INTO [dbo].[Connexions]
        ([id], [name], [type], [server], [port], [user], [database],
         [description], [password_enc], [is_primary], [created_at], [updated_at])
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
    PRINT '  ✓ Connexion Art52 (SQL Server) créée.';
END
ELSE
    PRINT '  · Connexion Art52 (SQL Server) déjà existante.';
GO

PRINT '';
PRINT '=== PARTIE 3 (connexions) terminée ===';
PRINT '';


-- =============================================================================
--                  PARTIE 4 — VÉRIFICATION FINALE
-- =============================================================================
PRINT '=== Récapitulatif des données insérées ===';
PRINT '';
PRINT 'TABLES :';
SELECT
    name AS [Table],
    (SELECT SUM(p.rows) FROM sys.partitions p
     WHERE p.object_id = t.object_id AND p.index_id IN (0,1)) AS [Nb_lignes]
FROM sys.tables t
WHERE name IN ('AppUsers','AuditLog','Connexions','Mandats')
ORDER BY name;

PRINT '';
PRINT 'COMPTES UTILISATEURS :';
SELECT [email], [name], [role], [created_at]
FROM [dbo].[AppUsers]
ORDER BY
    CASE [role]
        WHEN 'admin'   THEN 1
        WHEN 'ti'      THEN 2
        WHEN 'editeur' THEN 3
        WHEN 'lecteur' THEN 4
        ELSE 5
    END;

PRINT '';
PRINT 'CONNEXIONS :';
SELECT
    [name],
    [server] + N':' + CAST([port] AS NVARCHAR(10)) AS [serveur_port],
    [user]   AS [utilisateur],
    [database],
    [is_primary],
    CASE WHEN LEN([password_enc]) > 0 THEN 'Oui' ELSE 'Non' END AS [mdp_defini]
FROM [dbo].[Connexions]
ORDER BY [is_primary] DESC, [name];

PRINT '';
PRINT '════════════════════════════════════════════════════════════════════';
PRINT '  ✅ Initialisation terminée avec succès.';
PRINT '';
PRINT '  Prochaines étapes :';
PRINT '    1. Connectez-vous à l''application avec admin@gestioncardex.qc';
PRINT '       (mot de passe : Admin2026!).';
PRINT '    2. CHANGEZ IMMÉDIATEMENT le mot de passe via "Mon profil".';
PRINT '    3. Demandez à chaque utilisateur final de faire de même.';
PRINT '    4. Connectez-vous en tant que ti@gestioncardex.qc';
PRINT '       (mot de passe : Ti2026!), puis dans "Connexions",';
PRINT '       ajoutez le mot de passe SQL pour CardAvo / StaticPc / Art52';
PRINT '       et testez chaque connexion avec le bouton ⚡.';
PRINT '════════════════════════════════════════════════════════════════════';
