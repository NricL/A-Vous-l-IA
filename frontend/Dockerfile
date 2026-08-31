# Frontend RAG Chatbot (Vue 3 + Vite)
# Étape 1 : build production
FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build-only

# Étape 2 : serveur nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
# nginx.conf.template : l'entrypoint officiel de l'image nginx exécute envsubst sur
# /etc/nginx/templates/*.template au démarrage → /etc/nginx/conf.d/. La seule variable
# substituée est ${BACKEND_ORIGIN} (Axe 4.5 : URL backend = source unique, surchargée
# par l'env du conteneur). Valeur par défaut = backend de dev ci-dessous.
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
ENV BACKEND_ORIGIN=https://avoulia-backend.purpleocean-980317d1.francecentral.azurecontainerapps.io

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
