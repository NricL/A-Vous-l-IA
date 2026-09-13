# Avoulia V2 — Implementation Handover Guide for Simplon

## État déployé — 13 septembre 2026

Le dev sert maintenant v461 via `avoulia-backend--v461-20260913-r3`,100% trafic, mode Single ; image `sha256:9c356b0643a3313709f434d73505b6c7e98b49fca735ad869983b0e835410c1b`. Le frontend de référence reste https://nricl.github.io/A-Vous-l-IA/. Les étapes de préparation ci-dessous sont historiques, pas des tâches à recommencer.

Le mapping et le classeur sont sous `/app/private`, jamais sous la racine web. Les exports hérités sont conservés dans un sous-dossier privé et le serveur statique refuse leurs extensions. `INDEX_PATH` désigne le fichier explicite ; l'index utilise un répertoire/une collection propres à cette révision, sans effacement du précédent.

**Attention stockage :** une déclaration Azure Files existe, mais aucun montage n'était attaché au conteneur observé. L'index est donc local à la réplique et peut être reconstruit à son redémarrage. Ne pas annoncer une persistance Azure Files sans la mettre en œuvre et la vérifier dans un lot dédié.

**Rollback :** anciennes images et définitions de révision conservées ; les anciennes répliques sont inactives pour éviter des coûts et des endpoints hérités inutiles. Une restauration doit remettre ensemble code, catalogue, index et pages. Le retour à0045 remettrait aussi ses anciens comportements de confidentialité : préférer une correction conservant la protection du webroot lorsque possible. Ne jamais vider le nouvel index pour improviser un retour arrière.

**Sources / vitrine finalisées :** chatbot `24e145b` et parcours `a500a22` publiés ; Pages et frontend Azure affichent 1 021 cas, 14 domaines métier et 71 intentions. Frontend Azure `avoulia-frontend--v461-20260913`. Les mentions de préparation/non-publication plus bas sont historiques.

### Reprise du 13 septembre — lot UX-01 à UX-05

Les cinq frictions post-livraison ont des correctifs locaux : sélection du cas unique, exemples Q3 trop denses avec pipes bruts, exemples hors contexte Cabinet & conseil, besoin initial du magasin redemandé et suggestion secondaire supposant une saisonnalité. Ces correctifs ne sont pas encore déployés.

La documentation a été rapprochée avant l'implémentation. Voir la table active de `ROADMAP.md`. Ne pas relancer l'intégration v461, régénérer les pages, modifier le classeur ou préparer Simplon. Le composant actif est `frontend/src/views/HomeView.vue` ; ses boutons utilisent `suggestedCases` conservé dans chaque message. La réponse détail peut contenir plusieurs candidats : la présence de candidats seule ne suffit pas, le CTA autoritaire `parcours_url` et le marqueur de détail restent prioritaires. Le retour à la liste restaure ces candidats, pas ceux du dernier détail.

Les exemples Q3 utilisent l'éligibilité sectorielle de Q2, conservent le filtre intention et limitent à quatre situations après séparation/dédoublonnage. Une intention invalide ne doit pas revenir à tous les exemples du domaine. Le besoin initial reste réutilisable lors d'une correction ; un Q3 donné sous d'anciens choix est au contraire invalidé.

**Reproduire hors ligne depuis `backend` :** définir `PYTHONPATH=tests` puis lancer `python -B -m unittest test_haystack_rag test_chat_regressions test_chat_relevance test_case_selection_prompt test_relevance_evaluation test_catalogue_integration -q`. Définir `PARCOURS_SOURCE_ROOT` vers le checkout parcours rapproché pour inclure les contrôles associés. Depuis `frontend` : `npm run check:chat`, `npm run type-check`, `npm run build-only`.

**Évaluer UX-05 :** `python scripts\evaluate_chat_relevance.py --suite stock-assumptions --repeats 2 --max-completion-tokens 6000` prépare les huit requêtes sans réseau. Ajouter `--live --subscription "<abonnement-dev>" --resource-group rg-avoulia-fr-dev --container-app avoulia-backend --interval-seconds 90 --output "<dossier-prive-existant>\ux05.json"` uniquement pour un passage autorisé. Aucun classeur n'est lu ; les rapports contiennent les réponses brutes fictives et les paramètres, pas les identifiants d'authentification. Ne pas transformer les attentes techniques en taux de précision utilisateurs.

**Prochaine recette de déploiement, après confirmation :** utiliser `Dockerfile.dev-catalogue-code-fix` avec l'image r3 épinglée en tête et un contexte privé minimal. L'overlay doit comprendre **`app/haystack_rag.py` et `app/rag_constants.py`** ensemble ; inclure les tests et le banc à jour dans le paquet de validation. L'ancien `Dockerfile.dev-code-only` du 10 septembre ne copie pas `rag_constants.py` et ne suffit pas à ce lot. Hériter catalogue/pages/mapping, préserver les exports hors webroot, et valider dans l'image avant bascule. Pas de régénération ou d'effacement d'index ; un remplacement de réplique peut néanmoins reconstruire son index local au démarrage.

Préserver les changements préexistants du plan Azure et des worktrees parcours. Le reçu local Azure décrit la finalisation déjà effectuée ; sa présence modifiée n'indique pas un déploiement en attente. Les futures publications nécessitent leur aperçu et confirmation propres.

## Reprise prioritaire — 12 septembre 2026

**Point de départ historique au 12 septembre :** classeur privé consolidé et sauvegardé, avant son intégration. Le chemin, l'empreinte et les journaux exacts se trouvent dans le suivi privé et le classeur, jamais dans un export GitHub public. L'état courant figure en tête.

