-- ============================================================
-- AJOUT DES COLONNES email_subject + email_body À LetterConfig
-- ============================================================
-- Contexte: permet aux utilisateurs TI de personnaliser via l'UI le
-- sujet et le contenu du courriel envoyé automatiquement aux avocats
-- lors de la réinitialisation de mots de passe ou de l'envoi de la
-- lettre depuis l'onglet Web.
--
-- L'application fonctionne SANS ces colonnes (fallback aux valeurs
-- par défaut codées en dur), mais la personnalisation TI ne sera
-- persistée qu'APRÈS exécution de ce script.
--
-- À exécuter par le DBA (sysadmin/db_owner) dans SSMS sur CardAvo.
-- ============================================================

USE CardAvo;
GO

-- Ajout email_subject
IF NOT EXISTS (
    SELECT 1 FROM sys.columns
    WHERE Name = N'email_subject'
      AND Object_ID = Object_ID(N'dbo.LetterConfig')
)
BEGIN
    ALTER TABLE dbo.LetterConfig
        ADD email_subject NVARCHAR(500) NULL;
    PRINT '✅ Colonne email_subject ajoutée à LetterConfig.';
END
ELSE
BEGIN
    PRINT 'ℹ️  Colonne email_subject déjà présente — aucune action.';
END
GO

-- Ajout email_body
IF NOT EXISTS (
    SELECT 1 FROM sys.columns
    WHERE Name = N'email_body'
      AND Object_ID = Object_ID(N'dbo.LetterConfig')
)
BEGIN
    ALTER TABLE dbo.LetterConfig
        ADD email_body NVARCHAR(MAX) NULL;
    PRINT '✅ Colonne email_body ajoutée à LetterConfig.';
END
ELSE
BEGIN
    PRINT 'ℹ️  Colonne email_body déjà présente — aucune action.';
END
GO

-- Pré-remplissage de la ligne singleton avec les valeurs par défaut
UPDATE dbo.LetterConfig
SET email_subject = N'Réinitialisation de vos mots de passe — Aide juridique du Québec',
    email_body = N'Bonjour Me {nom},

Vos mots de passe Web de l''application GestionCardex ont été réinitialisés à votre demande.

Vous trouverez en pièce jointe (PDF) vos nouveaux identifiants (Mot de passe 1 et Mot de passe 2).

Pour des raisons de sécurité, conservez ce document en lieu sûr et ne le transférez pas par courriel.

Ceci est un message automatique — merci de ne pas y répondre.'
WHERE id = 1
  AND (email_subject IS NULL OR email_subject = '');
GO

-- Vérification
SELECT id,
       LEN(email_subject) AS subject_len,
       LEN(email_body)    AS body_len,
       CASE WHEN signature_image_base64 IS NULL THEN 'NON' ELSE 'OUI' END AS has_signature,
       updated_at,
       updated_by
FROM dbo.LetterConfig;
GO
