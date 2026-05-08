"""Initialise / migre les bases SQLite pour l'application web :
1. Renomme `sCardAvo.db` → `CardAvo.db`, `sStaticPc.db` → `StaticPc.db`,
   `sArt52.db` → `Art52.db` (idempotent).
2. Ajoute aux tables legacy les colonnes nécessaires à l'app web :
   - `Avocats` : id, type_code, actif, attente, annee_barreau, taxes,
     dateinscbarr (déjà présent), web_password_hash, created_at, updated_at.
   - `Adresses` : id, avocat_id, address (alias moderne d'`adresse`), telephone,
     telephone2, email (alias d'`adremail`), updated_at, created_at.
   - `infomega` : id, avocat_id, francais (bool), anglais (bool), tous_districts,
     created_at, updated_at.
   - `inhpra` : id (TEXT UUID), avocat_id, created_at, updated_at.
3. Crée la table `Mandats` (introduite par l'app web).
4. Crée les tables `AppUsers`, `AuditLog`, `Connexions` (idempotent).

Ce script est ré-exécutable autant de fois que nécessaire.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).parent.parent / "sqlite_dbs"

# Mapping renommage (ancien → nouveau)
RENAMES = {
    "sCardAvo.db": "CardAvo.db",
    "sStaticPc.db": "StaticPc.db",
    "sArt52.db": "Art52.db",
}


def rename_files() -> None:
    for old, new in RENAMES.items():
        old_p = DB_DIR / old
        new_p = DB_DIR / new
        if old_p.exists() and not new_p.exists():
            old_p.rename(new_p)
            print(f"  ✅ Renommé : {old} → {new}")
        elif old_p.exists() and new_p.exists():
            # Conflit : on garde le nouveau, on supprime l'ancien
            old_p.unlink()
            print(f"  ⚠️  {new} existait déjà, {old} supprimé")
        elif new_p.exists():
            print(f"  ✓ {new} déjà en place")


def _column_exists(cur: sqlite3.Cursor, table: str, column: str) -> bool:
    cur.execute(f'PRAGMA table_info("{table}")')
    return any(row[1] == column for row in cur.fetchall())


def _table_exists(cur: sqlite3.Cursor, table: str) -> bool:
    cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None


def _add_column_if_missing(cur: sqlite3.Cursor, table: str, column: str, ddl: str) -> bool:
    if not _table_exists(cur, table):
        return False
    if not _column_exists(cur, table, column):
        cur.execute(f'ALTER TABLE "{table}" ADD COLUMN {ddl}')
        return True
    return False


def migrate_card_avo() -> None:
    db_path = DB_DIR / "CardAvo.db"
    if not db_path.exists():
        print(f"  ❌ {db_path} introuvable — exécutez sql_to_sqlite.py d'abord")
        return
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # ----- Avocats : ajout colonnes app -----
    avocats_cols = [
        ('id', '"id" TEXT'),
        ('type_code', '"type_code" TEXT NOT NULL DEFAULT \'A\''),
        ('actif', '"actif" INTEGER NOT NULL DEFAULT 1'),
        ('attente', '"attente" INTEGER NOT NULL DEFAULT 0'),
        ('annee_barreau', '"annee_barreau" TEXT'),
        ('taxes', '"taxes" TEXT'),
        ('web_password_hash', '"web_password_hash" TEXT'),
        ('villerref', '"villerref" TEXT'),  # alias plus complet (legacy a villeref)
        ('adresse_courante', '"adresse_courante" TEXT'),  # JSON snapshot de l'adresse courante
        ('created_at', '"created_at" TEXT'),
        ('updated_at', '"updated_at" TEXT'),
    ]
    added = 0
    for col, ddl in avocats_cols:
        if _add_column_if_missing(cur, "Avocats", col, ddl):
            added += 1
    if added:
        print(f"  ✅ Avocats : {added} colonne(s) ajoutée(s)")

    # ----- Adresses : ajout colonnes app -----
    adresses_cols = [
        ('id', '"id" TEXT'),
        ('avocat_id', '"avocat_id" TEXT'),
        ('address', '"address" TEXT'),  # alias moderne (legacy = "adresse")
        ('email', '"email" TEXT'),       # alias d'`adremail`
        ('created_at', '"created_at" TEXT'),
        ('updated_at', '"updated_at" TEXT'),
    ]
    added = 0
    for col, ddl in adresses_cols:
        if _add_column_if_missing(cur, "Adresses", col, ddl):
            added += 1
    if added:
        print(f"  ✅ Adresses : {added} colonne(s) ajoutée(s)")

    # ----- infomega : ajout colonnes app -----
    mega_cols = [
        ('id', '"id" TEXT'),
        ('avocat_id', '"avocat_id" TEXT'),
        ('tous_districts', '"tous_districts" INTEGER NOT NULL DEFAULT 0'),
        ('created_at', '"created_at" TEXT'),
        ('updated_at', '"updated_at" TEXT'),
    ]
    added = 0
    for col, ddl in mega_cols:
        if _add_column_if_missing(cur, "infomega", col, ddl):
            added += 1
    if added:
        print(f"  ✅ infomega : {added} colonne(s) ajoutée(s)")

    # ----- inhpra : ajout colonnes app -----
    inhpra_cols = [
        ('uuid', '"uuid" TEXT'),  # legacy a déjà un Id INTEGER, on ajoute uuid
        ('avocat_id', '"avocat_id" TEXT'),
        ('created_at', '"created_at" TEXT'),
        ('updated_at', '"updated_at" TEXT'),
    ]
    added = 0
    for col, ddl in inhpra_cols:
        if _add_column_if_missing(cur, "inhpra", col, ddl):
            added += 1
    if added:
        print(f"  ✅ inhpra : {added} colonne(s) ajoutée(s)")

    # ----- Tables app web : AppUsers, AuditLog, Connexions, Mandats -----
    cur.executescript('''
        CREATE TABLE IF NOT EXISTS "AppUsers" (
            "id" TEXT NOT NULL PRIMARY KEY,
            "email" TEXT NOT NULL,
            "password_hash" TEXT NOT NULL,
            "name" TEXT,
            "role" TEXT NOT NULL CHECK ("role" IN ('admin','ti','editeur','lecteur')),
            "created_at" TEXT NOT NULL
        );
        CREATE UNIQUE INDEX IF NOT EXISTS "UX_AppUsers_email" ON "AppUsers"("email");

        CREATE TABLE IF NOT EXISTS "AuditLog" (
            "id" TEXT NOT NULL PRIMARY KEY,
            "avocat_id" TEXT NOT NULL,
            "action" TEXT NOT NULL,
            "user_email" TEXT NOT NULL,
            "summary" TEXT,
            "timestamp" TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS "IX_AuditLog_avocat_ts" ON "AuditLog"("avocat_id", "timestamp" DESC);

        CREATE TABLE IF NOT EXISTS "Connexions" (
            "id" TEXT NOT NULL PRIMARY KEY,
            "name" TEXT NOT NULL,
            "type" TEXT NOT NULL CHECK ("type" IN ('mongodb','sqlserver','sqlite')),
            "server" TEXT NOT NULL,
            "port" INTEGER,
            "user" TEXT,
            "database" TEXT,
            "description" TEXT,
            "password_enc" TEXT,
            "is_primary" INTEGER NOT NULL DEFAULT 0,
            "created_at" TEXT NOT NULL,
            "updated_at" TEXT NOT NULL
        );
        CREATE UNIQUE INDEX IF NOT EXISTS "UX_Connexions_name" ON "Connexions"("name");

        -- Table Mandats : nouvelle entité introduite par l'app web (Registre97/98)
        CREATE TABLE IF NOT EXISTS "Mandats" (
            "id" TEXT NOT NULL PRIMARY KEY,
            "avocat_id" TEXT NOT NULL,
            "requerant" TEXT,
            "article" TEXT NOT NULL DEFAULT '486.3',
            "date_ordonnance" TEXT,
            "date_emission" TEXT,
            "numero" TEXT,
            "groupe" TEXT NOT NULL DEFAULT 'Pratique Privée',
            "commentaire" TEXT,
            "usermodif" TEXT,
            "created_at" TEXT NOT NULL,
            "updated_at" TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS "IX_Mandats_avocat" ON "Mandats"("avocat_id");
        CREATE INDEX IF NOT EXISTS "IX_Mandats_dates" ON "Mandats"("date_ordonnance");
    ''')
    print("  ✅ AppUsers / AuditLog / Connexions / Mandats : tables OK")

    # ----- Index utiles sur les colonnes app -----
    try:
        cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS "UX_Avocats_id" ON "Avocats"("id") WHERE "id" IS NOT NULL')
        cur.execute('CREATE INDEX IF NOT EXISTS "IX_Adresses_avocat" ON "Adresses"("avocat_id")')
        cur.execute('CREATE INDEX IF NOT EXISTS "IX_infomega_avocat" ON "infomega"("avocat_id")')
        cur.execute('CREATE INDEX IF NOT EXISTS "IX_inhpra_avocat" ON "inhpra"("avocat_id")')
        cur.execute('CREATE INDEX IF NOT EXISTS "IX_infodistrict_code" ON "infodistrict"("code")')
        print("  ✅ Index app créés")
    except sqlite3.OperationalError as e:
        print(f"  ⚠️  Index : {e}")

    conn.commit()
    conn.close()


def main():
    print("=== Renommage des fichiers SQLite ===")
    rename_files()
    print("\n=== Migration du schéma CardAvo.db ===")
    migrate_card_avo()
    print("\n✅ Migration terminée")


if __name__ == "__main__":
    main()
