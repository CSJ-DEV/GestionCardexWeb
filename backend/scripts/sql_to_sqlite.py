"""Convertit les 3 dumps SQL Server (.sql, UTF-16) en bases SQLite.
Le but : avoir un environnement de test fonctionnel en ARM64 (où SQL Server n'existe pas)
et fournir au final des fichiers .db utilisables localement ou re-déployables.

Sortie : /app/backend/sqlite_dbs/{sCardAvo,sStaticPc,sArt52}.db
"""
from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path

# Mapping des types SQL Server → SQLite
# SQLite est typeless en pratique mais on garde les "types affinity" pour la doc.
TYPE_MAPPING = {
    # Chaînes
    r"char\(\d+\)": "TEXT",
    r"varchar\(\d+\)": "TEXT",
    r"varchar\(max\)": "TEXT",
    r"nchar\(\d+\)": "TEXT",
    r"nvarchar\(\d+\)": "TEXT",
    r"nvarchar\(max\)": "TEXT",
    r"text": "TEXT",
    r"ntext": "TEXT",
    # Entiers
    r"tinyint": "INTEGER",
    r"smallint": "INTEGER",
    r"int": "INTEGER",
    r"bigint": "INTEGER",
    r"bit": "INTEGER",  # 0/1
    # Numériques
    r"decimal\(\d+(?:,\s*\d+)?\)": "NUMERIC",
    r"numeric\(\d+(?:,\s*\d+)?\)": "NUMERIC",
    r"money": "NUMERIC",
    r"smallmoney": "NUMERIC",
    r"float(?:\(\d+\))?": "REAL",
    r"real": "REAL",
    # Dates (en ISO TEXT — SQLite n'a pas de type date)
    r"datetime": "TEXT",
    r"datetime2(?:\(\d+\))?": "TEXT",
    r"smalldatetime": "TEXT",
    r"date": "TEXT",
    r"time(?:\(\d+\))?": "TEXT",
    # Binaires / autres
    r"varbinary\(\d+\)": "BLOB",
    r"varbinary\(max\)": "BLOB",
    r"binary\(\d+\)": "BLOB",
    r"image": "BLOB",
    r"uniqueidentifier": "TEXT",  # GUID stocké comme TEXT
    r"timestamp": "BLOB",
    r"xml": "TEXT",
}

CREATE_TABLE_RE = re.compile(
    r"CREATE TABLE \[dbo\]\.\[(?P<table>[^\]]+)\]\s*\((?P<body>.*?)\n\) ON \[PRIMARY\]",
    re.DOTALL,
)

INSERT_RE = re.compile(
    r"INSERT \[dbo\]\.\[(?P<table>[^\]]+)\]\s*\((?P<cols>[^)]+)\)\s*VALUES\s*\((?P<vals>.*?)\)",
    re.DOTALL,
)


def map_type(sql_type: str) -> str:
    """Mappe un type SQL Server vers SQLite (insensible à la casse)."""
    s = sql_type.strip().lower()
    for pattern, sqlite_type in TYPE_MAPPING.items():
        if re.fullmatch(pattern, s):
            return sqlite_type
    return "TEXT"  # fallback safe


PK_BLOCK_RE = re.compile(
    r"(?:CONSTRAINT[^P]+)?PRIMARY KEY\s+(?:CLUSTERED|NONCLUSTERED)?\s*\(\s*(?P<cols>.*?)\s*\)",
    re.DOTALL | re.IGNORECASE,
)


