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

## Phase 3a — Onglet Web (2026-05-07)
**Implémenté** :
- Champ `codeusager` ajouté au modèle Avocat (rétrocompatible)
- Endpoint `PUT /api/avocats/{id}/web-password` : hash bcrypt + min 6 car. (admin/editeur)
- Endpoint `DELETE /api/avocats/{id}/web-password` : reset
- 5e onglet **Web** dans `AvocatSheet` :
  - Champ Code usager + Ville référence
  - 2 switches Facturation web / Confirmation web
  - Section mot de passe web (Définir / Effacer) — jamais affiché en clair
  - Bouton « Enregistrer code usager + options » (réutilise handleSubmit identification)
- Tests curl ✅ (set ok / rejet < 6 car.)
- Lint frontend ✅

**Phase 3b restante** : Rapports PDF (Registre97 + 4 listes) — bloqué tant que je n'ai pas de PDF d'exemple ou descriptions de colonnes pour chaque .rpt.

## Phase 3b — Rapports PDF (PLANIFIÉ — non implémenté)
**5 PDF d'exemple reçus** : Registre97, ListeDetBar, ListeDetDist, ListeDetReg, ListeSom

### Découverte critique
Registre97 nécessite une **entité Mandats** (table `tMandats` SQL) absente du modèle actuel.
Colonnes : Nom avocat, Nom requérant, Date ordonnance, Date émission, # Mandat
Groupé par : Avocats Pratique Privée / Permanent
Sections : Article 486.3, 486.7 (et probablement 672, 684 selon Méga)

### Plan prochaine session
1. **P0** Module Mandats : modèle + CRUD `/api/mandats` (avocat_id, requerant, article, dates, numero, groupe)
2. **P0** Endpoint PDF ReportLab `/api/rapports/registre97?date_debut=&date_fin=`
3. **P1** 4 autres endpoints PDF (ListeDetBar/Dist/Reg, ListeSom) — analyser leur structure (PDF en main)
4. **P1** Page frontend `/rapports` avec sélecteur + filtres dates + bouton « Générer PDF »
5. **P2** Installer reportlab : `pip install reportlab && pip freeze > requirements.txt`

### URLs PDF d'exemple (pour référence)
- Registre97.pdf, ListeDetBar.pdf, ListeDetDist.pdf, ListeDetReg.pdf, ListeSom.pdf — disponibles via customer-assets.emergentagent.com (job_cardex-migrate)

## Phase 3b — Mandats + Registre97 PDF (2026-05-08)
**Implémenté** :
- **Modèle Mandat** : avocat_id, requerant, article (486.3/486.7/672/684), date_ordonnance, date_emission, numero, groupe (Pratique Privée/Permanent), commentaire
- **CRUD `/api/mandats`** complet (list avec filtres, create, update, delete)
- **PDF Registre97** via ReportLab : `GET /api/rapports/registre97?date_debut=&date_fin=`
  - Reproduit la mise en page : titre Commission, sections Article 486.3 / 486.7, groupes (Pratique Privée/Permanent), tableau bleu, sous-totaux, totaux par article
- **Page `/rapports`** frontend : générateur Registre97 (date début/fin + bouton télécharger) + tableau CRUD des mandats + Sheet de saisie
- **Lien sidebar « Rapports »** (icône FileText) pour tous les rôles
- **Permissions** : create/update mandat = admin/editeur, delete = admin
- Tests curl ✅ : mandat créé, liste OK, PDF généré (2.5 KB, signature %PDF valide)
- `reportlab` ajouté à requirements.txt

**Non implémenté (prochaines itérations)** :
- 4 autres rapports PDF : ListeDetBar, ListeDetDist, ListeDetReg, ListeSom (PDF reçus mais non analysés)
- Registre98 (PDF reçu mais non implémenté)
- Tests E2E par rôles avec testing_agent

## Phase 3c — 5 rapports PDF + Tests E2E (2026-05-08)
**Implémenté** :
- Fonction générique `_build_avocat_list_pdf(title, subtitle, columns, rows_par_groupe)` réutilisée
- 5 endpoints PDF : `/rapports/registre98`, `/liste-det-bar`, `/liste-det-dist`, `/liste-det-reg`, `/liste-som`
- Tous validés via curl ✅ (200 OK, ~2KB chacun, signature %PDF)
- Page Rapports : 5 boutons supplémentaires de téléchargement
- **Backend testing : 27/27 tests passent (100%)** — testing_agent v3 complet

**Bug critique trouvé + fix** :
- `QC_DISTRICTS` dans AvocatSheet.jsx était référencé sans être défini → crash React → tous les onglets bloqués
- Fix : déclaration `const QC_DISTRICTS = [...]` au top du fichier (18 districts du Québec)
- Lint OK après fix

