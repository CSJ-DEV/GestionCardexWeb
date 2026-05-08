# Tables ajoutées par l'application web GestionCardex

> **Contexte** : ces 3 tables n'existent pas dans la base de données SQL Server `sCardAvo` legacy (Visual Basic). Elles ont été créées spécifiquement pour les besoins de la nouvelle application web :
> - **AppUsers** : authentification JWT moderne (remplace l'authentification SQL Server par défaut)
> - **AuditLog** : traçabilité des modifications (qui a modifié quoi et quand)
> - **Connexions** : configuration centralisée des connexions BDD (module TI)
>
> Ces tables sont déjà créées dans le **fichier SQLite local** (`sqlite_dbs/sCardAvo.db`) pour le développement.
> Pour les recréer côté **SQL Server production**, utilisez les scripts `T-SQL` ci-dessous.

---

## 📋 Vue d'ensemble

| Table | Rôle | Lignes attendues |
|-------|------|------------------|
| `AppUsers` | Comptes utilisateurs de l'app (admin / ti / éditeur / lecteur) | quelques dizaines |
| `AuditLog` | Historique de chaque modification de fiche avocat | en croissance continue |
| `Connexions` | Catalogue des connexions BDD (MongoDB / SQL Server / SQLite) | < 20 |

---

## 1️⃣ `AppUsers` — Comptes utilisateurs de l'application

```sql
USE [CardAvo];
GO

CREATE TABLE [dbo].[AppUsers](
    [id]            [uniqueidentifier] NOT NULL,                 -- UUID v4
    [email]         [varchar](200)     NOT NULL,                 -- normalisé en minuscules, unique
    [password_hash] [varchar](100)     NOT NULL,                 -- bcrypt 60 chars
    [name]          [varchar](200)     NULL,
    [role]          [varchar](20)      NOT NULL,                 -- admin / ti / editeur / lecteur
    [created_at]    [datetime2](7)     NOT NULL CONSTRAINT [DF_AppUsers_created_at] DEFAULT (sysutcdatetime()),
 CONSTRAINT [PK_AppUsers] PRIMARY KEY CLUSTERED
(
    [id] ASC
) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UX_AppUsers_email] UNIQUE NONCLUSTERED
(
    [email] ASC
) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY];
GO

ALTER TABLE [dbo].[AppUsers]
    ADD CONSTRAINT [CK_AppUsers_role] CHECK ([role] IN ('admin','ti','editeur','lecteur'));
GO
```

### Notes
- Le mot de passe est stocké en **bcrypt** (toujours 60 caractères, format `$2b$12$...`)
- Le rôle **`ti`** a les mêmes droits que **`admin`** plus l'accès au module Connexions
- À la création de la base, **2 comptes seed** sont insérés automatiquement par l'app (admin@... et ti@...) — voir `server.py` `on_startup`

---

## 2️⃣ `AuditLog` — Historique des modifications

```sql
USE [CardAvo];
GO

CREATE TABLE [dbo].[AuditLog](
    [id]         [uniqueidentifier] NOT NULL,
    [avocat_id]  [uniqueidentifier] NOT NULL,                    -- référence Avocats.id (lien logique)
    [action]     [varchar](40)      NOT NULL,                    -- voir liste ci-dessous
    [user_email] [varchar](200)     NOT NULL,                    -- email de l'auteur
    [summary]    [nvarchar](500)    NULL,                        -- résumé lisible en français
    [timestamp]  [datetime2](7)     NOT NULL CONSTRAINT [DF_AuditLog_timestamp] DEFAULT (sysutcdatetime()),
 CONSTRAINT [PK_AuditLog] PRIMARY KEY CLUSTERED
(
    [id] ASC
) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY];
GO

CREATE NONCLUSTERED INDEX [IX_AuditLog_avocat_ts]
    ON [dbo].[AuditLog]([avocat_id] ASC, [timestamp] DESC)
    WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];
GO
```

### Liste exhaustive des `action` possibles
| Action | Déclencheur |
|--------|-------------|
| `create` | Création d'une nouvelle fiche avocat |
| `update` | Modification d'un champ d'identification |
| `delete` | Suppression d'une fiche avocat |
| `adresse_create` / `adresse_update` / `adresse_delete` | CRUD adresses |
| `mega_update` / `mega_delete` | Modification du profil Méga |
| `inhab_create` / `inhab_update` / `inhab_delete` | CRUD périodes d'inhabilité |
| `web_password_set` / `web_password_clear` | Mot de passe extranet |

### Exemple de ligne
```
id          : 4a8c1f3e-...
avocat_id   : e8428eca-b482-42bc-abf2-6d64a548da00
action      : update
user_email  : admin@gestioncardex.qc
summary     : Modification : nom, prenom
timestamp   : 2026-05-08 17:03:42.123
```

---

## 3️⃣ `Connexions` — Catalogue des connexions BDD

```sql
USE [CardAvo];
GO

CREATE TABLE [dbo].[Connexions](
    [id]           [uniqueidentifier] NOT NULL,
    [name]         [varchar](100)     NOT NULL,                  -- nom affiché, unique
    [type]         [varchar](20)      NOT NULL,                  -- mongodb / sqlserver / sqlite
    [server]       [varchar](200)     NOT NULL,                  -- hostname ou chemin
    [port]         [int]              NULL,
    [user]         [varchar](100)     NULL,
    [database]     [varchar](100)     NULL,
    [description]  [nvarchar](500)    NULL,
    [password_enc] [varchar](500)     NULL,                      -- chiffré AES-128 (Fernet)
    [is_primary]   [bit]              NOT NULL CONSTRAINT [DF_Connexions_is_primary] DEFAULT (0),
    [created_at]   [datetime2](7)     NOT NULL CONSTRAINT [DF_Connexions_created_at] DEFAULT (sysutcdatetime()),
    [updated_at]   [datetime2](7)     NOT NULL CONSTRAINT [DF_Connexions_updated_at] DEFAULT (sysutcdatetime()),
 CONSTRAINT [PK_Connexions] PRIMARY KEY CLUSTERED
(
    [id] ASC
) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UX_Connexions_name] UNIQUE NONCLUSTERED
(
    [name] ASC
) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY];
GO

ALTER TABLE [dbo].[Connexions]
    ADD CONSTRAINT [CK_Connexions_type] CHECK ([type] IN ('mongodb','sqlserver','sqlite'));
GO
```

### Notes de sécurité
- Le champ `password_enc` est **chiffré côté application** avec une clé Fernet AES-128
  - Clé stockée dans la variable d'environnement `CONNEXIONS_FERNET_KEY` (jamais en BDD ni dans le code)
  - À la mise en production, **générer une nouvelle clé** :
    ```bash
    python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    ```
  - Si la clé change, **les mots de passe stockés deviennent illisibles** — il faudra les ressaisir
- La connexion `is_primary = 1` est en **lecture seule** (seule la description peut être modifiée)
- À l'initialisation, l'app insère 4 lignes seed :
  - `MongoDB principal (en service)` (is_primary=1)
  - `sCardAvo (SQLite local)`, `sStaticPc (SQLite local)`, `sArt52 (SQLite local)`

---

## 🛠️ Script de création complet (à copier-coller dans SSMS)

```sql
USE [CardAvo];
GO

-- ===== Table 1 : AppUsers =====
IF OBJECT_ID('[dbo].[AppUsers]', 'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[AppUsers](
        [id]            [uniqueidentifier] NOT NULL,
        [email]         [varchar](200)     NOT NULL,
        [password_hash] [varchar](100)     NOT NULL,
        [name]          [varchar](200)     NULL,
        [role]          [varchar](20)      NOT NULL,
        [created_at]    [datetime2](7)     NOT NULL DEFAULT (sysutcdatetime()),
        CONSTRAINT [PK_AppUsers] PRIMARY KEY CLUSTERED ([id]),
        CONSTRAINT [UX_AppUsers_email] UNIQUE NONCLUSTERED ([email]),
        CONSTRAINT [CK_AppUsers_role] CHECK ([role] IN ('admin','ti','editeur','lecteur'))
    );
END
GO

-- ===== Table 2 : AuditLog =====
IF OBJECT_ID('[dbo].[AuditLog]', 'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[AuditLog](
        [id]         [uniqueidentifier] NOT NULL,
        [avocat_id]  [uniqueidentifier] NOT NULL,
        [action]     [varchar](40)      NOT NULL,
        [user_email] [varchar](200)     NOT NULL,
        [summary]    [nvarchar](500)    NULL,
        [timestamp]  [datetime2](7)     NOT NULL DEFAULT (sysutcdatetime()),
        CONSTRAINT [PK_AuditLog] PRIMARY KEY CLUSTERED ([id])
    );
    CREATE NONCLUSTERED INDEX [IX_AuditLog_avocat_ts]
        ON [dbo].[AuditLog]([avocat_id] ASC, [timestamp] DESC);
END
GO

-- ===== Table 3 : Connexions =====
IF OBJECT_ID('[dbo].[Connexions]', 'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[Connexions](
        [id]           [uniqueidentifier] NOT NULL,
        [name]         [varchar](100)     NOT NULL,
        [type]         [varchar](20)      NOT NULL,
        [server]       [varchar](200)     NOT NULL,
        [port]         [int]              NULL,
        [user]         [varchar](100)     NULL,
        [database]     [varchar](100)     NULL,
        [description]  [nvarchar](500)    NULL,
        [password_enc] [varchar](500)     NULL,
        [is_primary]   [bit]              NOT NULL DEFAULT (0),
        [created_at]   [datetime2](7)     NOT NULL DEFAULT (sysutcdatetime()),
        [updated_at]   [datetime2](7)     NOT NULL DEFAULT (sysutcdatetime()),
        CONSTRAINT [PK_Connexions] PRIMARY KEY CLUSTERED ([id]),
        CONSTRAINT [UX_Connexions_name] UNIQUE NONCLUSTERED ([name]),
        CONSTRAINT [CK_Connexions_type] CHECK ([type] IN ('mongodb','sqlserver','sqlite'))
    );
END
GO

PRINT 'Tables AppUsers, AuditLog, Connexions créées (ou déjà présentes).';
```

---

## ✅ Vérification après exécution

```sql
SELECT
    t.name AS [Table],
    p.rows AS [Lignes]
FROM sys.tables t
JOIN sys.partitions p ON p.object_id = t.object_id AND p.index_id IN (0, 1)
WHERE t.name IN ('AppUsers', 'AuditLog', 'Connexions')
ORDER BY t.name;
```

Sortie attendue à l'installation initiale :
```
Table        Lignes
AppUsers     0
AuditLog     0
Connexions   0
```
