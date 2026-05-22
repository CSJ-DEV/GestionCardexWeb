/* =====================================================================
   ALTER_DATETIME2_PROD.sql
   ---------------------------------------------------------------------
   Migration des colonnes date/heure de NVARCHAR/VARCHAR  ->  DATETIME2(0)
   pour toutes les tables AJOUTÉES par l'application web.

   À exécuter dans SSMS sur la base CardAvo (legacy).

   Caractéristiques :
   - 100% idempotent : si la colonne est déjà en DATETIME / DATETIME2, on saute.
   - Préserve les données existantes via TRY_CONVERT (les chaînes ISO 8601
     'YYYY-MM-DDTHH:MM:SS' ou 'YYYY-MM-DD HH:MM:SS' sont reconnues).
   - Toute valeur non convertible devient NULL (visible dans le bloc PRINT).
   - Conserve le nom original de la colonne via sp_rename.

   Tables concernées (uniquement les colonnes ajoutées par l'app web) :
     dbo.Avocats     : created_at, updated_at
     dbo.Adresses    : created_at, updated_at
     dbo.infomega    : created_at, updated_at
     dbo.inhpra      : created_at, updated_at, datedeb, datefin
     dbo.AppUsers    : created_at
     dbo.AuditLog    : timestamp
     dbo.Connexions  : created_at, updated_at
     dbo.Mandats     : created_at, updated_at, date_ordonnance, date_emission

   IMPORTANT : Faire un BACKUP de CardAvo avant exécution.
   ===================================================================== */

SET NOCOUNT ON;
SET XACT_ABORT ON;

USE CardAvo;
GO

/* ---------------------------------------------------------------------
   Procédure utilitaire : convertit une colonne NVARCHAR/VARCHAR
   en DATETIME2(0) seulement si nécessaire.
   --------------------------------------------------------------------- */
IF OBJECT_ID('tempdb..#ConvertToDateTime2') IS NOT NULL
    DROP PROCEDURE #ConvertToDateTime2;
GO

CREATE PROCEDURE #ConvertToDateTime2
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
    DECLARE @null_clause NVARCHAR(20) = CASE WHEN @nullable = 1 THEN 'NULL' ELSE 'NOT NULL' END;

    /* 1. Récupère le type actuel
       NB : on force COLLATE DATABASE_DEFAULT pour éviter les conflits
       entre la collation de tempdb (où vit la procédure #temp) et celle
       de la base cible (ex : French_CI_AS vs SQL_Latin1_General_CP1_CI_AS). */
    SELECT @current_type = DATA_TYPE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA COLLATE DATABASE_DEFAULT = @schema COLLATE DATABASE_DEFAULT
      AND TABLE_NAME   COLLATE DATABASE_DEFAULT = @table  COLLATE DATABASE_DEFAULT
      AND COLUMN_NAME  COLLATE DATABASE_DEFAULT = @column COLLATE DATABASE_DEFAULT;

    IF @current_type IS NULL
    BEGIN
        PRINT '  [SKIP] ' + @full_name + '.' + @column + ' : colonne inexistante.';
        RETURN;
    END

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

    /* c) Drop l'ancienne colonne (les contraintes DEFAULT seront recréées plus bas) */
    /*    On supprime les éventuels DEFAULT constraints liés. */
    DECLARE @def_name SYSNAME;
    SELECT @def_name = dc.name
    FROM sys.default_constraints dc
    JOIN sys.columns c ON c.default_object_id = dc.object_id
    WHERE dc.parent_object_id = OBJECT_ID(@full_name)
      AND c.name COLLATE DATABASE_DEFAULT = @column COLLATE DATABASE_DEFAULT;

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
EXEC #ConvertToDateTime2 'dbo', 'Avocats', 'created_at', 1;
EXEC #ConvertToDateTime2 'dbo', 'Avocats', 'updated_at', 1;

PRINT '-- dbo.Adresses --';
EXEC #ConvertToDateTime2 'dbo', 'Adresses', 'created_at', 1;
EXEC #ConvertToDateTime2 'dbo', 'Adresses', 'updated_at', 1;

PRINT '-- dbo.infomega --';
EXEC #ConvertToDateTime2 'dbo', 'infomega', 'created_at', 1;
EXEC #ConvertToDateTime2 'dbo', 'infomega', 'updated_at', 1;

PRINT '-- dbo.inhpra --';
EXEC #ConvertToDateTime2 'dbo', 'inhpra', 'created_at', 1;
EXEC #ConvertToDateTime2 'dbo', 'inhpra', 'updated_at', 1;
EXEC #ConvertToDateTime2 'dbo', 'inhpra', 'datedeb',    1;
EXEC #ConvertToDateTime2 'dbo', 'inhpra', 'datefin',    1;

PRINT '-- dbo.AppUsers --';
EXEC #ConvertToDateTime2 'dbo', 'AppUsers', 'created_at', 0;   -- NOT NULL

PRINT '-- dbo.AuditLog --';
EXEC #ConvertToDateTime2 'dbo', 'AuditLog', 'timestamp', 0;    -- NOT NULL

PRINT '-- dbo.Connexions --';
EXEC #ConvertToDateTime2 'dbo', 'Connexions', 'created_at', 0; -- NOT NULL
EXEC #ConvertToDateTime2 'dbo', 'Connexions', 'updated_at', 0; -- NOT NULL

PRINT '-- dbo.Mandats --';
EXEC #ConvertToDateTime2 'dbo', 'Mandats', 'created_at',      0;  -- NOT NULL
EXEC #ConvertToDateTime2 'dbo', 'Mandats', 'updated_at',      0;  -- NOT NULL
EXEC #ConvertToDateTime2 'dbo', 'Mandats', 'date_ordonnance', 1;
EXEC #ConvertToDateTime2 'dbo', 'Mandats', 'date_emission',   1;

PRINT '';
PRINT '=== Migration terminée ===';
PRINT '';


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
