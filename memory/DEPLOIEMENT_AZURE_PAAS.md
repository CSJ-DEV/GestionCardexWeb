# 🚀 Déploiement GestionCardex sur Azure (PaaS)

Guide pas-à-pas pour déployer **GestionCardex** sur Azure avec :
- **Frontend React** → **Azure Static Web Apps** (gratuit)
- **Backend FastAPI** → **Azure App Service Linux** (B1, ~20 $CAD/mois)
- **Base de données** → **SQL Server existant** sur VM Azure `CSJ-SQL-TEST`
- **CI/CD** → **GitHub Actions** (déploiement automatique à chaque `git push`)

> **Public visé** : 5-10 utilisateurs internes Cour du Québec.
> **Architecture** : VNet integration pour atteindre `CSJ-SQL-TEST` en privé.

---

## 📋 Prérequis

- ✅ Compte Azure avec un Resource Group existant (notez son nom)
- ✅ Repo GitHub avec votre code (`Save to GitHub` depuis Emergent OU push manuel)
- ✅ Accès admin à la VM `CSJ-SQL-TEST` (pour ouvrir le pare-feu si nécessaire)
- ✅ Azure CLI installé localement (facultatif, on peut tout faire dans le portail)

---

## 🗺️ Vue d'ensemble — 7 étapes

1. **Créer l'App Service Plan + l'App Service** (backend Python)
2. **Configurer VNet Integration** pour atteindre `CSJ-SQL-TEST`
3. **Créer la Static Web App** (frontend React)
4. **Configurer les variables d'environnement** (`.env` Azure)
5. **Ajouter les secrets GitHub** (publish profile + token)
6. **Pousser le code** → déploiement automatique
7. **Tester + ouvrir aux utilisateurs**

---

## 🛠️ Étape 1 — Créer l'App Service (backend Python)

