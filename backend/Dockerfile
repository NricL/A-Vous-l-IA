# Backend RAG Chatbot (FastAPI + Haystack + Chroma)
# Chat (streaming SSE), documents (ingest/delete), RAG avec embeddings Foundry
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY documents ./documents
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Purge tout bytecode Python périmé éventuellement embarqué depuis le contexte de build
# (des .pyc compilés depuis une ancienne version du code — ou d'une autre version de Python —
# peuvent sinon être exécutés à la place de la source à jour, provoquant des bugs "fantômes"
# où le correctif est bien dans le .py mais l'ancien comportement persiste en prod).
RUN find /app -name '__pycache__' -type d -prune -exec rm -rf {} + || true

# Empêche l'écriture de bytecode au runtime : Python compile toujours depuis la source à jour.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV CHROMA_PERSIST_DIR=/app/data/chroma
RUN mkdir -p /app/data/chroma

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