**Notes du testing agent (P3 — backlog)** :
- Migrer `@app.on_event` vers FastAPI `lifespan()`
- Ajouter brute-force lockout sur /auth/login (5 essais)
- Cookie `secure` pilotable via `COOKIE_SECURE` env pour prod


## Phase 4 — Hardening + Bug-fix UX AvocatSheet (2026-05-08 / 2026-02 fork)
**Implémenté** :
- Brute-force lockout sur `/auth/login` (5 essais) + cookie `secure` via `COOKIE_SECURE` env
- **Fix P0 (fork actuel)** : `AvocatSheet` ne se ferme plus à chaque sauvegarde de sous-onglet
  - `AvocatsList.handleSaved({ close, updatedAvocat })` : ferme uniquement si `close=true` ; bascule en mode édition après création (POST → `setEditing(updatedAvocat)`)
  - `saveAdresse`, `saveMega`, `saveInhab` (implicite) : passent `{close:false}` → la fenêtre reste ouverte, fidèle au workflow VB.NET
  - `handleSubmit` (POST/PUT identification) : passe `{updatedAvocat: data}` → après création, les onglets Adresses/Inhab/Méga/Web deviennent activés sans réouvrir la fiche
  - `useEffect` charge maintenant **adresses + inhabilités + profil méga** depuis le backend → pas de perte de données existantes lors de la réouverture
- **Tests** : `iteration_5.json` — 8/8 critères d'acceptation validés (100% frontend)

