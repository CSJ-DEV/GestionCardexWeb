#!/bin/bash
# Script de démarrage pour Azure App Service Linux (Python 3.12).
# Installe le driver ODBC SQL Server puis lance uvicorn.
# Azure exécute ce script via le champ "Startup Command" de l'App Service.

set -e

echo "=== Installation du driver Microsoft ODBC 18 pour SQL Server ==="
if ! command -v sqlcmd &> /dev/null; then
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/microsoft.gpg || true
    curl -sSL https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list
    apt-get update
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev
fi

echo "=== Démarrage de uvicorn ==="
cd /home/site/wwwroot
gunicorn -w 2 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8000 --timeout 120
