# sync-requirements.ps1
# ---------------------------------------------------------------------
# Régénère backend\requirements.txt depuis le venv actif via `pip freeze`
# puis le copie à la racine du repo. Version Windows / PowerShell.
#
# Utilisation :
#   .\scripts\sync-requirements.ps1
#
# (Active d'abord ton venv : .\backend\venv\Scripts\Activate.ps1)
# ---------------------------------------------------------------------

$ErrorActionPreference = "Stop"

$RootDir    = Resolve-Path (Join-Path $PSScriptRoot "..")
$BackendReq = Join-Path $RootDir "backend\requirements.txt"
$RootReq    = Join-Path $RootDir "requirements.txt"

if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Error "[ERREUR] pip introuvable. Active ton venv avant d'executer ce script."
    exit 1
}

Write-Host "[1/2] pip freeze -> $BackendReq"
pip freeze --exclude-editable | Out-File -FilePath $BackendReq -Encoding utf8

Write-Host "[2/2] Copie -> $RootReq"
Copy-Item $BackendReq $RootReq -Force

$lines = (Get-Content $BackendReq).Length
Write-Host "OK : $lines paquets synchronises."