1. **Choisir explicitement la source.** Préserver le classeur original et ses restrictions. Ne pas prendre le premier fichier `*.xlsx`, la plus grande version trouvée dans un dossier ou la copie historique du dépôt. Ne pas lire une feuille d'audit : `Sheet1` est le catalogue courant ; `BASE_PROPOSEE` est historique.
2. **Valider l'import.** Contrôler l'unicité et la présence des IDs, les champs obligatoires, les valeurs calculées, puis le nombre de documents. Une formule sans valeur recalculée ne devient pas un texte indexable ; ne pas envoyer les formules elles-mêmes aux embeddings.
3. **Aligner les secteurs.** Conserver l'ordre des choix existants et les domaines qui n'affichent pas Q1.5. Compléter les choix à partir des métadonnées du catalogue chargé ; ne jamais supprimer le secteur de la recherche pour obtenir des résultats. Des cas multi-sectoriels doivent rester accessibles.
4. **Préparer ensemble index et parcours.** Utiliser le générateur `avoulia-parcours`, pas l'ancien script backend. Préserver les couples ID/hash publiés et le sel ; refuser un mapping incomplet ou ambigu. Générer dans une destination nouvelle plutôt qu'effacer le `dist` existant. Les gabarits CHAT-04/05/06 ne prennent effet qu'après cette régénération.
5. **Recetter avant toute bascule.** Rapprocher ID → contenu source → résultat indexé → détail verbatim → URL → contenu de la page. Couvrir aussi listes courtes, absence de correspondance, secteurs composés, retour arrière, HTTP/SSE et mobile. Un bon décompte de pages n'est pas une preuve de bonne correspondance.
6. **Autoriser la destination avant publication.** Une URL difficile à deviner et `noindex` ne constituent pas un contrôle d'accès. Les pages contiennent du texte issu du classeur : ne pas les publier sur un site public sans autorisation explicite sur cette exposition. Prévoir la restauration cohérente de l'index, des pages, du mapping et de l'image précédente.

La demande d'exécution autonome du 12 septembre dispense des validations éditoriales répétitives, pas de la protection des données ni des gates de déploiement. Une publication GitHub de code/documentation ne doit contenir ni workbook, ni export de catalogue, ni nouveau mapping privé. Aucun package Simplon n'est demandé à ce stade.

### Précontrôle d'indexation — lot local du 12 septembre

Depuis `backend`, `python -m app.scripts.index_documents --validate-only "<source-privee.xlsx>"` charge et valide les sources, affiche les comptes et n'appelle ni Chroma ni les embeddings. Utiliser ce mode avant toute construction d'index ; conserver les résultats détaillés hors du dépôt public.

Pour la future construction autorisée, configurer explicitement une **nouvelle collection et un emplacement privé** puis utiliser `--require-empty`. Cette option refuse une collection non vide ; elle ne choisit pas elle-même un environnement isolé. Ne jamais pointer cette commande sur l'index en service par commodité. Une erreur d'embeddings peut laisser un index candidat partiel : ne pas le promouvoir et reconstruire dans un autre candidat vide.

`--clear` reste disponible pour les usages explicitement autorisés, mais les sources sont désormais toutes chargées avant le vidage. Ce mode **ne constitue pas une transaction ni un rollback**. Le démarrage du conteneur n'utilise plus `--clear` : il refuse une erreur de lecture du compte, un résultat invalide ou une indexation échouée, au lieu de démarrer comme si tout était prêt.

Un index existant est volontairement conservé au redémarrage : remplacer uniquement `INDEX_PATH` ou le classeur ne réindexe pas les données. La future bascule doit donc identifier explicitement le nouvel index et garder l'ancien disponible.

### Génération préparatoire explicite

Depuis le dépôt associé `avoulia-parcours`, après autorisation de traitement dans la destination privée :

```powershell
python pipeline\genere.py --workbook "<source-privee.xlsx>" --sheet Sheet1 --mapping "<mapping-existant.csv>" --output-dir "<nouveau-dossier-prive>" --layout backend --app-url "https://nricl.github.io/A-Vous-l-IA/"
```

Cette commande prépare `action-<hash>.html` et un CSV `case_id,case_hash,url` dans un **dossier privé**. Ne pas publier ce dossier tel quel : le mapping ne doit pas être servi. Les entrées historiques du mapping sont conservées, mais leurs pages ne sont pas régénérées lorsqu'elles sont absentes du catalogue ; décider de leur conservation avant toute bascule globale. Les hashes ne sont pas recalculés avec un sel de développement.

Le workflow du dépôt parcours associé est désormais manuel, avec source, mapping et confirmation de publication explicites. Il refuse une différence d'IDs entre catalogue et mapping avant un remplacement de site, retire le mapping du répertoire web et ne charge pas celui-ci en artefact. Configurer les protections de l'environnement GitHub `parcours-publication` avant usage ; aucune protection distante n'a été configurée par le code local.

Les régressions backend se lancent avec `python -B -m unittest discover -s tests -q`. Pour couvrir aussi le générateur et son workflow, définir `PARCOURS_SOURCE_ROOT` vers le dépôt associé ; sinon les classes concernées sont explicitement ignorées. Les contrôles locaux ont utilisé Python 3.14 et un environnement `.venv` isolé pour la dépendance LangChain manquante ; revalider dans l'image Python 3.11 avant déploiement.

## Canal de livraison Eneric — confirmé le 10 septembre 2026

Référence de code et suivi : `NricL/A-Vous-l-IA`. Référence de test utilisateur : https://nricl.github.io/A-Vous-l-IA/. Chaque livraison comprend code + `SUIVI_PROJET.md`, `ROADMAP.md`, `CHANGELOG.md` et ce guide lorsque pertinent.

Le workflow `.github/workflows/pages.yml` publie le frontend sous `/A-Vous-l-IA/` avec `VITE_API_URL` ciblant le backend Azure. Un push de changements frontend sur `main` déclenche Pages ; un changement backend/documentation seul ne le déclenche pas (déclenchement manuel disponible). Ce workflow ne met pas à jour le backend Azure. Après une livraison, distinguer version backend, version Pages et état des pages parcours ; contrôler le site GitHub Pages lui-même, pas seulement le frontend Container Apps.

