/* =====================================================================
   ALTER_DATETIME2_PROD.sql  (v3 - sans procédure temp)
   ---------------------------------------------------------------------
   Migration des colonnes date/heure de NVARCHAR/VARCHAR -> DATETIME2(0)
   pour toutes les tables AJOUTÉES par l'application web.

   À exécuter dans SSMS sur la base CardAvo.

   v3 : la procédure est créée DANS CardAvo (pas en #temp) pour éviter
        les conflits de collation entre tempdb (French_CI_AS) et
        CardAvo (SQL_Latin1_General_CP1_CI_AS). Elle est supprimée à la fin.

   IMPORTANT : Faire un BACKUP de CardAvo avant exécution.
   ===================================================================== */

SET NOCOUNT ON;
SET XACT_ABORT ON;

USE CardAvo;
GO

/* Nettoyage si un essai précédent a laissé la procédure */
IF OBJECT_ID('dbo.sp_ConvertToDateTime2', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_ConvertToDateTime2;
GO

/* ---------------------------------------------------------------------
   Procédure utilitaire (permanente dans CardAvo, dropée à la fin)
   --------------------------------------------------------------------- */
CREATE PROCEDURE dbo.sp_ConvertToDateTime2
    @schema     SYSNAME,
    @table      SYSNAME,
    @column     SYSNAME,
    @nullable   BIT = 1   -- 1 = NULL autorisé, 0 = NOT NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @current_type SYSNAME;
    DECLARE @sql NVARCHAR(MAX);
    DECLARE @full_name NVARCHAR(400) = QUOTENAME(@schema) + '.' + QUOTENAME(@table);
    DECLARE @object_id INT = OBJECT_ID(@full_name);

    IF @object_id IS NULL
    BEGIN
        PRINT '  [SKIP] ' + @full_name + ' : table inexistante.';
        RETURN;
    END

    /* 1. Récupère le type via sys.columns + COLUMNPROPERTY (pas de comparaison string -> pas de conflit collation) */
    DECLARE @col_id INT = COLUMNPROPERTY(@object_id, @column, 'ColumnId');

    IF @col_id IS NULL
    BEGIN
        PRINT '  [SKIP] ' + @full_name + '.' + @column + ' : colonne inexistante.';
        RETURN;
    END

    SELECT @current_type = TYPE_NAME(c.user_type_id)
    FROM sys.columns c
    WHERE c.object_id = @object_id
      AND c.column_id = @col_id;

    /* 2. Déjà au bon type ? */
    IF @current_type IN ('datetime', 'datetime2', 'smalldatetime', 'date')
    BEGIN
        PRINT '  [OK]   ' + @full_name + '.' + @column + ' : déjà ' + @current_type + ', aucune action.';
        RETURN;
    END

    /* 3. Sinon : conversion via colonne temp */
    IF @current_type NOT IN ('nvarchar', 'varchar', 'char', 'nchar', 'text', 'ntext')
    BEGIN
        PRINT '  [WARN] ' + @full_name + '.' + @column + ' : type inattendu (' + @current_type + '), ignoré.';
        RETURN;
    END

    PRINT '  [CONVERT] ' + @full_name + '.' + @column + ' : ' + @current_type + ' -> datetime2(0)';

    /* Compte les valeurs non convertibles avant action */
    DECLARE @bad_count INT = 0;
    SET @sql = N'SELECT @bad = COUNT(*) FROM ' + @full_name +
               N' WHERE ' + QUOTENAME(@column) + N' IS NOT NULL ' +
               N'   AND LTRIM(RTRIM(' + QUOTENAME(@column) + N')) <> '''' ' +
               N'   AND TRY_CONVERT(datetime2(0), ' + QUOTENAME(@column) + N') IS NULL';
    EXEC sp_executesql @sql, N'@bad INT OUTPUT', @bad = @bad_count OUTPUT;

    IF @bad_count > 0
        PRINT '           AVERTISSEMENT : ' + CAST(@bad_count AS NVARCHAR(10)) +
              ' valeur(s) non convertibles deviendront NULL.';

    /* a) Ajoute la colonne temp */
    SET @sql = N'ALTER TABLE ' + @full_name +
               N' ADD ' + QUOTENAME(@column + '_dt2_new') + N' datetime2(0) NULL;';
    EXEC sp_executesql @sql;

    /* b) Copie via TRY_CONVERT */
    SET @sql = N'UPDATE ' + @full_name +
               N' SET ' + QUOTENAME(@column + '_dt2_new') +
               N' = TRY_CONVERT(datetime2(0), ' + QUOTENAME(@column) + N');';
    EXEC sp_executesql @sql;

    /* c) Supprime l'éventuel DEFAULT lié, puis drop l'ancienne colonne
       Pas de comparaison string : on filtre via column_id récupéré plus haut. */
    DECLARE @def_name SYSNAME;
    SELECT @def_name = dc.name
    FROM sys.default_constraints dc
    JOIN sys.columns c
      ON c.default_object_id = dc.object_id
    WHERE dc.parent_object_id = @object_id
      AND c.object_id = @object_id
      AND c.column_id = @col_id;

    IF @def_name IS NOT NULL
    BEGIN
        SET @sql = N'ALTER TABLE ' + @full_name + N' DROP CONSTRAINT ' + QUOTENAME(@def_name) + N';';
        EXEC sp_executesql @sql;
    END

    SET @sql = N'ALTER TABLE ' + @full_name +
               N' DROP COLUMN ' + QUOTENAME(@column) + N';';
    EXEC sp_executesql @sql;

    /* d) Renomme la colonne temp pour récupérer le nom d'origine */
    DECLARE @rename_old NVARCHAR(400) = @full_name + '.' + QUOTENAME(@column + '_dt2_new');
    EXEC sp_rename @rename_old, @column, 'COLUMN';

    /* e) Applique la contrainte NOT NULL si demandée */
    IF @nullable = 0
    BEGIN
        SET @sql = N'UPDATE ' + @full_name +
                   N' SET ' + QUOTENAME(@column) + N' = SYSUTCDATETIME() ' +
                   N' WHERE ' + QUOTENAME(@column) + N' IS NULL;';
        EXEC sp_executesql @sql;

        SET @sql = N'ALTER TABLE ' + @full_name +
                   N' ALTER COLUMN ' + QUOTENAME(@column) + N' datetime2(0) NOT NULL;';
        EXEC sp_executesql @sql;
    END
END
GO


/* =====================================================================
   EXÉCUTION DES MIGRATIONS
   ===================================================================== */
PRINT '';
PRINT '=== Migration NVARCHAR -> DATETIME2(0) ===';
PRINT '';

PRINT '-- dbo.Avocats --';
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'Avocats', 'created_at', 1;
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'Avocats', 'updated_at', 1;

PRINT '-- dbo.Adresses --';
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'Adresses', 'created_at', 1;
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'Adresses', 'updated_at', 1;

PRINT '-- dbo.infomega --';
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'infomega', 'created_at', 1;
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'infomega', 'updated_at', 1;

PRINT '-- dbo.inhpra --';
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'inhpra', 'created_at', 1;
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'inhpra', 'updated_at', 1;
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'inhpra', 'datedeb',    1;
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'inhpra', 'datefin',    1;

PRINT '-- dbo.AppUsers --';
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'AppUsers', 'created_at', 0;

PRINT '-- dbo.AuditLog --';
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'AuditLog', 'timestamp', 0;

PRINT '-- dbo.Connexions --';
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'Connexions', 'created_at', 0;
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'Connexions', 'updated_at', 0;

PRINT '-- dbo.Mandats --';
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'Mandats', 'created_at',      0;
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'Mandats', 'updated_at',      0;
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'Mandats', 'date_ordonnance', 1;
EXEC dbo.sp_ConvertToDateTime2 'dbo', 'Mandats', 'date_emission',   1;

PRINT '';
PRINT '=== Migration terminée ===';
PRINT '';
GO

/* Nettoyage : on enlève la procédure utilitaire */
DROP PROCEDURE dbo.sp_ConvertToDateTime2;
GO


/* =====================================================================
   VÉRIFICATION FINALE
   Doit retourner DATA_TYPE = datetime2 pour toutes les lignes.
   ===================================================================== */
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dbo'
  AND (
        (TABLE_NAME = 'Avocats'    AND COLUMN_NAME IN ('created_at','updated_at')) OR
        (TABLE_NAME = 'Adresses'   AND COLUMN_NAME IN ('created_at','updated_at')) OR
        (TABLE_NAME = 'infomega'   AND COLUMN_NAME IN ('created_at','updated_at')) OR
        (TABLE_NAME = 'inhpra'     AND COLUMN_NAME IN ('created_at','updated_at','datedeb','datefin')) OR
        (TABLE_NAME = 'AppUsers'   AND COLUMN_NAME =  'created_at') OR
        (TABLE_NAME = 'AuditLog'   AND COLUMN_NAME =  'timestamp')  OR
        (TABLE_NAME = 'Connexions' AND COLUMN_NAME IN ('created_at','updated_at')) OR
        (TABLE_NAME = 'Mandats'    AND COLUMN_NAME IN ('created_at','updated_at','date_ordonnance','date_emission'))
      )
ORDER BY TABLE_NAME, COLUMN_NAME;
GO
