# Guide de déploiement en production — GestionCardex

Ce document explique comment passer de l'environnement de développement (Emergent, SQLite) à votre serveur de production (SQL Server, 3 bases : CardAvo, StaticPc, Art52).

---

## 🎯 Vue d'ensemble

| Élément | Dev (Emergent) | Prod (votre serveur) |
|---------|----------------|-----------------------|
| Code Python | identique | identique |
| Code React | identique | identique |
| BDD CardAvo | `sqlite_dbs/CardAvo.db` | Base SQL Server `CardAvo` sur `csj-sql-test` |
| BDD StaticPc | `sqlite_dbs/StaticPc.db` | Base SQL Server `StaticPc` sur `csj-sql-test` |
| BDD Art52 | `sqlite_dbs/Art52.db` | Base SQL Server `Art52` sur `csj-sql-test` |
| Différence | rien dans le code, **uniquement** `/app/backend/.env` |

---

## 📋 Étape 1 — Préparer le serveur SQL Server

### 1.1 — Compte applicatif

Sur votre SQL Server (via SSMS), créez **un seul compte** qui aura accès aux 3 bases.

```sql
-- Login dédié à l'application (une seule fois)
CREATE LOGIN gestioncardex_app WITH PASSWORD = 'ChoisirUnMotDePasseFort!2026';
GO

-- Accès en lecture+écriture sur les 3 bases
USE [CardAvo];
CREATE USER gestioncardex_app FOR LOGIN gestioncardex_app;
ALTER ROLE db_datareader ADD MEMBER gestioncardex_app;
ALTER ROLE db_datawriter ADD MEMBER gestioncardex_app;
GO

USE [StaticPc];
CREATE USER gestioncardex_app FOR LOGIN gestioncardex_app;
ALTER ROLE db_datareader ADD MEMBER gestioncardex_app;
ALTER ROLE db_datawriter ADD MEMBER gestioncardex_app;
GO

USE [Art52];
CREATE USER gestioncardex_app FOR LOGIN gestioncardex_app;
ALTER ROLE db_datareader ADD MEMBER gestioncardex_app;
ALTER ROLE db_datawriter ADD MEMBER gestioncardex_app;
GO
```

### 1.2 — Créer les 4 tables ajoutées par l'app

Dans la base **`CardAvo`** uniquement, exécutez le script T-SQL du fichier **`/app/memory/TABLES_AJOUTEES_APP.md`**. Il crée :

- `AppUsers` (comptes Admin / TI / Éditeur / Lecteur)
- `AuditLog` (historique des modifications avec pagination)
- `Connexions` (catalogue des BDD géré par le TI)
- `Mandats` (Registre 97 / 98)

### 1.3 — Vérifier la connectivité

Depuis votre serveur d'application, vérifiez que vous joignez bien le SQL Server :

```bash
telnet csj-sql-test 1433
# ou
nc -vz csj-sql-test 1433
```

---

## 📋 Étape 2 — Déployer le code sur votre serveur

### 2.1 — Cloner le dépôt

Sur Emergent : **"Save to GitHub"** dans la barre du chat → vous obtenez un dépôt Git avec tout le code.

Sur votre serveur d'application :
```bash
git clone <votre-dépôt-github> /app
cd /app
```

### 2.2 — Installer les dépendances Python

```bash
cd /app/backend
pip install -r requirements.txt

# Ajouter le pilote SQL Server (UNIQUEMENT en prod, pas inclus par défaut)
pip install pymssql
```

### 2.3 — Construire le frontend

```bash
cd /app/frontend
yarn install
yarn build
# Sert `build/` via nginx ou similaire
```

---

## 📋 Étape 3 — Configurer `/app/backend/.env`

C'est la **seule** étape qui diffère vraiment du dev. Créez `/app/backend/.env` avec ce contenu :

```env
# ============================================================
#           CONNEXIONS SQL SERVER (3 bases sur 1 serveur)
# ============================================================
# Mode "champs séparés" — comme dans SSMS
SQLSERVER_HOST=csj-sql-test
SQLSERVER_PORT=1433
SQLSERVER_USER=gestioncardex_app
SQLSERVER_PASSWORD=ChoisirUnMotDePasseFort!2026

# Les 3 catalogues sur ce même serveur
DB_CARDAVO=CardAvo
DB_STATICPC=StaticPc
DB_ART52=Art52

# ============================================================
#                     AUTHENTIFICATION
# ============================================================
# Générer avec : python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET=changer_par_un_secret_de_64_caracteres_genere_aleatoirement

ADMIN_EMAIL=admin@votreorganisation.qc
ADMIN_PASSWORD=ChangerImmediatementApresPremiereConnexion!

TI_EMAIL=ti@votreorganisation.qc
TI_PASSWORD=ChangerImmediatementApresPremiereConnexion!

# ============================================================
#               CHIFFREMENT DES CONNEXIONS BDD
# ============================================================
# Générer avec : python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
CONNEXIONS_FERNET_KEY=changer_par_une_cle_Fernet_generee

# ============================================================
#                  COOKIES & FRONTEND
# ============================================================
# En HTTPS uniquement (mettre à false si HTTP local de test)
COOKIE_SECURE=true
FRONTEND_URL=https://gestioncardex.votreorganisation.qc

# ============================================================
#  (Variables MONGO_URL / DB_NAME : NON utilisées par l'app
#   mais présentes pour compatibilité environnement Emergent)
# ============================================================
MONGO_URL=mongodb://localhost:27017
DB_NAME=unused
```