def convert_create_table(table: str, body: str) -> str:
    """Convertit un CREATE TABLE SQL Server → SQLite.
    
    Stratégie : extraire d'abord les contraintes PK (qui sont multilignes en SSMS),
    puis traiter chaque ligne de colonne individuellement.
    """
    lines = []
    pk_cols: list[str] = []
    has_identity = False

    # 1) Extraire les colonnes PK (multi-ligne) puis retirer les blocs CONSTRAINT du body
    pk_match = PK_BLOCK_RE.search(body)
    if pk_match:
        for col_match in re.finditer(r"\[([^\]]+)\]\s*(?:ASC|DESC)?", pk_match.group("cols")):
            col_name = col_match.group(1)
            if col_name not in pk_cols:
                pk_cols.append(col_name)
    # Retirer les blocs CONSTRAINT/UNIQUE/PRIMARY KEY entiers pour ne pas confondre avec les colonnes
    body_no_constraints = re.sub(
        r"(?:CONSTRAINT\s*\[[^\]]+\]\s*)?(?:PRIMARY KEY|UNIQUE)\s+(?:CLUSTERED|NONCLUSTERED)?\s*\([^)]*\)\s*(?:WITH\s*\([^)]*\))?\s*(?:ON\s*\[PRIMARY\])?",
        "",
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )
    # Retirer aussi les "ON [PRIMARY]" résiduels et "WITH(...)" trailing
    body_no_constraints = re.sub(r"WITH\s*\([^)]*\)\s*ON\s*\[PRIMARY\]", "", body_no_constraints, flags=re.IGNORECASE)
    body_no_constraints = re.sub(r"ON\s*\[PRIMARY\]", "", body_no_constraints, flags=re.IGNORECASE)

    # 2) Parser chaque ligne de colonne
    raw_lines = [l.strip() for l in body_no_constraints.split("\n") if l.strip()]
    for line in raw_lines:
        line = line.rstrip(",").strip()
        if not line or line in ("(", ")"):
            continue
        # Lignes résiduelles d'options de contraintes
        if any(line.upper().startswith(opt) for opt in
               ("PAD_INDEX", "STATISTICS_NORECOMPUTE", "ALLOW_ROW_LOCKS",
                "ALLOW_PAGE_LOCKS", "FILLFACTOR", "OPTIMIZE_FOR_SEQUENTIAL_KEY",
                "IGNORE_DUP_KEY", "WITH ", "WITH(", "CONSTRAINT")):
            continue

        # Colonne : [name] [type] [(args)] [rest]
        m = re.match(
            r"\[(?P<col>[^\]]+)\]\s+\[(?P<type>[^\]]+)\](?:\s*\((?P<args>[^)]*)\))?\s*(?P<rest>.*)",
            line,
        )
        if not m:
            continue
        col = m.group("col")
        ctype = m.group("type")
        args = m.group("args") or ""
        rest = (m.group("rest") or "").upper()
        type_str = f"{ctype}({args})" if args else ctype
        sqlite_type = map_type(type_str)
        nullable = "NOT NULL" not in rest
        identity = "IDENTITY" in rest
        if identity and not has_identity:
            col_def = f'"{col}" INTEGER PRIMARY KEY AUTOINCREMENT'
            has_identity = True
            pk_cols = []  # PK déjà déclarée
        else:
            col_def = f'"{col}" {sqlite_type}'
            if not nullable:
                col_def += " NOT NULL"
        lines.append(col_def)

    if pk_cols and not has_identity:
        pk_quoted = ", ".join(f'"{c}"' for c in pk_cols)
        lines.append(f"PRIMARY KEY ({pk_quoted})")

    return f'CREATE TABLE "{table}" (\n  ' + ",\n  ".join(lines) + "\n);"


