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
