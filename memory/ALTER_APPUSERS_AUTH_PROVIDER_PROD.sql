-- ============================================================
-- AJOUT DE LA COLONNE auth_provider SUR AppUsers (PROD)
-- ============================================================
-- Contexte: la migration auto au startup du backend FastAPI échoue
-- car le compte SQL applicatif n'a pas les droits DDL (ALTER TABLE).
-- C'est normal et sécuritaire. Ce script doit être exécuté UNE FOIS
-- par le DBA (sysadmin/db_owner) dans SSMS sur la base CardAvo.
--
-- Cette colonne permet de distinguer les comptes:
--   - 'local' : authentification par email/mdp (formulaire JWT)
--   - 'entra' : authentification par Microsoft Entra ID (SSO)
-- ============================================================

USE CardAvo;
GO

-- 1. Ajout idempotent de la colonne
IF NOT EXISTS (
    SELECT 1 FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.AppUsers') AND name = 'auth_provider'
)
BEGIN
    ALTER TABLE dbo.AppUsers
    ADD auth_provider NVARCHAR(20) NOT NULL
    CONSTRAINT DF_AppUsers_auth_provider DEFAULT 'local';
    PRINT '✅ Colonne auth_provider ajoutée avec succès.';
END
ELSE
BEGIN
    PRINT 'ℹ️  Colonne auth_provider déjà présente — aucune action.';
END
GO

-- 2. Vérification
SELECT email, role, auth_provider, created_at
FROM dbo.AppUsers
ORDER BY email;
GO

-- ============================================================
-- APRÈS EXÉCUTION DE CE SCRIPT :
--   1. Redémarrer l'App Service (Azure Portal → Restart)
--      ou attendre le prochain auto-restart (changement de config).
--   2. Se déconnecter de l'application puis se reconnecter via
--      "Se connecter avec Microsoft" — le backend va alors mettre
--      auth_provider='entra' automatiquement sur les comptes SSO.
-- ============================================================