Le rattrapage Pages est publié par le commit `4033e8e` (workflow34461697021 réussi, CI34461697054 réussie). Les tests de gabarits nécessitant le dépôt parcours associé sont explicitement ignorés sur le checkout CI isolé : ce succès n'atteste pas une régénération de parcours. Le package Simplon demeure différé.

**Status:** Integration preparation (2026-09-12); Simplon package deferred

**Target:** Existing development environment; official production release not engaged
**Audience:** Simplon DevOps / Backend Team

## Addendum du 9 septembre 2026 — préparation locale, pas encore une livraison

### Livraison limitée DEV du 10 septembre — pas un package Simplon

Eneric a autorisé le déploiement sur les ressources de développement existantes. Backend final0045, frontend0023 ; images et preuves dans `SUIVI_PROJET.md`. Les notes de préparation locale précédentes ne doivent pas être interprétées comme l'état actuel du chatbot dev.

Pour préserver exactement la base et les pages alors déployées, la recette `backend/Dockerfile.dev-code-only` hérite d'une image existante **par digest** et copie seulement deux fichiers Python. Le contexte de build utilisé contenait uniquement cette recette (nommée Dockerfile), `app/haystack_rag.py` et `app/routes/chat.py`. Aucun Excel, secret ou mapping n'y a été ajouté. La base immuable utilisée est :

```text
acravoulia97186.azurecr.io/avoulia-backend@sha256:9d885637d00ded89af891807e0173e1772dc513d9ec1ee6a0a82b87ae6894b8a
```

Exemple de commande de build, depuis ce contexte minimal, après validation et confirmation de la cible :

```powershell
az acr build --registry acravoulia97186 --subscription "<abonnement-dev>" --image avoulia-backend:<nouveau-tag> --build-arg "BASE_IMAGE=acravoulia97186.azurecr.io/avoulia-backend@sha256:9d885637d00ded89af891807e0173e1772dc513d9ec1ee6a0a82b87ae6894b8a" --file Dockerfile --no-logs .
```

Le frontend a été construit avec son Dockerfile existant, et les applications mises à jour par `az containerapp update --image`, sans modification de leurs variables/secrets. Pour une future mise à jour, ne pas appliquer cette recette aveuglément : comparer dépendances, modules importés et modifications déjà en ligne, vérifier la base de départ et relever les images de rollback. Cette recette de dev **n'est pas la procédure finale Simplon**.

Rollback du lot : réaffecter l'image backend `v2-parcoursfix3-1788183296` et/ou frontend `v2-cfg-1788165520` sur les mêmes ressources, puis vérifier santé et trafic. Ne pas supprimer les ressources ni tourner le sel. Les modifications de gabarits CHAT-04/05/06 ne sont pas livrées : leur future intégration reste soumise au rapprochement des sources et mappings indiqué ci-dessous.

### Évaluation de pertinence ajoutée le 10 septembre (outil indépendant du packaging)

Depuis `backend`, exécuter `python scripts\evaluate_chat_relevance.py` pour préparer les scénarios sans réseau. La suite `python -B -m unittest discover -s tests -q` couvre aussi le banc ; elle n'appelle pas Azure.

Pour une évaluation réelle explicitement autorisée, utiliser un chemin JSON privé nouveau et une cible explicite :

```powershell
python scripts\evaluate_chat_relevance.py --live --subscription "<abonnement>" --resource-group "<groupe>" --container-app "<application>" --scenario zero-match --scenario synonyms-zero-keyword-overlap --repeats 2 --max-completion-tokens 6000 --interval-seconds 90 --output "<chemin-prive-nouveau.json>"
```

Cela consomme des tokens sur la ressource existante ; maximum 16 tentatives par campagne (4 pour la commande ci-dessus), aucune modification de ressource ou déploiement. L'authentification par jeton CLI est utilisée par défaut, sans bascule silencieuse vers une clé. Le plafond inclut raisonnement ET sortie ; le plafond initial de 1 200 a tronqué plusieurs réponses et ne permettait pas de conclure. Ne pas confondre une réponse tronquée, une liste non reconnue et une erreur de pertinence.

Les rapports bruts du 10 septembre sont privés et synthétiques, non des données de production. Le verdict strict n'est pas un taux de précision utilisateurs. Les questions de suivi numérotées peuvent déclencher le diagnostic strict de parsing ; lire la réponse brute avant de conclure. Ne pas changer les attentes d'un rapport déjà exécuté ni publier un résultat favorable en ignorant ses limites.

**Report explicite à 15:41** : Eneric demande de ne pas préparer ni assembler le package Simplon à ce stade. Ce guide conserve les exigences et précautions pour une reprise ultérieure ; il ne constitue pas un ordre de packaging ou de déploiement. Les travaux courants reprennent sur les corrections restantes et leur documentation.

**Contrat de liste à préserver lors de la future reprise** : niveau 1 peut omettre des candidats périphériques. Le rapprochement serveur (`_reconcile_generated_case_list`, utilisé par les chemins HTTP/SSE) doit rester actif : mêmes cas, même ordre, mêmes IDs et sources entre texte affiché et sélection. Les numéros Markdown en gras, blocs inconnus, doublons et titres ambigus sont couverts par `backend/tests/test_chat_relevance.py`. Ne pas remplacer cette vérification d'identité par un simple compte des éléments. Ce contrôle ne mesure pas la pertinence sémantique ; le détail verbatim conserve son chemin distinct.

Les instructions et statuts historiques ci-dessous ne valent pas validation de la future livraison de septembre. Le périmètre est limité aux corrections du chatbot et aux colonnes Excel existantes, sans pivot.

