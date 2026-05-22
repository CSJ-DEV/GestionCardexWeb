/* =====================================================================
   ALTER_AUDITLOG_AVOCATID_TO_VARCHAR.sql
   ---------------------------------------------------------------------
   Convertit dbo.AuditLog.avocat_id de UNIQUEIDENTIFIER -> VARCHAR(36).

   Raison : depuis le refactor PK legacy, on stocke le `code` de l'avocat
   (ex: 'P10948') dans avocat_id, ce qui n'est pas un GUID. SQL Server
   refuse alors l'INSERT (8169 - Conversion failed).

   Caractéristiques :
   - 100% idempotent (vérifie le type avant ALTER).
   - Conversion naturelle GUID -> VARCHAR (pas de perte de données).
   - Ne touche pas aux lignes existantes.
   ===================================================================== */

SET NOCOUNT ON;
USE CardAvo;
GO

DECLARE @type SYSNAME;
SELECT @type = TYPE_NAME(c.user_type_id)
FROM sys.columns c
WHERE c.object_id = OBJECT_ID('dbo.AuditLog')
  AND c.name COLLATE DATABASE_DEFAULT = 'avocat_id' COLLATE DATABASE_DEFAULT;

IF @type IS NULL
    PRINT '  [SKIP] dbo.AuditLog.avocat_id : colonne inexistante.';
ELSE IF @type = 'varchar' OR @type = 'nvarchar'
    PRINT '  [OK]   dbo.AuditLog.avocat_id : déjà ' + @type + ', aucune action.';
ELSE
BEGIN
    PRINT '  [CONVERT] dbo.AuditLog.avocat_id : ' + @type + ' -> varchar(36)';
    ALTER TABLE dbo.AuditLog ALTER COLUMN avocat_id VARCHAR(36) NULL;
    PRINT '  [DONE]';
END
GO

/* Vérification */
SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dbo'
  AND TABLE_NAME   = 'AuditLog'
  AND COLUMN_NAME  = 'avocat_id';
GO
