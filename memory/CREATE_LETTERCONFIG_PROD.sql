-- ============================================================
-- CRÉATION DE LA TABLE LetterConfig (PROD)
-- ============================================================
-- Contexte: configuration singleton de la lettre PDF officielle envoyée
-- aux avocats (Code utilisateur et mots de passe). Stocke le signataire
-- courant et l'image de signature manuscrite.
-- À exécuter par le DBA (sysadmin/db_owner) dans SSMS sur CardAvo.
-- ============================================================

USE CardAvo;
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'LetterConfig')
BEGIN
    CREATE TABLE dbo.LetterConfig (
        id                      INT             NOT NULL PRIMARY KEY,  -- toujours 1
        signataire_nom          NVARCHAR(200)   NOT NULL DEFAULT '',
        signataire_titre        NVARCHAR(200)   NOT NULL DEFAULT '',
        signataire_affiliation  NVARCHAR(200)   NOT NULL DEFAULT 'Commission des services juridiques',
        signature_image_base64  NVARCHAR(MAX)   NULL,    -- PNG/JPG en base64
        signature_mime          NVARCHAR(50)    NULL,    -- 'image/png' ou 'image/jpeg'
        updated_at              DATETIME2(0)    NOT NULL DEFAULT SYSDATETIME(),
        updated_by              NVARCHAR(200)   NULL
    );
    PRINT '✅ Table LetterConfig créée.';

    -- Insérer la ligne par défaut (signataire actuel)
    INSERT INTO dbo.LetterConfig
        (id, signataire_nom, signataire_titre, signataire_affiliation, updated_at, updated_by)
    VALUES
        (1, N'M. Yves Boisvert, CPA, CGA',
            N'Directeur des services financiers',
            N'Commission des services juridiques',
            SYSDATETIME(),
            N'system');
    PRINT '✅ Ligne singleton id=1 insérée (signataire par défaut).';
END
ELSE
BEGIN
    PRINT 'ℹ️  Table LetterConfig déjà présente — aucune action.';
END
GO

-- Vérification
SELECT id, signataire_nom, signataire_titre, signataire_affiliation,
       CASE WHEN signature_image_base64 IS NULL THEN 'NON' ELSE 'OUI' END AS has_signature,
       updated_at, updated_by
FROM dbo.LetterConfig;
GO
