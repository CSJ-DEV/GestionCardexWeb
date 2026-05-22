#!/usr/bin/env bash
# sync-requirements.sh
# ---------------------------------------------------------------------
# Régénère backend/requirements.txt depuis le venv actif via `pip freeze`
# puis le copie à la racine du repo.
#
# Utilisation :
#   bash scripts/sync-requirements.sh
# ---------------------------------------------------------------------
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_REQ="${ROOT_DIR}/backend/requirements.txt"
ROOT_REQ="${ROOT_DIR}/requirements.txt"

if ! command -v pip >/dev/null 2>&1; then
    echo "[ERREUR] pip introuvable. Active ton venv avant d'exécuter ce script." >&2
    exit 1
fi

echo "[1/2] pip freeze -> ${BACKEND_REQ}"
pip freeze --exclude-editable > "${BACKEND_REQ}"

echo "[2/2] Copie -> ${ROOT_REQ}"
cp "${BACKEND_REQ}" "${ROOT_REQ}"

echo "OK : $(wc -l < "${BACKEND_REQ}") paquets synchronisés."
