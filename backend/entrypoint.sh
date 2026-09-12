#!/bin/sh
set -eu

# Indexation idempotente : si INDEX_PATH est défini ET l'index Chroma est vide,
# indexer une fois (le volume persistant conserve l'index entre redémarrages).
if [ -n "${INDEX_PATH:-}" ]; then
  if ! COUNT=$(python -c "from app.haystack_rag import get_document_store; print(get_document_store().count_documents())"); then
    echo "[Entrypoint] Lecture de l'index impossible ; démarrage interrompu." >&2
    exit 1
  fi
  case "$COUNT" in
    ''|*[!0-9]*)
      echo "[Entrypoint] Nombre de documents invalide ; démarrage interrompu." >&2
      exit 1
      ;;
  esac
  if [ "$COUNT" -gt 0 ]; then
    echo "[Entrypoint] Index déjà présent ($COUNT documents), indexation ignorée."
  else
    echo "[Entrypoint] Indexation des documents : $INDEX_PATH"
    python -m app.scripts.index_documents --require-empty "$INDEX_PATH"
    echo "[Entrypoint] Indexation terminée."
  fi
fi
exec "$@"