### 1.1. Dans le portail Azure
1. Allez sur **votre Resource Group existant**
2. Cliquez **Créer → Web App**
3. Renseignez :
   - **Subscription** : votre abonnement
   - **Resource Group** : votre RG existant
   - **Name** : `cardex-api` (sera l'URL : `cardex-api.azurewebsites.net`)
   - **Publish** : `Code`
   - **Runtime stack** : `Python 3.12`
   - **OS** : `Linux`
   - **Region** : **même région que CSJ-SQL-TEST** ⚠️
   - **Plan** : créez un nouveau plan
     - **Name** : `cardex-plan`
     - **SKU** : `B1` (Basic, ~20 $/mois)
4. **Review + Create** → **Create**
5. ⏳ Attendez ~2 min

### 1.2. Configurer le startup command
1. Dans l'App Service → **Configuration → General settings**
2. **Startup Command** :
   ```bash
   gunicorn -w 2 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8000 --timeout 120
   ```
3. **Save**

### 1.3. Activer "Always On"
Toujours dans **Configuration → General settings** :
- **Always On** : `On` (sinon le backend s'endort après 20 min)
- **HTTP version** : `2.0`
- **HTTPS Only** : `On`
- **Save**

---

## 🌐 Étape 2 — VNet Integration (accès privé à SQL Server)

### 2.1. Pré-requis VNet
La VM `CSJ-SQL-TEST` doit être dans un **Virtual Network**. Si oui (cas standard) :
1. App Service → **Networking → VNet integration**
2. Cliquez **Add VNet**
3. Sélectionnez le **VNet de CSJ-SQL-TEST**
4. Choisissez un **subnet dédié** (créez-en un nouveau : `snet-appservice`, /28 suffit)
5. **OK**

### 2.2. Ouvrir le pare-feu SQL sur CSJ-SQL-TEST
Sur la VM `CSJ-SQL-TEST` :
1. **Windows Defender Firewall → Advanced Settings**
2. **Inbound Rules → New Rule**
3. **Port** → TCP **1433** → **Allow**
4. **Scope** : limitez à la plage IP du subnet App Service (ex : `10.0.2.0/28`) pour la sécurité

### 2.3. Vérifier que SQL accepte les connexions TCP/IP
Via **SQL Server Configuration Manager** sur la VM SQL :
- **SQL Server Network Configuration → Protocols for MSSQLSERVER**
- **TCP/IP** : **Enabled**
- **TCP Port** : `1433`
- Redémarrer le service SQL Server si modifié

---

## 🎨 Étape 3 — Créer la Static Web App (frontend React)

1. Resource Group → **Créer → Static Web App**
2. Renseignez :
   - **Name** : `cardex-web`
   - **Plan type** : `Free` (largement suffisant pour 5-10 users)
   - **Region** : la plus proche
   - **Source** : `GitHub`
   - **Sign in with GitHub** → autorisez
   - **Organization / Repository / Branch** : sélectionnez votre repo et `main`
   - **Build presets** : `React`
   - **App location** : `/frontend`
   - **Output location** : `build`
3. **Review + Create**

📌 Azure va automatiquement créer un workflow GitHub Actions et faire le 1er déploiement (~3 min).

> ⚠️ **Important** : ce workflow auto-généré est plus complet que celui que j'ai créé dans `.github/workflows/deploy-frontend.yml`. Choisissez **soit** celui d'Azure **soit** le mien, pas les deux. Plus simple : gardez celui d'Azure et supprimez le mien.

---

## 🔐 Étape 4 — Variables d'environnement

### 4.1. Backend (App Service)

App Service `cardex-api` → **Configuration → Application settings** → **+ New application setting**.

Ajoutez ces variables une par une :

| Nom | Valeur | Notes |
|---|---|---|
| `ENVIRONMENT` | `production` | |
| `SQLSERVER_HOST` | `csj-sql-test.<votre.domaine.interne>` | nom DNS ou IP privée de la VM SQL |
| `SQLSERVER_PORT` | `1433` | |
| `SQLSERVER_USER` | `DajWeb` | |
| `SQLSERVER_PASSWORD` | `ExTest` | ou un mot de passe plus fort |
| `DB_CARDAVO` | `CardAvo` | |
| `DB_STATICPC` | `StaticPc` | |
| `DB_ART52` | `Art52` | |
| `SQLSERVER_ODBC_DRIVER` | `ODBC Driver 18 for SQL Server` | App Service Linux |
| `JWT_SECRET` | (générez 32+ caractères aléatoires) | **CRITIQUE — à changer** |
| `CONNEXIONS_FERNET_KEY` | (la valeur actuelle ou générez une nouvelle) | |
| `COOKIE_SECURE` | `true` | App Service force HTTPS |
| `FRONTEND_URL` | `https://cardex-web.azurestaticapps.net` | URL de votre Static Web App (cf. étape 3) |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` | force `pip install` à chaque déploiement |

> 💡 **Tip** : Pour générer un JWT_SECRET sécurisé, dans PowerShell : `[System.Web.Security.Membership]::GeneratePassword(48,0)` ou en ligne sur [randomkeygen.com](https://randomkeygen.com).

**Save** → l'app redémarre automatiquement.

### 4.2. Frontend (Static Web App)

Static Web App `cardex-web` → **Configuration**.

| Nom | Valeur |
|---|---|
| `REACT_APP_BACKEND_URL` | `https://cardex-api.azurewebsites.net` |

**Save** → relancez le workflow GitHub Actions pour reprendre cette variable.

---

## 🔑 Étape 5 — Configurer les secrets GitHub

### 5.1. Publish Profile pour le backend

1. App Service `cardex-api` → **Get publish profile** (bouton en haut)
2. Téléchargez le fichier `.PublishSettings`
3. Ouvrez-le dans Notepad, copiez **TOUT le contenu**
4. Sur GitHub → votre repo → **Settings → Secrets and variables → Actions**
5. **New repository secret** :
   - Name : `AZURE_WEBAPP_PUBLISH_PROFILE`
   - Value : collez le XML
6. Save

### 5.2. Token pour la Static Web App

Le token a déjà été créé automatiquement par Azure à l'étape 3 sous le nom `AZURE_STATIC_WEB_APPS_API_TOKEN_<XXX>`.

Si vous utilisez **mon workflow** au lieu de celui d'Azure, ajoutez aussi :
- `REACT_APP_BACKEND_URL` = `https://cardex-api.azurewebsites.net`

---

## 🚀 Étape 6 — Déclencher le déploiement

### 6.1. Commit + push
```bash
git add .
git commit -m "Configure Azure deployment"
git push origin main
```

### 6.2. Suivi
- **Backend** : GitHub → **Actions** → workflow "Deploy Backend to Azure App Service" (3-5 min)
- **Frontend** : GitHub → **Actions** → workflow Static Web App (2-3 min)

### 6.3. Logs en direct
- **Backend** : App Service `cardex-api` → **Log stream** (toutes les requêtes en temps réel)
- **Frontend** : Static Web App `cardex-web` → **Functions → Logs** (si applicable)

---

## ✅ Étape 7 — Tester

### 7.1. Backend
Ouvrez : `https://cardex-api.azurewebsites.net/api/`

Vous devez voir :
```json
{"app":"GestionCardex","version":"2.1.0","backend":"SQLAlchemy/SQLite"}
```

> Si "Application Error" : allez dans Log stream pour voir l'erreur.

### 7.2. Frontend
Ouvrez : `https://cardex-web.azurestaticapps.net`

Connectez-vous avec :
- `admin@gestioncardex.qc` / `Admin2026!` (ou votre mot de passe modifié)

---

## 🛡️ Sécurité — à ajouter plus tard

| Action | Priorité | Comment |
|---|---|---|
| **Restriction d'IP** sur le backend | 🔴 P0 | App Service → Networking → Access Restriction → autoriser uniquement votre plage IP Cour du Québec + l'IP sortante de la Static Web App |
| **Custom domain** (`cardex.cour.gouv.qc.ca`) | 🟠 P1 | Static Web App → Custom Domains |
| **Microsoft Entra ID (SSO)** | 🟠 P1 | App Service → Authentication → Microsoft → utilisateurs Cour du Québec |
| **Secrets dans Key Vault** | 🟡 P2 | Stockez `SQLSERVER_PASSWORD` et `JWT_SECRET` dans Azure Key Vault et référencez-les via `@Microsoft.KeyVault(...)` |
| **Application Insights** | 🟡 P2 | Monitoring + alertes par email automatiques |

---

## 🐛 Troubleshooting

### Backend renvoie 500 ou ne démarre pas
1. **Log stream** dans le portail Azure → cherchez le `Traceback`
2. Causes fréquentes :
   - `pyodbc` non compilable → notre `startup.sh` installe `msodbcsql18` mais Azure utilise un *runtime image* qui peut ne pas le permettre. Solution : utilisez **`pymssql`** (qui marche out-of-the-box sur Azure Linux) en supprimant `SQLSERVER_ODBC_DRIVER` des variables d'env.
   - Connexion SQL refusée → vérifiez VNet Integration + pare-feu sur la VM SQL.

### Le frontend ne joint pas le backend (CORS)
- Vérifiez que `FRONTEND_URL` côté backend pointe bien sur `https://cardex-web.azurestaticapps.net`
- Vérifiez que `REACT_APP_BACKEND_URL` côté frontend pointe bien sur `https://cardex-api.azurewebsites.net`

### Cookies non envoyés (login passe mais /auth/me retourne 401)
- `COOKIE_SECURE=true` est obligatoire sur Azure (HTTPS)
- Si Static Web App et App Service sont sur des sous-domaines différents (`*.azurestaticapps.net` vs `*.azurewebsites.net`) → on est en cross-site → les cookies sont bloqués par Chrome. **Solution** :
  - Soit utiliser un **custom domain** commun (ex: `cardex.cour.gouv.qc.ca` et `api.cardex.cour.gouv.qc.ca`)
  - Soit basculer vers l'auth par **header Authorization** (modif côté frontend)
  - Soit utiliser le **proxy** intégré Static Web Apps : route `/api/*` → backend (notre code y est compatible)

> 💡 **L'option Proxy Static Web Apps est la plus simple**. Je peux préparer le fichier `staticwebapp.config.json` pour cela à votre demande.

---

## 📊 Récap des coûts mensuels

| Service | Plan | Coût CAD/mois |
|---|---|---|
| App Service Plan | B1 | ~20 $ |
| Static Web App | Free | 0 $ |
| Bande passante interne (VNet) | inclus | 0 $ |
| Application Insights (optionnel) | Free 5 Go | 0 $ |
| **Total** | | **~20 $** |

La VM `CSJ-SQL-TEST` reste à son coût actuel (vous l'aviez déjà).

---

## 🆘 Besoin d'aide ?

Si une étape échoue, partagez :
1. **Le log précis** (App Service Log stream ou GitHub Actions)
2. **Le numéro d'étape** où ça plante

Je vous débloque dans la foulée. 🚀
