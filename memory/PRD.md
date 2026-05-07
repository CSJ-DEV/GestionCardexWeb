# GestionCardex – Web Edition

## Original problem statement
"Bonjour, on veut que l'application GestionCardex qui est developpé en visual basic la rendre en web, les bases de données sont sql server, quelle language de programmation c'est mieux pour toi le faire?"

## Stack chosen
React 19 + FastAPI + MongoDB (replaces VB6/SQL Server). Internal app.

## User personas
- **Administrateur du barreau / personnel légal (Québec)** : gère le registre des avocats (création, modification, recherche, statut actif/inactif, méga, NEQ, NAS, adresse).

## Core requirements (frozen)
- Langue : Français (fr-CA) uniquement
- Auth JWT email/password (cookies httpOnly)
- Module Gestion d'avocats : CRUD complet + recherche + filtres + pagination
- Style ERP moderne / professionnel (Swiss & High-Contrast – Cabinet Grotesk + IBM Plex Sans)

## Implemented (2026-05-07)
- Backend FastAPI (`/app/backend/server.py`) : auth (login/logout/me), avocats CRUD, /avocats/stats, seed admin
- Mongo collections : `users`, `avocats` (indexes uniques sur email et code)
- Frontend React : routes `/login`, `/`, `/avocats` ; AuthContext ; ProtectedRoute ; Layout (sidebar + topbar)
- Pages : Login (split visual), Dashboard (4 stat cards + activité 30j), AvocatsList (table + recherche + filter statut + pagination + add/edit/delete via Sheet)
- Composant `AvocatSheet` (formulaire complet : identité, adresse, statuts, commentaires)
- Tests E2E : 10/10 backend pytest, frontend e2e Playwright = 100% pass

## Backlog (priorisé)
- **P1** Import des données existantes depuis fichiers .sql (sArt52 / sCardAvo / sStaticPc) vers MongoDB
- **P1** Module **Fournisseurs** (table `Fournisseurs` du SQL d'origine)
- **P1** Module **Adresses** multiples par avocat (table `Addresses` originale supportait `noseq`)
- **P2** Module **Rev27** (déclarations / contributions annuelles `tRev27_Contrib`)
- **P2** Module **Journal d'appels FviLog** (suivi des appels par avocat)
- **P2** Audit log `usermodif` / historique des modifications
- **P2** Export Excel/CSV des avocats
- **P3** Multi-utilisateurs avec rôles (admin / lecture seule)
- **P3** Brute-force lockout sur /auth/login
- **P3** Migration `@app.on_event` → lifespan context manager
- **P3** Cookie `secure=True` piloté par env var `COOKIE_SECURE` pour la prod

## Test credentials
Voir `/app/memory/test_credentials.md`
- admin@gestioncardex.qc / Admin2026!

## Phase 1a — Backend (2026-05-07)
**Implémenté** :
- Modèle Avocat enrichi : `type_code` (A/N/P), `attente`, `annee_barreau`, `taxes`
- `GET /api/avocats/next-code?type=A` → auto-génération séquentielle (A0001, P0001, N0001 — Jordan supprimé)
- Validation NAS **Luhn** côté serveur (rejet 422 si invalide) — port direct du `funcValidNoAssSoc` VB
- Sous-ressource Adresses : `/api/avocats/{id}/adresses` (GET/POST/PUT/DELETE) avec gestion logique « courante »
- Suppression d'avocat → cascade des adresses associées
- Modèle User étendu avec rôles : `admin` / `editeur` / `lecteur`
- CRUD Utilisateurs `/api/users` (admin uniquement) avec protection auto-suppression
- Helper `require_role(...)` pour protéger les routes par rôle
- Routes Avocats protégées : create/update = admin+editeur, delete = admin uniquement

**Phase 1b à venir** : Frontend tabbed UI (5 onglets) + page Utilisateurs + sidebar dynamique selon rôle + mode lecture seule.

## Phase 2a — Backend Méga + Inhabilité (2026-05-07)
**Implémenté** :
- Modèle `InfoMega` : sectbar, districthab, francais/anglais (bool), autres, experience (int), details, art486/672/684 (bool), commentaire, dateinsc, districts (list[int]), tous_districts
- Modèle `Inhabilite` : datedeb, datefin, comm
- Endpoints Méga (1 par avocat — upsert) :
  - `GET /api/avocats/{id}/mega`
  - `PUT /api/avocats/{id}/mega` (admin/editeur, met automatiquement avocats.mega=true)
  - `DELETE /api/avocats/{id}/mega` (met avocats.mega=false)
- Endpoints Inhabilité (sous-collection) :
  - `GET /api/avocats/{id}/inhabilites`
  - `POST /api/avocats/{id}/inhabilites` (admin/editeur)
  - `PUT /api/avocats/{id}/inhabilites/{inhab_id}`
  - `DELETE /api/avocats/{id}/inhabilites/{inhab_id}`
- Suppression d'avocat → cascade des collections `avocat_mega` + `avocat_inhab`
- Tous testés via curl ✅

**Phase 2b à venir** : Onglets frontend Méga + Inhabilité dans `AvocatSheet`.

## Rapports Crystal reçus (à traiter en Phase 3)
- `Registre97.rpt` (P0)
- `ListeDetBar.rpt`, `ListeDetDist.rpt`, `ListeDetReg.rpt`, `ListeSom.rpt`
⚠️ Format binaire SAP non parsable directement — requis : PDF d'exemple OU liste colonnes/groupes/totaux OU requêtes SQL.

## Phase 2b — Frontend Méga + Inhabilité (2026-05-07)
**Implémenté** :
- `AvocatSheet` passe à **4 onglets** : Identification / Adresses / Inhabilité / Méga
- **Onglet Inhabilité** : tableau des périodes (datedeb → datefin), formulaire inline avec date pickers HTML5 (`type="date"`), commentaire, CRUD complet via API `/avocats/{id}/inhabilites`
- **Onglet Méga** :
  - Section barreau, expérience (input number), date inscription
  - Switches Français / Anglais + champ texte « Autres langues »
  - 3 switches Articles 486 / 672 / 684
  - Liste 18 districts du Québec (Montréal, Québec, Laval, etc.) en checkboxes scrollables + switch « Tous » (sélection rapide)
  - Détails + Commentaire (textarea)
  - Bouton « Enregistrer le profil Méga » → PUT upsert
- **Onglets désactivés** tant que l'avocat n'est pas créé (Adresses / Inhabilité / Méga)
- **Mode lecture seule** respecté (`lecteur` voit tout en disabled)
- Lint JS : 0 erreur, webpack compilation : OK

**Captures validées** : login + sidebar dynamique + page Utilisateurs + ouverture du Sheet avec les 4 onglets visibles et activables.

## Phase 3 (à venir)
- Onglet **Web** (codes usager + mots de passe — `frmMotPasse` du VB)
- **Rapports PDF** (Registre97 + ListeDetBar + ListeDetDist + ListeDetReg + ListeSom) — *requiert PDF d'exemple ou descriptions de colonnes pour chaque rapport*