## Phase 5 — Pixel-perfect PDFs + Refactor AvocatSheet (2026-02 fork, suite)
**Implémenté** :
- **Nouveau module `/app/backend/pdf_reports.py`** (480 lignes) — reproduction fidèle Crystal Reports :
  - Pavé bleu `AIDE JURIDIQUE` en haut-gauche (équivalent du logo balances de l'aide juridique)
  - Titre centré "Commission des services juridiques" + sous-titre rule-specific (article 97/98/83.10)
  - Footer répété sur chaque page : `AAAA/MM/JJ | nom_rapport.rpt | Page X` + filet de séparation
  - `BaseDocTemplate` + `onPage` callback pour chrome persistant
  - Polices Helvetica (équiv. Arial Crystal d'origine)
  - **Registre97** : 4 articles (486.3/486.7/672.5/684), sous-groupes par type avocat (Pratique Privée / Permanents / Notaires), libellés exacts "Sous-total Avocats X    N mandat(s)" + "Total Article X C.cr.    N mandat(s)"
  - **Registre98** : colonnes legacy (Avocat | Mandat | Ordonnance | Date ord. | Date émission | Date fermeture), tri explicite des articles
  - **ListeDetBar/Dist/Reg** : blocs détaillés par avocat (nom + adresse + tél + email + langues + sections + districts) groupés respectivement par section barreau / ville / décennie barreau
  - **ListeSom** : tableau alphabétique compact avec colonnes legacy
  - Suppression du "Total général" qui n'existe pas en legacy
- **Refactor frontend `AvocatSheet.jsx`** : 540 → 232 lignes, split en 5 sous-composants dans `/app/frontend/src/components/avocat/` (`IdentificationTab`, `AdressesTab`, `InhabTab`, `MegaTab`, `WebTab` + `constants.js` partagé)
- **Optimisation `useEffect`** : 2 effets séparés — form-sync sur `[avocat]` (léger), heavy-fetch (adresses/inhab/mega) sur `[avocat?.id]` uniquement → plus de refetches après PUT identification
- **Tests** : `iteration_6.json` — backend 13/13 pytest (100%), frontend sans régression du fix P0

## Phase 6 — Indicateurs dirty + Audit log (2026-02 fork, suite)
**Implémenté** :
- **Frontend P2 — Dirty dots sur les TabsTrigger** : point ambré qui apparaît dès qu'un onglet a des modifications non enregistrées et disparaît automatiquement après sauvegarde. 5 indicateurs : `dirty-ident`, `dirty-adr`, `dirty-inhab`, `dirty-mega`, `dirty-web`. Implémentation via `useState` baselines + `useMemo` + sérialisation stable JSON.
- **Backend P3 — Audit log** : nouvelle collection `audit_log` (index composite `avocat_id + timestamp:-1`), helper `_audit()` best-effort, instrumenté sur 12 actions (create/update/delete avocat, adresse_create/update/delete, mega_update/delete, inhab_create/update/delete, web_password_set/clear). Endpoint `GET /api/avocats/{id}/audit` admin-only.
- **Frontend P3 — Onglet Historique** (`/components/avocat/HistoriqueTab.jsx`) visible uniquement pour `admin`. Affiche chaque entrée avec badge coloré (Modification/Création/Suppression/Méga/Adresse/Inhab/MdP), résumé lisible, date locale `fr-CA`, email utilisateur. La grille des onglets passe à `grid-cols-6` pour admin, `grid-cols-5` sinon.
- **Bug corrigé en cours d'itération** : conversion `useRef → useState` pour les baselines afin que `setBaseline()` invalide les `useMemo` (sans ça le dirty-mega restait visible après save).
- **Tests** : `iteration_7.json` — backend 10/10 pytest (100%), frontend après fix dirty-mega : tous les flags se mettent à jour correctement, test live confirmé.

## Phase 7 — Pagination historique + timestamp BSON natif (2026-02 fork)
**Implémenté** :
- **Backend** — Endpoint `GET /api/avocats/{id}/audit` retourne maintenant `{items, total, page, page_size}` avec `page` (ge=1) et `page_size` (ge=1, le=200, défaut=20). Validation 422 automatique via FastAPI `Query()`.
- **Backend** — Helper `_audit()` stocke maintenant `timestamp` en `datetime` BSON natif. `_audit_to_out()` convertit en ISO string pour la réponse HTTP. Tri/index plus robustes.
- **Backend** — Migration idempotente au startup : convertit les anciens timestamps ISO string → datetime BSON natif (19 entrées converties au déploiement).
- **Frontend** — `HistoriqueTab` adapté : compteur `hist-count`, boutons `hist-prev`/`hist-next` visibles uniquement si `totalPages > 1`, reset page à 1 lors d'un changement d'avocat, clamp défensif si la page courante devient vide (entrées supprimées), `console.warn` sur erreur fetch.
- **Tests** : `iteration_8.json` — **backend 21/21 (100%)**, **frontend 7/7 (100%)**, aucune régression. Mongo direct check confirme : 0 timestamp string restant, 19 datetime BSON.

## Phase 8 — Code avocat généré au save + plein écran (2026-02 fork)
**Implémenté** :
- **Génération du code au save** : le code n'est plus pré-affiché. Format `<A|P|N><5 chiffres>` (ex `A00001`, `P00042`). Le code envoyé par le frontend est ignoré ; le serveur le calcule à partir du dernier code existant pour ce type, avec retry sur `DuplicateKeyError` (5 essais) pour gérer les créations concurrentes — testé avec 5 créations parallèles → 5 codes uniques séquentiels.
- **AvocatCreate.code** est maintenant `Optional[str]`. L'endpoint `GET /next-code` reste exposé comme aperçu indicatif uniquement (utilise le même helper `_generate_avocat_code`).
- **UI** : champ Code vide avec placeholder « *— attribué automatiquement —* » en création, label devient « *Code (généré à la sauvegarde)* ». Plus de pré-fetch lors d'un changement de type.
- **Plein écran** : `SheetContent` passe à `!w-screen !max-w-none`, contenu centré dans `max-w-7xl mx-auto` pour rester lisible sur très grand écran.
- **Tests** : smoke test live confirmé — création multi-types (A/P/N) génère bien `A00002`, `P00001`, `N00001` ; 5 créations concurrentes → 5 codes uniques.

## Phase 9 — Migration MongoDB → SQLAlchemy/SQLite (2026-02 fork, suite)
**Implémenté** :
- **Renommage des BDD** : `sCardAvo.db` → `CardAvo.db`, `sStaticPc.db` → `StaticPc.db`, `sArt52.db` → `Art52.db` (préfixe `s` retiré).
- **Backend complètement migré** de MongoDB/Motor vers SQLAlchemy 2.0 / SQLite local. Plus aucun appel `db.find_one`/`db.insert_one` Mongo. Tous les endpoints utilisent `Session = Depends(get_db)`.
- **Nouveaux fichiers** :
  - `/app/backend/database.py` : engine + sessionmaker, FK SQLite activées via PRAGMA, switchable vers SQL Server par simple changement de `DATABASE_URL`.
  - `/app/backend/models.py` : 9 modèles ORM (Avocat, Adresse, InfoMega, InfoDistrict, Inhpra, AppUser, AuditLog, Connexion, Mandat) avec mapping legacy (CamelCase preserved + `O`/`N` booléens via helpers `yn_to_bool`/`bool_to_yn`).
  - `/app/backend/scripts/init_app_schema.py` : script idempotent qui renomme les fichiers + ajoute les colonnes app aux tables legacy + crée les 4 tables app (AppUsers, AuditLog, Connexions, **Mandats**).
- **Nouvelle table `Mandats`** dans CardAvo.db (avant : MongoDB) — colonnes : id, avocat_id, requerant, article, date_ordonnance, date_emission, numero, groupe, commentaire, usermodif, created_at, updated_at + index sur avocat_id et date_ordonnance.
- **Tables legacy étendues** (colonnes app ajoutées par ALTER TABLE) :
  - `Avocats` : id (UUID), type_code, actif, attente, annee_barreau, taxes, web_password_hash, villerref, adresse_courante (JSON), created_at, updated_at.
  - `Adresses` : id, avocat_id, address (alias moderne), email, created_at, updated_at. `RowId` legacy populé avec le même UUID.
  - `infomega` : id, avocat_id, tous_districts, created_at, updated_at.
  - `inhpra` : uuid (TEXT, exposé comme `id` côté API), avocat_id, created_at, updated_at — `Id` INTEGER legacy conservé.
- **Adaptations critiques** :
  - Booléens stockés en `'O'/'N'` legacy mais exposés en bool dans l'API (rétro-compat seamless).
  - `adresse` embedded de l'avocat est sérialisé en JSON dans la colonne `adresse_courante`.
  - Districts (many-to-many) dans `infodistrict` : delete-and-reinsert lors de chaque PUT mega.
  - Suppression d'un avocat → cascade sur Adresses + InfoMega + Inhpra + Mandats + InfoDistrict.
  - JWT auth, brute-force lockout (héritée), Fernet password encryption pour Connexions — tout fonctionnel.
- **Tests** : `iteration_9.json` — **39/39 tests SQLAlchemy PASS** (auth, avocats, adresses, méga, inhab, mandats, audit, web pwd, 6 rapports PDF, connexions admin/ti, lecteur 403, persistance après restart).
- **Frontend inchangé** : le contrat API est identique (snake_case, mêmes champs), aucune modification UI requise.

**Documentation mise à jour** :
- `/app/memory/SCHEMAS_SQL_LEGACY.md` : références mises à jour CardAvo/StaticPc/Art52.
- `/app/memory/TABLES_AJOUTEES_APP.md` : ajout de la table Mandats (T-SQL fournie pour SQL Server).

## Phase 10 — Refactor server.py + Page Profil (2026-02 fork, suite)
**Implémenté** :
- **server.py 1413 → 124 lignes** (orchestrateur minimal). Code métier éclaté en :
  - `security.py` (hash, JWT, dépendances FastAPI, Luhn NAS)
  - `schemas.py` (tous les Pydantic models)
  - `audit.py` (write_audit + sérialiseurs ORM→dict)
  - `routers/auth.py`, `avocats.py`, `adresses.py`, `mega_inhab.py`, `mandats.py`, `rapports.py`, `users.py`, `connexions.py`
- **Nouveau endpoint** `PUT /api/auth/change-password` : tout utilisateur authentifié peut changer son propre mot de passe (current_password + new_password ≥ 8 chars). Vérifie l'ancien mot de passe, refuse si identique au nouveau.
- **Nouvelle page** `/profil` accessible à tous les rôles. Affiche carte "Informations" (nom/courriel/rôle avec badge) + formulaire change-password (3 champs + Eye/EyeOff toggle, validations client identiques au serveur).
- **Lien sidebar** "Mon profil" (`data-testid=nav-profil`) ajouté juste au-dessus de l'email et du bouton de déconnexion.
- **WebPasswordIn** Pydantic remplace l'ancien `payload: dict` (validation min_length=6 propre).
- **Tests** : `iteration_11.json` — backend 46/47 (97.9%) + frontend 12/12 (100%). Le seul fail est un changement sémantique 400→422 sur web-password (validation Pydantic plus stricte).

**Cloisonnement Admin/TI** (Phase 9b — déjà appliqué) :
- Admin (non-TI) ne voit pas les comptes TI dans la liste
- Admin ne peut pas créer/modifier/supprimer/promouvoir au rôle TI
- Côté UI : option "TI" cachée du sélecteur de rôle pour les non-TI

**Backlog après Phase 10** :
- **P2** Migration SQL Server → MongoDB (sCardAvo.sql, sStaticPc.sql) quand structure figée
- **P3** Streaming PDF par chunks pour gros datasets
- **P3** Export CSV historique audit (preuve formelle pour audits Barreau/Commission)
- **P3** Filtre par type d'action sur l'onglet Historique
- **P3** Tests E2E par rôles (admin/éditeur/lecteur) systématiques
- **P3** Bilingue FR/EN (extension future)
