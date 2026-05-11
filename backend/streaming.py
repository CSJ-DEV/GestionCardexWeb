"""Helpers de streaming HTTP pour les gros payloads (rapports PDF principalement).

Le but : éviter de garder l'intégralité du PDF en mémoire dans la file de réponse
de Uvicorn/Starlette. On découpe les bytes par chunks de 64 Ko et on émet via
un générateur, ce qui permet au client (browser ou curl) de commencer à recevoir
immédiatement et au serveur de libérer la mémoire après envoi de chaque chunk.

Pour les gros volumes côté lecture BDD, on s'appuie sur SQLAlchemy `yield_per()`
qui charge les rangées par batches au lieu de tout matérialiser en mémoire.
"""
from __future__ import annotations

from typing import Iterator

# 64 Ko : valeur classique alignée sur les buffers TCP/HTTP. Chaque chunk est
# atomique côté response.body_iterator → Starlette n'agrège pas.
CHUNK_SIZE = 64 * 1024


def chunk_bytes(data: bytes, chunk_size: int = CHUNK_SIZE) -> Iterator[bytes]:
    """Découpe un buffer bytes en chunks de taille fixe pour StreamingResponse.

    Exemple : un PDF de 4 Mo génère 64 chunks de 64 Ko au lieu d'un seul payload
    monolithique en RAM. Pas de copie supplémentaire : on slice la `bytes`
    immuable (slices de bytes sont des vues quand possible en CPython).
    """
    if not data:
        return
    total = len(data)
    for i in range(0, total, chunk_size):
        yield data[i:i + chunk_size]


def pdf_streaming_headers(filename: str, total_bytes: int) -> dict:
    """Headers HTTP standardisés pour la livraison d'un PDF en streaming.

    - Content-Length : permet au navigateur d'afficher une barre de progression.
    - Content-Disposition : attachment + nom de fichier proposé.
    - Cache-Control : empêche le cache navigateur (les rapports sont datés).
    """
    return {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Length": str(total_bytes),
        "Cache-Control": "no-store, max-age=0",
        "X-Accel-Buffering": "no",  # désactive le buffering nginx → vrai streaming
    }
