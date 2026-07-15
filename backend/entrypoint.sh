#!/bin/sh
# Indexation idempotente : si INDEX_PATH est défini ET l'index Chroma est vide,
# indexer une fois (le volume persistant conserve l'index entre redémarrages).
if [ -n "$INDEX_PATH" ]; then
  COUNT=$(python -c "from app.haystack_rag import get_document_store; print(get_document_store().count_documents())" 2>/dev/null || echo 0)
  case "$COUNT" in
    ''|*[!0-9]*) COUNT=0 ;;
  esac
  if [ "$COUNT" -gt 0 ]; then
    echo "[Entrypoint] Index déjà présent ($COUNT documents), indexation ignorée."
  else
    echo "[Entrypoint] Indexation des documents : $INDEX_PATH"
    python -m app.scripts.index_documents --clear "$INDEX_PATH"
    echo "[Entrypoint] Indexation terminée."
  fi
fi
exec "$@"