**Sources de génération à distinguer impérativement :**
- Le gabarit des six étapes actuellement observées est `templates/page.html.j2` du dépôt `avoulia-parcours`, généré par son `pipeline/genere.py`.
- Le script `backend/scripts/generate_parcours_pages.py` embarque un ancien gabarit ; ne pas l'exécuter pour publier les corrections UX de septembre.
- Le générateur parcours produit `dist/action/<hash>/index.html`, alors que le backend observé sert `app/static/parcours/action-<hash>.html`. Les contrats de mapping, de sel et de liens de retour doivent être rapprochés avant toute régénération destinée au backend. Ne pas copier aveuglément un dossier `dist` sur les pages servies ; ne pas modifier celles-ci manuellement.
- Préserver le classeur source et les mappings ; les corrections Excel nécessitent un nouveau fichier versionné et un journal. Les arbitrages éditoriaux sont désormais délégués par Eneric ; le choix de publication reste distinct. Ne pas régénérer depuis une vieille v453 par défaut.

**Contrôles locaux disponibles :** depuis `backend`, lancer `python -m unittest discover -s tests`. Les tests de gabarit `test_parcours_ux.py` utilisent des cas fictifs, sans lecture de classeur ; définir `PARCOURS_SOURCE_ROOT` vers le dépôt parcours si nécessaire (sinon cette classe de tests est explicitement ignorée). Vérifier que les tests de gabarit ne sont pas ignorés avant de conclure sur la cohérence des deux sources.

**Avant livraison** : aligner sources et correctifs précédemment déployés, régénérer avec le mapping approuvé, conserver les liens de retour/configuration d'environnement, contrôler ID → cas → URL → bonne page et l'ordre des six étapes, puis seulement préparer la publication et le retour arrière. Aucun de ces changements locaux n'est encore en ligne.

> **Documents de référence (onboarding v1 → v2) :**
> [`CHANGELOG.md`](./CHANGELOG.md) (**synthèse v1 → v2 — commencer ici**) ·
> [`ROADMAP.md`](./ROADMAP.md) (évolutions prévues & priorités) ·
> [`SUIVI_PROJET.md`](./SUIVI_PROJET.md) (journal chronologique des correctifs) ·
> [`README.md`](./README.md) (install & lancement local). Un dev Simplon ayant fait la v1
> doit lire ces fichiers + ce guide pour comprendre tout ce qui a changé depuis la v1.

---

## 📋 Overview

Avoulia V2 adds **parcours pages** (guided implementation steps) + **real-time telemetry** to the existing RAG chatbot system. When a PME asks a question:

1. **Backend** returns RAG response + **parcours URL** (`/action/<hash>/`)
2. **Frontend** displays URL to PME
3. **PME clicks** → Opens parcours page (tracks: validation, 6 steps, quickwin)
4. **App Insights** records full funnel: chat → RAG → parcours → step completion
5. **Dashboard (Workbook)** shows: funnel %, top cases, retention, bounce rate

---

## 🚀 Implementation Steps (Production Ready)

### Phase 1: Azure Infrastructure (Bicep)

**Files to use:**
- `infra/main.bicep` — IaC template (App Insights, Log Analytics, Storage)
- `config/environments/prod.officiel.sample.json` — Production parameters template

**Steps:**

1. **Prepare environment config:**
   ```bash
   # Copy template and fill production values
   cp config/environments/prod.officiel.sample.json config/environments/prod.officiel.json
   
   # Edit prod.officiel.json:
   # - resourceGroup: rg-avoulia-fr-prod
   # - region: westeurope
   # - subscription: <your-prod-subscription-id>
   # - appInsights name: ai-avoulia-prod
   # - storage account: stavouliafr4prod (must be globally unique)
   ```

2. **Deploy Bicep to Production:**
   ```bash
   az group create \
     --name rg-avoulia-fr-prod \
     --location westeurope
   
   az deployment group create \
     --resource-group rg-avoulia-fr-prod \
     --template-file infra/main.bicep \
     --parameters @config/environments/prod.officiel.json
   ```

