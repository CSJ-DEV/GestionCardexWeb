# Scripts utilitaires

## sync-requirements

Régénère `backend/requirements.txt` depuis le `venv` Python actif (via
`pip freeze`) puis le copie à la racine du repo (`/requirements.txt`)
pour qu'il soit visible par les outils de CI/CD et les hosts qui
cherchent ce fichier à la racine.

### Quand l'utiliser

Après avoir installé ou mis à jour un paquet :

```bash
pip install <nouveau_paquet>
bash scripts/sync-requirements.sh         # Linux / Mac / Git Bash
# OU
.\scripts\sync-requirements.ps1           # Windows / PowerShell
```

### Pré-requis

- Le `venv` doit être **actif** avant l'exécution.
- Linux/Mac : `bash scripts/sync-requirements.sh`
- Windows PowerShell : `.\scripts\sync-requirements.ps1`
  (si Execution Policy refuse, lance d'abord :
   `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)
