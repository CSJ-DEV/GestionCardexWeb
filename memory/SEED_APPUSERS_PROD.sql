-- ============================================================
--   SEED des comptes utilisateurs — GestionCardex
-- ============================================================
-- À exécuter UNE SEULE FOIS dans la base CardAvo après la création
-- de la table AppUsers (voir /app/memory/TABLES_AJOUTEES_APP.md).
--
-- Crée les 4 comptes par défaut. Idempotent : ne réinsère pas si
-- l'email existe déjà.
--
-- ⚠️ IMPORTANT — SÉCURITÉ :
--   1. Connectez-vous à l'application IMMÉDIATEMENT après cette
--      insertion et changez les 4 mots de passe via la page
--      "Mon profil".
--   2. Ne laissez JAMAIS ces mots de passe par défaut en production.
--   3. Ne committez JAMAIS ce fichier avec les vrais hash dans un
--      dépôt public.
-- ============================================================

USE [CardAvo];
GO

-- ------------------------------------------------------------
--                  COMPTES PAR DÉFAUT
-- ------------------------------------------------------------
-- email                           rôle       mot de passe initial
-- admin@gestioncardex.qc          admin      Admin2026!
-- ti@gestioncardex.qc             ti         Ti2026!
-- editeur@gestioncardex.qc        editeur    Editeur2026!
-- lecteur@gestioncardex.qc        lecteur    Lecteur2026!
-- ------------------------------------------------------------

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
    PRINT 'Compte admin@gestioncardex.qc créé.';
END
ELSE
    PRINT 'Compte admin@gestioncardex.qc déjà existant — ignoré.';
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
    PRINT 'Compte ti@gestioncardex.qc créé.';
END
ELSE
    PRINT 'Compte ti@gestioncardex.qc déjà existant — ignoré.';
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
    PRINT 'Compte editeur@gestioncardex.qc créé.';
END
ELSE
    PRINT 'Compte editeur@gestioncardex.qc déjà existant — ignoré.';
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
    PRINT 'Compte lecteur@gestioncardex.qc créé.';
END
ELSE
    PRINT 'Compte lecteur@gestioncardex.qc déjà existant — ignoré.';
GO

-- ------------------------------------------------------------
--                  VÉRIFICATION
-- ------------------------------------------------------------
SELECT [email], [name], [role], [created_at]
FROM [dbo].[AppUsers]
ORDER BY
    CASE [role]
        WHEN 'admin' THEN 1
        WHEN 'ti' THEN 2
        WHEN 'editeur' THEN 3
        WHEN 'lecteur' THEN 4
        ELSE 5
    END;
GO

PRINT '';
PRINT '✅ Seed terminé. Connectez-vous IMMÉDIATEMENT et changez les 4 mots de passe.';
PRINT '   Page : /profil (visible dans la sidebar pour tous les rôles).';