3. **Capture Outputs:**
   After deployment succeeds, capture these values (you'll need them):
   ```bash
   az deployment group show \
     --resource-group rg-avoulia-fr-prod \
     --name main \
     --query "properties.outputs" > outputs.json
   
   # Extract and store in GitHub Secrets:
   # - APPINSIGHTS_INSTRUMENTATION_KEY_PROD (from outputs.appInsightsKey)
   # - APPINSIGHTS_CONNECTION_STRING_PROD (from outputs.appInsightsConnectionString)
   # - STORAGE_ACCOUNT_NAME_PROD (from outputs.storageAccountName)
   # - STORAGE_ACCOUNT_KEY_PROD (from outputs.storageAccountKey)
   ```

---

### Phase 2: Backend Enhancement (Chantier E)

**File to modify:**
- `backend/app/routes/chat.py` (or your main chat endpoint)

**Changes:**

1. **Add parcours URL generation to chat endpoint:**
   - Reference: `backend/CHANTIER_E_BACKEND_ENDPOINT.py` (template provided)
   - Implement `generate_case_hash(case_id, salt)` function
   - Update chat response to include:
     ```python
     {
       "answer": "...",  # RAG response (Q2 + Q3 text)
       "case_id": "UC-0042",
       "case_hash": "vn38reuyw7",
       "parcours_url": "https://avoulia.azurewebsites.net/action/vn38reuyw7/",
       "matching_score": 0.92,
       ...
     }
     ```

2. **Environment variables (set in Container Apps):**
   ```
   AVOULIA_SALT = "prod-salt-value-NEVER-rotate-in-prod"
   PARCOURS_BASE_URL = "https://avoulia.azurewebsites.net"
   APPINSIGHTS_INSTRUMENTATION_KEY = <from Bicep outputs>
   ```

3. **Test locally:**
   ```bash
   export AVOULIA_SALT="test-salt-123"
   export PARCOURS_BASE_URL="http://localhost:5173"
   python -m pytest tests/test_chat_endpoint.py -v
   ```

---

### Phase 3: Frontend Integration (Chantier C)

**Files to modify:**
- `frontend/src/main.ts` — Initialize App Insights on load
- `frontend/index.html` — Add telemetry snippet to `<head>`
- `frontend/src/components/ChatMessage.vue` — Track user messages + RAG hits
- `frontend/src/components/ParcoursPage.vue` — Track step completion (if exists)

**Changes:**

1. **Add App Insights snippet:**
   Reference: `frontend/src/appinsights-instrumentation.html`
   
   Copy the script into `frontend/src/appinsights.ts`:
   ```typescript
   // frontend/src/appinsights.ts
   
   export const appInsights = {
     sessionId: getSessionId(),
     
     trackChatSessionStart: () => { /* ... */ },
     trackUserMessage: (msg) => { /* ... */ },
     trackRagResult: (caseId, score) => { /* ... */ },
     trackParcoursUrlProposed: (url) => { /* ... */ },
     // ... other methods
   };
   ```

2. **Track user message in chat component:**
   ```vue
   <!-- frontend/src/components/ChatMessage.vue -->
   <script setup>
   import { appInsights } from '@/appinsights';
   
   const sendMessage = async () => {
     appInsights.trackUserMessage(messageText, 'pme_question');
     const response = await fetchFromBackend(messageText);
     appInsights.trackRagResult(response.case_id, response.matching_score);
     if (response.parcours_url) {
       appInsights.trackParcoursUrlProposed(response.parcours_url, response.case_hash);
     }
   }
   </script>
   ```

3. **Environment variables (build time):**
   Set `VITE_APPINSIGHTS_KEY` in GitHub Secrets → injected by CI/CD

---

### Phase 4: Parcours Pages (Chantier B — Reference)

**Reference files:**
- `templates/page.html.j2` — Jinja2 template for parcours pages
- `frontend/src/appinsights-instrumentation.html` — Telemetry integration

**Architecture:**
- Pages can be **static** (pre-generated) or **dynamic** (server-rendered)
- Each page has a unique `<body data-case-hash="UC-0042">` attribute
- Telemetry auto-tracks step completion when checkboxes are marked

**Quick checklist:**
- [ ] Étape 1 (validation) at top (appears expanded by default)
- [ ] Transition message "✓ OK, c'est pour vous" visible
- [ ] Étapes 2-6 collapsed below
- [ ] Quick win accordion at bottom (closed by default)
- [ ] App Insights events fire on step/quickwin interactions

---

### Phase 5: Dashboard & Monitoring (Chantier D)

**Files:**
- `infra/kql-queries.kql` — Pre-written KQL queries
- `infra/dashboards/avoulia-parcours-dashboard.json` — Workbook JSON

**Setup:**

1. **Import Workbook to Azure Portal:**
   ```bash
   az monitor workbooks create \
     --resource-group rg-avoulia-fr-prod \
     --definition @infra/dashboards/avoulia-parcours-dashboard.json \
     --name avoulia-parcours-dashboard
   ```

2. **Verify KQL Queries Work:**
   - Go to: Azure Monitor → Logs
   - Paste each query from `infra/kql-queries.kql`
   - Verify data flows (after 5-10 min of traffic)

3. **Dashboard Metrics Tracked:**
   - **Funnel:** chat_start → RAG_hit → parcours_opened → step_completion
   - **Top Cases:** Most-visited parcours pages
   - **Quickwin Rate:** % of users who copied quick solution
   - **Retention:** J+1, J+3, J+7 re-engagement
   - **Bounce Rate:** Chat sessions with no RAG result
   - **Timeline:** Event volume per hour

---

## 🔧 Configuration Reference

### Environment Variables (Prod)

| Variable | Value | Source |
|---|---|---|
| `AVOULIA_SALT` | `prod-salt-...` (fixed) | Set in Container Apps secret |
| `PARCOURS_BASE_URL` | `https://avoulia.azurewebsites.net` | Hardcode in backend config |
| `APPINSIGHTS_INSTRUMENTATION_KEY` | From Bicep output | GitHub Secret → CI/CD |
| `APPINSIGHTS_CONNECTION_STRING` | From Bicep output | For SDK initialization |
| `STORAGE_ACCOUNT_NAME` | `stavouliafr4prod` | From Bicep output |
| `STORAGE_ACCOUNT_KEY` | From Bicep output | For mapping CSV access |

### Storage (Mapping CSV)

The backend can optionally load `mapping_uc_hash.csv` from Blob Storage:
```
Storage Account: stavouliafr4prod
Container: parcours-mappings
File: mapping_uc_hash.csv

Format:
case_id,case_hash
UC-0001,vn38reuyw7
UC-0002,kx92mnopq3
...
```

If not using dynamic mapping, case hashes are generated deterministically via `AVOULIA_SALT`.

---

## ✅ Validation Checklist (Before Go-Live)

### Backend
- [ ] Chat endpoint returns `parcours_url` field
- [ ] `case_hash` is deterministic (same input → same hash)
- [ ] Environment variables are set correctly
- [ ] Local test: `curl http://localhost:8000/api/v1/chat -X POST -d '{"message": "test"}'` returns URL

### Frontend
- [ ] Chat page loads without errors
- [ ] Telemetry events appear in browser DevTools → Network → App Insights calls
- [ ] User message + RAG result trigger events
- [ ] Parcours URL is clickable in response

### Parcours Page
- [ ] Page loads (HTTP 200)
- [ ] Headers include `X-Robots-Tag: noindex, nofollow, noarchive` + meta noindex
- [ ] Étape 1 validation appears first
- [ ] Steps track completion (check DevTools Console for event logs)
- [ ] Quickwin accordion is collapsible

### App Insights
- [ ] Bicep deployment succeeded (all resources created)
- [ ] Data flows in: `customEvents` table populated
- [ ] KQL queries return non-zero results
- [ ] Workbook dashboard loads without errors
- [ ] Funnel metrics make sense (each step < previous)

---

## 🩹 Known Issues Fixed (2026-08-25) — Read Before Modifying `haystack_rag.py`

Two related bugs were found and fixed in the RAG retrieval/qualification pipeline (`backend/app/haystack_rag.py`). **Both share the same root cause pattern**, and it's important Simplon's team understands it before touching this file, to avoid reintroducing it.

**Symptoms observed:**
1. When a user selected a specific marketing objective (e.g. "Créer des contenus marketing"), the reformulation examples (Q3) and some suggested cases actually belonged to *other* marketing objectives (acquisition, market analysis, campaigns, etc.) — an intention mismatch.
2. The bot displayed up to 5 numbered use cases, but rejected the user's selection of case 4 or 5 ("Le choix « 4 » n'est pas disponible... 1, 2 ou 3") — meaning fewer real cases were actually retrieved than were shown in the text.

**Root cause (anti-pattern):** several places in the retrieval pipeline had a "graceful fallback" of the form `filtered_docs if filtered_docs else all_domain_docs` (or literally dropping the `intention` filter condition) to avoid returning an empty result when the strict filter (`domaine` + `intention` + `secteur`) matched too few documents. This silently reintroduced off-topic documents from *other* intentions into the pool. Separately, the RAG prompt hard-coded a "minimum 3 cases" instruction with no guarantee that 3 real documents existed, which caused the LLM to invent extra cases to satisfy the minimum — explaining the gap between displayed cases and selectable `suggested_case_ids`.

**Fix applied:**
- `build_pool()`: removed the `docs = filtered if filtered else docs` fallback — now returns an empty list rather than mixing intentions.
- `_retrieve_docs_for_question()`: reordered the fallback cascade so the `intention` filter is **never dropped** (domain+intention+secteur → domain+intention+secteur-élargi → domain+intention only, with sector applied as a Python post-filter).
- `RAG_PROMPT`: replaced "Minimum 3 cas / Maximum 5 cas" with an absolute anti-hallucination rule — never present more cases than actually provided, never pad below 3 with invented ones.
- `_build_rag_prompt_from_docs()`: removed a dead code branch that implied (but never enforced) a minimum-3 display rule.
- Added 3 regression tests in `backend/tests/test_haystack_rag.py` (the file now has 11 tests, all passing).
- Deployed to `avoulia-backend` (revision `avoulia-backend--0000023`) in `rg-avoulia-fr-dev`.

**⚠️ Guidance for future changes:** if you see a similar "no results, so fall back to something broader" pattern anywhere else in `haystack_rag.py`, treat it as a code smell — prefer returning an empty/partial result (and letting the LLM say "no matching case found") over silently mixing categories. See `SUIVI_PROJET.md`, entry "Update 2026-08-25 — Fix filtrage RAG", for full detail.

---

## 🔗 Parcours Link CTA (2026-08-25) — Single Source of Truth for Button/Text Wording

The parcours link is **no longer shown as raw text** requiring copy-paste — the frontend (`ChatView.vue`) renders it as a clickable button (`SuggestedCase.parcours_url`).

The text/label around it (step count, duration, CTA wording) is **not hardcoded in multiple places**. It all comes from one function: `backend/app/parcours_util.get_parcours_pitch()`, driven by two constants:
- `PARCOURS_STEPS_COUNT` (currently 6)
- `PARCOURS_ACTIVE_MINUTES` (currently 132, i.e. sum of the fixed-duration steps in `generate_parcours_pages.py`, excluding the open-ended "test during your week" step)

Both `routes/chat.py` and `haystack_rag.py` call this function for the chat message text, and `models.SuggestedCase.parcours_cta_label` propagates the same computed button label to the frontend — so text and button are always in sync.

**If the parcours page template changes** (more/fewer steps, different durations), update only the two constants in `parcours_util.py`. Do not hardcode new wording anywhere else — that would defeat the purpose of this single source of truth and risks the button/text drifting out of sync again.

---

## 🎯 Parcours CTA — Backend Is Authoritative (2026-08-26)

**Do not let the frontend guess which case was selected.** On any case-detail
response, the backend (`get_rag_prompt_and_sources`) returns the selected case's
`parcours_url` and `parcours_cta_label` as **top-level fields** of the SSE `done`
payload. The frontend (`resolveParcoursCta` in **`HomeView.vue`** — the live chat
component) reads these fields **first**; the old resolution-by-id/index/typed-digit
is only a fallback.

- **Why:** previously the button was reconstructed on the frontend by matching
  `suggested_cases[index]` against the digit the user typed. That was fragile
  (affirmations like "ok", free-text detail requests, uncaught numbers) and often
  produced a missing button even though the message said "click the button below".
- **Backend:** `_ret_niveau2(payload, selected_id=...)` computes the URL/label via
  `build_parcours_info(selected_id)` and appends them to the returned tuple, which
  `routes/chat.py` puts into `done_payload["parcours_url"] / ["parcours_cta_label"]`.
- **Rule for future changes:** the selected-case parcours button must stay
  **backend-driven**. Never reintroduce index-based guessing as the primary path.
  (A digit-based fallback was removed on 2026-08-26 because it made the button
  appear during the Q1.5/Q2/Q3 questions whenever the user answered with a digit.)

## 🧩 Haystack Chat Generator API (2026-08-26)

The installed Haystack exposes **chat** generators only:
`AzureOpenAIChatGenerator` / `OpenAIChatGenerator` (built via
`ChatPromptBuilder` + `ChatMessage`, connected on `generator.messages`). The old
`AzureOpenAIGenerator` / `OpenAIGenerator` (text-completion) no longer exist and
importing them crashes at runtime.

Replies are `ChatMessage` objects whose text is accessed via **`.text`** (not the
old `.content`). Always extract text through the helper `_reply_to_text()` in
`haystack_rag.py` — it handles `.text`, legacy `.content`, and plain strings.
Calling `.strip()` directly on a reply crashes with
`'ChatMessage' object has no attribute 'strip'`.

---

## 📊 Usage Stats — Integrated `/stats` Page (2026-08-27)

Simple, **self-contained** usage tracking — no external product, no separate repo, no dashboard
service (constraint C1). Answers "which roles/problems/cases are most visited?".

- **Where to look:** open **`/stats`** on the backend (e.g.
  `https://<backend-host>/stats`) — server-rendered HTML listing top **domaines (roles)**,
  **problématiques (Q3)**, **cas d'usage consultés**, and total **clics bouton parcours**
  (the key conversion). JSON at **`/api/v1/stats.json`**.
- **How it records:** `backend/app/stats.py`. Each event is appended to an **Azure append blob**
  (`stats/events.jsonl`) when `STORAGE_ACCOUNT_NAME` / `STORAGE_ACCOUNT_KEY` are set; otherwise it
  falls back to **in-memory** (resets on restart). The append blob is created on first event.
- **Wiring (already done in dev):**
  ```bash
  KEY=$(az storage account keys list -n stavoulia97186 -g rg-avoulia-fr-dev --query "[0].value" -o tsv)
  az containerapp update -n avoulia-backend -g rg-avoulia-fr-dev \
    --set-env-vars STORAGE_ACCOUNT_NAME=stavoulia97186 STORAGE_ACCOUNT_KEY="$KEY"
  ```
  Without these env vars the app still works (memory fallback); with them stats survive restarts.
- **Recording points:** domaine (at selection) + problème (free-text Q3 that yields the case list)
  in `routes/chat.py::_record_usage_stats`; cas (when the verbatim card opens) in
  `haystack_rag.py::stats.record("cas", …)`; parcours_click via `POST /api/v1/chat/parcours-click`
  called fire-and-forget by the frontend (`chat.ts::trackParcoursClick`, wired in
  `HomeView.vue::onParcoursClick`).
- **Reset:** delete the blob to start clean —
  `az storage blob delete --account-name stavoulia97186 --account-key "$KEY" --container-name stats --name events.jsonl`.
- **Compatible with the future single-container packaging** (no new infra; FastAPI serves `/stats`).

### Case feedback 👍/👎 (Axe 3.2)
- Below each case card, two buttons ask "Ce cas vous semble-t-il pertinent ?". A click posts to
  **`POST /api/v1/chat/feedback`** (`{useful: bool, case_label}`) which records `feedback_up` /
  `feedback_down` with the case's **verbatim title** (`cas_utilisation`). One vote per card, then a
  thank-you replaces the buttons.
- The `/stats` page shows a **satisfaction KPI** (`N👍 / M👎`) plus two rankings: cases rated useful
  and cases rated not-relevant — a quality signal to prioritise improving the use-case base.
- Frontend: `chat.ts::sendCaseFeedback` (fire-and-forget), wired in `HomeView.vue::onCaseFeedback`.
  The clean label comes from `suggested_cases[].cas_utilisation` (already in the SSE payload), NOT
  the raw `content` (which is the pipe-delimited rag_text).

---

## 🔁 Lien "Retour à Avoulia" sur les pages parcours (Axe 3.4, 2026-08-31)

Chaque page parcours (`backend/app/static/parcours/action-*.html`, servie par le backend, ouverte
dans un nouvel onglet) contient un lien **« ← Retour à Avoulia »** (en tête + rappel en pied) vers
l'app chat, pour relancer l'exploration au lieu de laisser l'utilisateur dans un cul-de-sac.

**⚠️ Important :** ces liens sont **injectés** dans les fichiers statiques par
`backend/scripts/add_backlink_parcours.py`, PAS par le générateur. Raison : les pages servies
utilisent un template abouti dont le générateur canonique n'est pas `generate_parcours_pages.py`
(ce dernier produit un template plus ancien — **ne pas l'utiliser pour régénérer**, cela écraserait
le design actuel). Le script est **idempotent** (marqueur `id="avoulia-back"`).

**Si les pages sont un jour régénérées** (nouveau lot depuis l'Excel) : relancer
`python scripts/add_backlink_parcours.py` (depuis `backend/`) pour réinjecter les liens. L'URL de
l'app vient de `AVOULIA_APP_URL` (défaut = front Container App) — cohérent avec l'Axe 4.5.

---

## 🔧 URL backend = variable unique (Axe 4.5, 2026-08-31)

Pour héberger ailleurs (reprise Simplon), **une seule variable par composant** suffit — plus aucune
URL codée en dur à traquer :

| Composant | Variable | Où | Défaut |
|---|---|---|---|
| Backend (génère les liens parcours) | `PARCOURS_BASE_URL` | `config.py` → `parcours_base_url`, lue par `parcours_util._parcours_base_url()` | URL Container App backend |
| Frontend (proxy nginx `/api/`) | `BACKEND_ORIGIN` | `nginx.conf.template` (`${BACKEND_ORIGIN}`), défaut dans `frontend/Dockerfile` | URL Container App backend |
| Vitrine GitHub Pages (build Vite) | `BACKEND_ORIGIN` | `.github/workflows/pages.yml` (`env`) → `VITE_API_URL` | idem |
| Smoke test | `SMOKE_BASE_URL` / `PARCOURS_BASE_URL` | `smoke-test.mjs` | idem |

**Frontend — comment ça marche :** `nginx.conf.template` est monté dans `/etc/nginx/templates/` ;
l'entrypoint officiel de l'image nginx exécute `envsubst` au démarrage et ne substitue que les
variables **définies dans l'environnement** (donc `${BACKEND_ORIGIN}`), en préservant les variables
nginx (`$uri`, `$scheme`, `$proxy_host`…). Le Host de l'upstream est dérivé via `$proxy_host` (pas de
2ᵉ variable). Pour changer de backend : `az containerapp update -n avoulia-frontend -g rg-avoulia-fr-dev
--set-env-vars BACKEND_ORIGIN=https://mon-backend...` (ou éditer le défaut du Dockerfile).

**Backend — comment ça marche :** `PARCOURS_BASE_URL` (env) est lue via `get_settings().parcours_base_url`.
Pour changer : `az containerapp update -n avoulia-backend -g rg-avoulia-fr-dev --set-env-vars
PARCOURS_BASE_URL=https://mon-backend...`.

---

## ⚙️ CI/CD & déploiement (2026-08-31)

**CI (automatique, sans secret) —** `.github/workflows/ci.yml` tourne à chaque push/PR sur `main` :
- **backend** : `pip install -r requirements.txt` → `python -m compileall app` → `python -m unittest`.
- **frontend** : `npm ci` → `npm run type-check` → `npm run check:dead` → `npm run build-only`
  (+ lint informatif, `continue-on-error`).

Cette CI **ne déploie rien** — c'est un garde-fou : si le code ne compile pas, qu'un test casse ou
qu'un composant Vue est mort, la CI passe au rouge **avant** tout déploiement.

**Détection de code mort —** `frontend/scripts/check-dead-code.mjs` (`npm run check:dead`) échoue si
un `.vue` de `src/` n'est importé nulle part (exception : `App.vue`). Objectif : ne plus jamais
rééditer un fichier fantôme (le bug `ChatView.vue` a coûté cher). Le scaffolding Vite mort
(HelloWorld / TheWelcome / WelcomeItem / `icons/*`) a été supprimé.

**Déploiement (aujourd'hui, manuel) —** build ACR + update Container App :
```bash
# Backend (toujours avec CACHEBUST pour éviter la couche COPY en cache)
az acr build --registry acravoulia97186 --image avoulia-backend:<tag> \
  --build-arg CACHEBUST=$(date +%s) backend/
az containerapp update -n avoulia-backend -g rg-avoulia-fr-dev \
  --image acravoulia97186.azurecr.io/avoulia-backend:<tag>
# Frontend (idem sans CACHEBUST)
az acr build --registry acravoulia97186 --image avoulia-frontend:<tag> frontend/
az containerapp update -n avoulia-frontend -g rg-avoulia-fr-dev \
  --image acravoulia97186.azurecr.io/avoulia-frontend:<tag>
```
**Pour ajouter le CD (déploiement auto) plus tard :** créer un service principal / OIDC côté tenant
Simplon, stocker les identifiants en **secrets GitHub**, et ajouter un job `deploy` (needs: [backend,
frontend]) qui rejoue les commandes ci-dessus puis `node smoke-test.mjs`. Volontairement **non
branché ici** car les identifiants sont spécifiques au tenant d'hébergement (Simplon).

**GitHub Pages —** `.github/workflows/pages.yml` publie le frontend statique sur Pages (vitrine) ;
distinct du déploiement applicatif sur Container Apps.

---

## 🐛 Troubleshooting

| Issue | Solution |
|---|---|
| Bicep deployment fails | Check Azure CLI auth + RG exists + correct parameters |
| No telemetry data | Verify `APPINSIGHTS_INSTRUMENTATION_KEY` is valid; check browser console for JS errors |
| Parcours URL always 404 | Verify `AVOULIA_SALT` matches prod environment; check hash generation logic |
| Dashboard shows no data | Wait 5-10 min for events to flow; check KQL query syntax in Logs |
| App Insights quota exceeded | Check data retention settings (prod = 90 days); consider sampling rate |
| Cases from wrong intention appear, or fewer selectable cases than displayed | See "Known Issues Fixed (2026-08-25)" above — check for a silent fallback reintroducing off-topic docs in `haystack_rag.py` |
| Parcours button missing after selecting a case | Backend must send top-level `parcours_url` in the `done` payload — see "Parcours CTA — Backend Is Authoritative (2026-08-26)". Don't rely on frontend index matching |
| `'ChatMessage' object has no attribute 'strip'` | Extract reply text via `_reply_to_text()`; the Haystack chat API returns `ChatMessage` (text via `.text`) — see "Haystack Chat Generator API (2026-08-26)" |
| Duplicated `🚀 Passez à l'action` block after case selection | The parcours pitch was appended twice. Both append sites are now idempotent via `PARCOURS_PITCH_SENTINEL` (`parcours_util.py`) |
| A code fix is in the deployed `.py` (confirmed by `grep` in the container) but prod still shows the OLD behavior | **Stale Python bytecode.** Old `__pycache__/*.pyc` (even from a different Python version, e.g. a dev machine's `cpython-314.pyc`) shipped in the image and ran instead of the up-to-date source. The `backend/Dockerfile` now purges `__pycache__` after `COPY app` and sets `PYTHONDONTWRITEBYTECODE=1`. Never copy/commit `__pycache__` into the build context |
| The deployed `.py` ITSELF is stale (grep in the container shows old source, though the local file is up to date) | **Cached `COPY` layer in the ACR build.** `backend/Dockerfile` has `ARG CACHEBUST` before `COPY app`; always build with `--build-arg CACHEBUST=$(date +%s)` (or the image tag / git commit) so the code copy is redone from scratch |
| A frontend change doesn't appear in the built bundle (same JS hash every build) | The edited component may be **dead code** (not imported anywhere) and tree-shaken out. The live chat UI is **`frontend/src/views/HomeView.vue`**, NOT `ChatView.vue` (deleted). Verify with `grep -r ComponentName src/`. Edit `HomeView.vue` for chat/CTA changes |
| Users don't see a new deployment (old JS keeps loading) | `index.html` must be served `no-cache` so browsers re-fetch it and pick up the new content-hashed assets. See `frontend/nginx.conf.template` (`location = /index.html`) |
| `/stats` is empty or resets on restart | The stats append blob isn't configured — set `STORAGE_ACCOUNT_NAME` / `STORAGE_ACCOUNT_KEY` env vars on the backend container app (see "Usage Stats" section). Without them, stats use an in-memory fallback that resets on each restart |


---

## 📞 Contact & Support

**Questions about V2 implementation?**
- Review files in `infra/` and `backend/` directories
- Check `SUIVI_PROJET.md` for decisions and architecture notes
- Reference template implementations in `CHANTIER_*.py` files

**Critical constraints:**
- ⚠️ **AVOULIA_SALT must never rotate in production** (all hashes depend on it)
- ⚠️ **Case IDs must be verbatim from Excel** (no reformulation by LLM)
- ⚠️ **Parcours pages must be non-indexed** (`X-Robots-Tag: noindex`)

---

**Last Updated:** 2026-07-10  
**Prepared by:** Eneric (with Copilot)