### 🔐 Génération des secrets (à faire sur votre serveur)

```bash
# JWT_SECRET
python3 -c "import secrets; print(secrets.token_hex(32))"

# CONNEXIONS_FERNET_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

⚠️ Ne **JAMAIS** réutiliser les secrets du dev (Emergent) en prod.

---

## 📋 Étape 4 — Configurer `/app/frontend/.env`

```env
REACT_APP_BACKEND_URL=https://gestioncardex.votreorganisation.qc
```

(Si frontend et backend sur le même domaine derrière un reverse proxy comme nginx.)

---

## 📋 Étape 5 — Démarrer

```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

### Que se passe-t-il au premier démarrage ?

1. SQLAlchemy se connecte à `csj-sql-test` avec vos identifiants.
2. `Base.metadata.create_all()` vérifie que les 4 tables app existent (idempotent).
3. Si les comptes `admin@...` et `ti@...` n'existent pas dans `AppUsers`, ils sont créés avec les mots de passe `ADMIN_PASSWORD` / `TI_PASSWORD`.
4. Les comptes Éditeur et Lecteur sont créés s'ils n'existent pas.
5. La table `Connexions` reçoit 3 entrées de référence (CardAvo / StaticPc / Art52) que le TI pourra adapter.

---

## ✅ Vérification post-déploiement

### Test 1 — Endpoint de santé

```bash
curl https://gestioncardex.votreorganisation.qc/api/
# Réponse attendue : {"app":"GestionCardex","version":"2.1.0","backend":"SQLAlchemy/SQLite"}
```

> ℹ️ Le mot "SQLite" dans la réponse est juste un libellé interne — l'app est bien sur SQL Server si votre `.env` est correct.

### Test 2 — Login admin

```bash
curl -X POST https://gestioncardex.votreorganisation.qc/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@votreorganisation.qc","password":"VotreMdpAdmin"}'
```

### Test 3 — Confirmer que c'est bien SQL Server

Connectez-vous comme TI → Page "Connexions" → Cliquer "Tester" sur CardAvo → doit afficher "SQL Server OK".

### Test 4 — Diagnostic des 3 BDD

Un endpoint interne pourrait être ajouté pour confirmer (à demander). En attendant, dans les logs backend :

```bash
tail -f /var/log/supervisor/backend.err.log
```

Toute requête SQL devrait passer sur `csj-sql-test`.

---

## 🔄 Mise à jour de l'application en prod

```bash
cd /app
git pull
cd backend && pip install -r requirements.txt
cd ../frontend && yarn install && yarn build
sudo supervisorctl restart backend frontend
```

⚠️ Faites **toujours un backup SQL Server avant** d'appliquer une mise à jour qui touche au schéma.

---

## 🆘 Rollback

Si une mise à jour casse quelque chose :
```bash
cd /app && git reset --hard <commit_precedent>
cd backend && pip install -r requirements.txt
cd ../frontend && yarn install && yarn build
sudo supervisorctl restart backend frontend
```

Et restaurer le backup SQL Server si le schéma a été modifié.

---

## 📞 Pré-prod (recommandé avant la vraie prod)

1. Cloner votre base SQL Server sur un serveur de test : `csj-sql-test-preprod`
2. Déployer l'application avec `SQLSERVER_HOST=csj-sql-test-preprod`
3. Tester pendant quelques jours avec des utilisateurs internes
4. Une fois validé, repointer `SQLSERVER_HOST` vers `csj-sql-test` (prod)

---

## 📚 Récapitulatif des fichiers de référence

| Fichier | Rôle |
|---------|------|
| `/app/backend/database.py` | Détecte automatiquement le mode (SQLite dev / SQL Server prod) |
| `/app/backend/.env` | **Le seul fichier à adapter** entre dev et prod |
| `/app/memory/SCHEMAS_SQL_LEGACY.md` | DDL des 22 tables legacy SQL Server |
| `/app/memory/TABLES_AJOUTEES_APP.md` | Script T-SQL des 4 tables ajoutées par l'app (à exécuter dans CardAvo) |
| `/app/memory/test_credentials.md` | Comptes seedés au premier démarrage |

---

**En une ligne :** Vous mettez `SQLSERVER_HOST=csj-sql-test` + user/password + nom des 3 bases dans `.env`, vous redémarrez, c'est fini. Aucune ligne de code Python à toucher.