def convert_database(sql_path: Path, db_path: Path) -> dict:
    """Lit un .sql.utf8 et crée le .db SQLite correspondant. Retourne stats."""
    sql = sql_path.read_text(encoding="utf-8", errors="replace").replace("\x00", "")
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF;")
    cur = conn.cursor()

    tables_created = 0
    rows_inserted = 0
    errors = []

    # 1) Tables
    for m in CREATE_TABLE_RE.finditer(sql):
        table = m.group("table")
        try:
            ddl = convert_create_table(table, m.group("body"))
            cur.execute(ddl)
            tables_created += 1
        except sqlite3.Error as e:
            errors.append(f"{table}: {e}")

    # 2) INSERTs (souvent peu nombreux dans des dumps schema-only)
    for m in INSERT_RE.finditer(sql):
        table = m.group("table")
        cols = [c.strip().strip("[]") for c in m.group("cols").split(",")]
        vals_text = m.group("vals")
        # Parsing naïf — suffisant pour les valeurs simples (strings entre quotes, NULL, nombres)
        vals = _split_values(vals_text)
        try:
            placeholders = ", ".join(["?"] * len(vals))
            quoted_cols = ", ".join(f'"{c}"' for c in cols)
            cur.execute(f'INSERT INTO "{table}" ({quoted_cols}) VALUES ({placeholders})', vals)
            rows_inserted += 1
        except sqlite3.Error as e:
            errors.append(f"INSERT {table}: {e}")

    conn.commit()
    conn.close()
    return {"tables": tables_created, "rows": rows_inserted, "errors": errors}


def _split_values(vals_text: str) -> list:
    """Parse une liste de valeurs SQL Server VALUES(...) → liste Python."""
    out = []
    i = 0
    n = len(vals_text)
    while i < n:
        # skip spaces / commas
        while i < n and vals_text[i] in " ,\n":
            i += 1
        if i >= n:
            break
        ch = vals_text[i]
        if ch == "'":  # string
            j = i + 1
            buf = []
            while j < n:
                if vals_text[j] == "'":
                    if j + 1 < n and vals_text[j + 1] == "'":
                        buf.append("'")
                        j += 2
                    else:
                        break
                else:
                    buf.append(vals_text[j])
                    j += 1
            out.append("".join(buf))
            i = j + 1
        elif ch == "N" and i + 1 < n and vals_text[i + 1] == "'":  # N'string'
            i += 1
            continue  # repasse en mode string sur la prochaine itération
        else:
            j = i
            while j < n and vals_text[j] not in ",)":
                j += 1
            tok = vals_text[i:j].strip()
            if tok.upper() == "NULL":
                out.append(None)
            else:
                try:
                    out.append(int(tok))
                except ValueError:
                    try:
                        out.append(float(tok))
                    except ValueError:
                        out.append(tok)  # fallback string brut
            i = j
    return out


def main():
    src_dir = Path("/tmp")
    out_dir = Path("/app/backend/sqlite_dbs")
    out_dir.mkdir(exist_ok=True, parents=True)

    targets = {
        "sCardAvo": src_dir / "sCardAvo.sql.utf8",
        "sStaticPc": src_dir / "sStaticPc.sql.utf8",
        "sArt52": src_dir / "sArt52.sql.utf8",
    }

    print(f"Sortie : {out_dir}\n")
    total_tables = 0
    total_rows = 0
    for name, sql_path in targets.items():
        if not sql_path.exists():
            print(f"  ⚠️  {name}: source manquante {sql_path}")
            continue
        db_path = out_dir / f"{name}.db"
        stats = convert_database(sql_path, db_path)
        size = os.path.getsize(db_path)
        total_tables += stats["tables"]
        total_rows += stats["rows"]
        print(f"  ✅ {name}.db — {stats['tables']} tables, {stats['rows']} rows, {size} bytes")
        if stats["errors"]:
            for err in stats["errors"][:3]:
                print(f"     ⚠️  {err}")
            if len(stats["errors"]) > 3:
                print(f"     ⚠️  ... et {len(stats['errors']) - 3} autres erreurs")

    print(f"\n📊 Total : {total_tables} tables, {total_rows} rows")

    # Ajouter les 3 tables propres à l'app web dans sCardAvo (idempotent)
    _add_app_tables(out_dir / "sCardAvo.db")
    print("  ➕ AppUsers / AuditLog / Connexions ajoutées dans sCardAvo.db")


def _add_app_tables(db_path: Path) -> None:
    """Ajoute les 3 tables introduites par l'app web (auth, audit, connexions)."""
    if not db_path.exists():
        return
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
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
    ''')
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
