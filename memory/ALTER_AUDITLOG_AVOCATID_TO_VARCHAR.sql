/* =====================================================================
   ALTER_AUDITLOG_AVOCATID_TO_VARCHAR.sql  (v2 - gère l'index)
   ---------------------------------------------------------------------
   Convertit dbo.AuditLog.avocat_id de UNIQUEIDENTIFIER -> VARCHAR(36).

   v2 : drop/recreate de l'index IX_AuditLog_avocat_ts qui bloque l'ALTER.

   Idempotent : peut être ré-exécuté sans risque.
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
BEGIN
    PRINT '  [SKIP] dbo.AuditLog.avocat_id : colonne inexistante.';
    RETURN;
END

IF @type = 'varchar' OR @type = 'nvarchar'
BEGIN
    PRINT '  [OK]   dbo.AuditLog.avocat_id : déjà ' + @type + ', aucune action.';
    RETURN;
END

PRINT '  [CONVERT] dbo.AuditLog.avocat_id : ' + @type + ' -> varchar(36)';

/* 1. Drop l'index qui bloque l'ALTER (s'il existe) */
IF EXISTS (SELECT 1 FROM sys.indexes
           WHERE name = 'IX_AuditLog_avocat_ts'
             AND object_id = OBJECT_ID('dbo.AuditLog'))
BEGIN
    PRINT '  [DROP INDEX] IX_AuditLog_avocat_ts';
    DROP INDEX IX_AuditLog_avocat_ts ON dbo.AuditLog;
END

/* 2. Drop tout autre index qui référence avocat_id */
DECLARE @idx_name SYSNAME;
DECLARE idx_cursor CURSOR FOR
    SELECT DISTINCT i.name
    FROM sys.indexes i
    JOIN sys.index_columns ic ON ic.object_id = i.object_id AND ic.index_id = i.index_id
    JOIN sys.columns c        ON c.object_id  = ic.object_id AND c.column_id = ic.column_id
    WHERE i.object_id = OBJECT_ID('dbo.AuditLog')
      AND c.name COLLATE DATABASE_DEFAULT = 'avocat_id' COLLATE DATABASE_DEFAULT
      AND i.is_primary_key = 0
      AND i.name IS NOT NULL;

OPEN idx_cursor;
FETCH NEXT FROM idx_cursor INTO @idx_name;
WHILE @@FETCH_STATUS = 0
BEGIN
    PRINT '  [DROP INDEX] ' + @idx_name;
    EXEC ('DROP INDEX ' + @idx_name + ' ON dbo.AuditLog');
    FETCH NEXT FROM idx_cursor INTO @idx_name;
END
CLOSE idx_cursor;
DEALLOCATE idx_cursor;

/* 3. ALTER COLUMN */
ALTER TABLE dbo.AuditLog ALTER COLUMN avocat_id VARCHAR(36) NULL;
PRINT '  [DONE] ALTER COLUMN appliqué';

/* 4. Recrée l'index principal */
PRINT '  [CREATE INDEX] IX_AuditLog_avocat_ts (avocat_id, timestamp DESC)';
CREATE INDEX IX_AuditLog_avocat_ts
    ON dbo.AuditLog (avocat_id ASC, [timestamp] DESC);
GO

/* Vérification */
SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'AuditLog' AND COLUMN_NAME = 'avocat_id';

SELECT name AS index_name, type_desc
FROM sys.indexes
WHERE object_id = OBJECT_ID('dbo.AuditLog')
  AND name IS NOT NULL;
GO
