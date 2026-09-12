# Avoulia V2 — Suivi Projet & Décisions

### 12 septembre 2026 — base consolidée, intégration applicative engagée

**État faisant foi :** la nouvelle version du classeur privé est sauvegardée après revue du catalogue et corrections tracées. Aucun de ses contenus, journaux ou exports n'est ajouté au dépôt public. La base sauvegardée n'est pas la preuve d'une version indexée ou déployée.

- **Décisions :** arbitrages éditoriaux et de classement délégués par Eneric ; demande à 15:25 de poursuivre l'intégration et de tester à chaque étape. Catalogue, IDs, colonnes existantes, pré-filtrage, détail verbatim et six étapes conservés.
- **Défaut d'intégration identifié :** `app/services/ingest.py` et le générateur parcours lisent actuellement la première feuille. Un onglet d'audit placé avant les données peut donc être ingéré à tort. Le classeur consolidé place le catalogue en tête ; le code doit aussi sélectionner et valider la feuille explicitement.
- **Secteurs :** certains rattachements métier légitimes ne figurent pas dans les menus statiques. La correction doit rendre ces choix accessibles à partir des métadonnées, sans changer les données pour contourner le filtre et sans casser l'ordre des choix existants.
- **Suite ordonnée :** INT-01 import/secteurs et tests synthétiques ; INT-02 génération explicite et rapprochement source/index/mapping/pages ; INT-03 recette et livraison dev après les contrôles de cible, confidentialité et publication. État détaillé dans `ROADMAP.md`.
- **Toujours en ligne selon le dernier relevé :** backend0045, frontend0023 et Pages du 10 septembre. Aucun nouveau contrôle cloud effectué dans cette mise à jour documentaire.
- **Hors lot :** package Simplon différé, pas de production officielle, pas de publication de la base sur GitHub, pas de nouvel outil de télémétrie.

Les entrées datées ci-dessous décrivent leur état au moment du lot ; elles ne remplacent pas ce statut courant.

**Clôture de la préparation locale INT-01/02 :**

- `backend/app/services/ingest.py` sélectionne `Sheet1` ou un unique catalogue historique non ambigu, exclut les colonnes de travail et conserve les métadonnées métier. IDs vides/dupliqués après normalisation, erreurs Excel et caches de formules manquants sont refusés ; les loaders sont fermés en cas d'erreur.
- `backend/app/haystack_rag.py` complète les secteurs depuis les métadonnées sans changer les numéros historiques, y compris « Autre ». Le rejeu utilise les libellés effectivement affichés, y compris en Markdown. Le cache est invalidé lors des écritures/effacements et borné dans le temps ; une lecture en échec n'est pas masquée.
- L'indexation dispose d'un précontrôle sans réseau et d'une option de collection vide ; aucun effacement automatique lors d'un conflit de dimension d'embeddings. Le démarrage échoue explicitement si l'index ne peut pas être lu ou construit.
- Le générateur du dépôt parcours associé utilise source/mapping/destination explicites, conserve les hashes et refuse les remplacements implicites. Le lien de retour est paramétrable ; son workflow devient manuel, sans export du mapping dans le répertoire public.
- **Tests finaux locaux :** 182 backend/générateur, 19 frontend et typecheck réussis. Passage sur le catalogue réel en mémoire : import, secteurs, pré-filtres, rendu des six étapes, champs verbatim et URLs rapprochés ; source et mapping inchangés, aucune page persistée ni requête embeddings.
- **Limites :** Python local 3.14 avec avertissement de compatibilité Pydantic-v1, pas le runtime 3.11 de l'image ; aucun nouvel index Chroma réel ni test de modèle réel dans ce lot. Publication GitHub et Azure non exécutées ; préparation locale ne vaut pas recette dev.

### Publication GitHub Pages clôturée le 10 septembre 2026

- **Commit livré** : [`4033e8e`](https://github.com/NricL/A-Vous-l-IA/commit/4033e8e03a60346be855c3f6cac8c3d69bf02ce2), code, tests, workflows et documentation nettoyée, dans `main`.
- **Lien de référence à jour** : https://nricl.github.io/A-Vous-l-IA/ ; bundle observé `index-CHHXhvYM.js`, backend dev0045 inchangé.
- **Publication** : [Pages 34461697021](https://github.com/NricL/A-Vous-l-IA/actions/runs/34461697021) réussie ; [CI 34461697054](https://github.com/NricL/A-Vous-l-IA/actions/runs/34461697054) réussie. 101 tests backend en CI, une classe de gabarits ignorée faute du dépôt parcours associé, contre106 tests locaux avec ce dépôt ;19 tests frontend. Lint informatif avec défauts préexistants, non présenté comme propre ; avertissement de dépréciation des actions Node20.
- **Contrôle sur Pages lui-même** : à390px saisie et envoi visibles, libellé accessible présent ; accueil →13 →BTP →objectif →demande fiscale hors contexte →message sans correspondance →retour objectif fonctionne. Aucun chiffre extrapolé à tout le catalogue.
- **Périmètre** : aucun Excel, rapport privé, lien SharePoint interne ou nouvel export de mapping ajouté par ce commit. Le mapping historiquement suivi par Git n'a pas été modifié ; ce lot n'est pas un audit/réécriture de l'historique public.
- **Écart volontaire maintenu** : changements de gabarits CHAT-04/05/06 non déployés, pages existantes et base inchangées. Package Simplon différé. Les mentions « à publier » ci-dessous décrivent les étapes précédentes.

### Synchronisation GitHub autorisée le 10 septembre à 11:34

Eneric confirme la publication dans le dépôt **public** après nettoyage. Ce lot synchronise code, tests, workflows et documentation ; aucun Excel, rapport privé de modèle, lien SharePoint interne ou nouvel export de mapping n'est ajouté. L'identifiant d'abonnement a été retiré des fichiers publiables et doit être fourni explicitement au banc d'évaluation.

Validation locale :106 tests backend avec le dépôt parcours associé,19 tests frontend, typecheck et build au chemin `/A-Vous-l-IA/`. Dans un checkout isolé, les tests de gabarits externes sont explicitement ignorés si le dépôt associé est absent ; cela ne valide pas une régénération de parcours. Les sources `parcours_util.py` anticipent les durées harmonisées mais le backend0045 conserve son module hérité : ne pas confondre code versionné et totalité du code déployé.

Publication Pages déclenchée par le push frontend ; succès et contrôle du site seront consignés après exécution. Aucun package Simplon.

### Règle de livraison confirmée le 10 septembre à 11:20

Le dépôt `NricL/A-Vous-l-IA` et **https://nricl.github.io/A-Vous-l-IA/** sont les références d'Eneric. Chaque mise à jour doit synchroniser le code, les fichiers de suivi/roadmap/changelog/handoff et les éléments GitHub concernés, puis contrôler le résultat sur ce lien. Un déploiement Azure seul ne constitue pas une livraison complète.

**Rattrapage effectué** : frontend GitHub Pages publié par `4033e8e`, backend dev0045 et frontend Azure0023 inchangés. Les tests d'état frontend sont exécutés par CI et Pages. Le constat d'interface ancienne à11:14 est résolu par la publication documentée en tête. Package Simplon toujours différé ; aucune modification Excel.

### État final du 10 septembre — correctifs chatbot déployés sur DEV uniquement

**Livraison terminée sur l'environnement de développement confirmé par Eneric**, pas sur Simplon/avouslia.fr : `rg-avoulia-fr-dev`, `francecentral`. L'identifiant d'abonnement reste dans les relevés privés de déploiement.

| Élément | Révision / image | État observé |
|---|---|---|
| Backend final | `avoulia-backend--0000045`, `v2-nomatch-20260910-r2`, digest `sha256:9408ae9a6d8ffc1275a6b6c03f5bba5bbfbb59120f14d4b20b87c44b06b414ea` | Healthy, trafic 100 % |
| Frontend | `avoulia-frontend--0000023`, `v2-nomatch-20260910` | Healthy, trafic 100 % |
| Builds ACR | `dd2a` (backend intermédiaire0044), `dd2b` (frontend), `dd2c` (backend final0045) | Succeeded |

**Inclus** : mobile/état frontend, qualification et classement/listes précédemment préparés, réponse commune « Je n'ai pas de cas suffisamment pertinent… » (sans cas/CTA inventé), précision du besoin ou retour aux étapes antérieures. Le défaut initial « 13 » découvert sur0044 a été corrigé sur0045 (reconnaissance d'un premier choix numérique uniquement avant qualification, après accueil ou historique vide).

**Non inclus** : gabarits CHAT-04/05/06 (durées harmonisées, accès au prompt, rôle neutre), toujours locaux et non régénérés. `parcours_util.py`, documents, pages statiques, mapping et dépendances sont hérités de0043 ; aucune v454 intégrée, v455 créée, modification Excel ou préparation de package Simplon.

**Validation finale** : 106 tests backend et 19 tests frontend, build/typecheck réussis. Live sur0045/0023 : départ direct13 → BTP → objectif4 → problème fiscal hors contexte → message sans correspondance avec stepper disponible → précision vers compte rendu → liste alignée → détail du premier cas et URL UC-0725 correcte ; retour « Modifier : Objectif » opérationnel. API non-stream0045 : même no-match, zéro cas, état de sélection conservé. À390 px, saisie x45..290/envoi x298..330 ; desktop1240 px utilisable. Deux pages servies ont exactement les mêmes SHA-256 avant/après. Pas d'affirmation de test exhaustif du catalogue ni de précision métier globale.

**Reprise / rollback** : recette code-only dans `backend/Dockerfile.dev-code-only`, digest de base et commandes dans `.azure/plan.md` et `HANDOFF.md`. Retour backend : image `acravoulia97186.azurecr.io/avoulia-backend:v2-parcoursfix3-1788183296` ; retour frontend : `acravoulia97186.azurecr.io/avoulia-frontend:v2-cfg-1788165520`. Code local non committé/non poussé ; les images ACR sont publiées sur le dev avec autorisation, pas un package Simplon.

### Update 2026-09-10 — Déploiement développement autorisé, validation en cours

Section chronologique intermédiaire ; état final ci-dessus fait foi.

- **Autorisation** : Eneric a confirmé à 10:15 l'environnement dev uniquement : abonnement Visual Studio Enterprise, `rg-avoulia-fr-dev`, `francecentral`. Package Simplon toujours différé ; aucune modification de la base.
- **Images initiales du lot** : ACR `dd2a` backend et `dd2b` frontend réussis, tags `v2-nomatch-20260910`. Révisions `avoulia-backend--0000044` et `avoulia-frontend--0000023`, Healthy et trafic 100 % observés.
- **Préservation des données** : `backend/Dockerfile.dev-code-only` reprend l'image backend 0043 par digest immuable, superpose uniquement `app/haystack_rag.py` et `app/routes/chat.py`. Pas de classeur, page ou mapping dans le contexte source. `parcours_util.py` conservé : CHAT-04/05/06 ne sont PAS déployés dans ce lot.
- **Contrôles live acquis** : saisie/envoi visibles à 390 px ; flux guidé via choix de domaine/secteur/objectif ; absence de correspondance sur demande fiscale en contexte chantier ; clarification suivante proposant deux cas de compte rendu ; détail du premier avec URL correcte. Endpoint non-stream : même message sans cas sélectionnable, état BTP/objectif4 conservé. Deux empreintes SHA-256 de pages parcours identiques avant/après.
- **Régression repérée pendant la validation** : chiffre « 13 » fourni directement après le seul message d'accueil ne fixe pas le domaine ; la question secteur est alors répétée. Le flux avec question Q1 explicite fonctionne. Correctif source et révision complémentaire en cours, ne pas clôturer ce lot avant nouveau contrôle.
- **Retour arrière disponible** : backend image `v2-parcoursfix3-1788183296` (0043) ; frontend `v2-cfg-1788165520` (0022). Aucun push/commit ou package Simplon.

### Update 2026-09-10 — CHAT-03 : premier essai avec le modèle réel

**Clôture du passage ciblé (pas du calibrage métier)** : quatre appels supplémentaires sur les mêmes modèle, prompt et raisonnement par défaut, avec plafond total de 6 000 tokens et espacement de 90 s. Quatre réponses complètes, aucune troncature. Les deux demandes sans correspondance rejettent tous les candidats ; l'une ajoute des questions numérotées que le diagnostic strict du banc classe comme liste non reconnue. Les deux demandes vagues par synonymes retiennent synthèse + actions plutôt que la seule synthèse attendue. Verdict automatisé inchangé : 1 concordance stricte / 4, 3 échecs (un de format, deux d'ensemble attendu). Ne pas interpréter ce chiffre comme une précision de production : les attentes sont des hypothèses techniques, et le suivi d'actions peut être une interprétation plausible du besoin vague.

**Points restant ouverts** : arbitrer les alternatives acceptables sur demandes vagues ; distinguer questions numérotées et propositions de cas dans le diagnostic d'évaluation ; examiner le message utilisateur sans correspondance (le rapprochement serveur donne une réponse générique sans cas sélectionnable). Aucun seuil sémantique arbitraire ou modification de production ajouté à partir de ces seuls résultats.

**Traçabilité finale** : `chat03-real-model-followup.json` conservé dans les artefacts privés de session, distinct du premier rapport. Consommation des quatre appels : 6 092 tokens de complétion dont 5 184 de raisonnement et 908 non-raisonnement ; un seul budget total, pas deux plafonds indépendants. Script paramétrable par scénario, répétitions, plafond et cible Azure explicite, reprise contrôlée par configuration/empreintes, aucune clé persistée. Suite globale locale : 95 tests réussis, dont 19 propres au banc d'évaluation (les 33 rapportés par l'agent incluaient également les 14 tests de pertinence existants).

Évaluation locale du prompt courant et du rapprochement des listes, avec candidats fictifs, sur le déploiement Azure existant correspondant à la configuration streaming (`gpt-5-mini`). Aucun changement de production, donnée Excel, packaging ou déploiement.

- Outil reproductible ajouté : `backend/scripts/evaluate_chat_relevance.py` (mode hors ligne par défaut, appels réels explicitement activés) ; tests isolés : `backend/tests/test_relevance_evaluation.py`.
- Premier passage borné : 16 tentatives, 15 réponses et une limitation 429. Six concordances avec les attentes techniques, une divergence (requête par synonymes avec cas d'actions supplémentaire), huit réponses tronquées, dont les deux essais sans correspondance.
- Limite du banc : plafond de 1 200 tokens de complétion incluant le raisonnement. Les réponses tronquées ne permettent pas de conclure sur la pertinence en production ; ne pas publier de taux global de précision.
- Suite ciblée effectuée : quatre appels sur les scénarios sans correspondance et par synonymes, budget de réponse augmenté et paramètres consignés ; bilan ci-dessus. Pas de modification du modèle ni de ses paramètres de raisonnement.
- Hors périmètre de cette mesure : recherche vectorielle, base réelle, parcours UI complet et validation des attentes par des utilisateurs. Rapport brut synthétique conservé dans les artefacts privés de session, pas dans les pages publiées.

**Date de démarrage:** 2026-07-08  
**Statut global:** Base privée consolidée ; intégration et recette en cours de préparation ; package Simplon différé

**Cible de travail:** environnement dev existant ; production officielle non engagée
**Repo:** `NricL/A-Vous-l-IA` (public — code et documentation ; données sources exclues)

### Update 2026-09-09 — Améliorations ciblées engagées, non déployées

**Suite CHAT-03 après report du package — lot local clôturé** : prompt imposant tous les candidats identifié et corrigé pour autoriser une sélection plus courte ; rapprochement des titres/IDs affichés avec les cas sélectionnables et rétablissement de leur ordre de classement. Modifications dans `backend/app/haystack_rag.py`, `backend/app/routes/chat.py` ; scénarios fictifs dans `backend/tests/test_chat_relevance.py`. Les limites de blocs Markdown sont détectées indépendamment de la validation du titre, y compris numéros en gras : un candidat inconnu ne peut pas être conservé dans le corps d'un cas reconnu. Total final : 76 tests backend/gabarits, dont 14 de pertinence ; contre-revue ciblée sans blocage connu (20 reproductions HTTP/SSE indépendantes). Ces scénarios ne mesurent pas la précision d'un modèle réel et ne constituent pas un calibrage humain de la pertinence. Aucun seuil arbitraire ajouté, aucun package ni déploiement.

**Décision Eneric à 15:41** : ne pas préparer le package Simplon maintenant. Poursuivre les actions restantes, en commençant par CHAT-03 (pertinence), avec traçabilité dans les documents du dépôt. L'accès structuré nécessaire pour terminer l'audit Excel reste à résoudre. Pas de packaging, push ou déploiement engagé. La future reprise simple par Simplon reste une contrainte, pas le chantier courant.

Le statut global ci-dessus est historique. La livraison locale de septembre n'est pas encore publiée ni prête à être déployée.

- **Accord Eneric** : corriger les frictions du chatbot et améliorer les colonnes Excel existantes, sans pivot. La découverte reste destinée aux employés qui ne savent pas encore comment l'IA pourrait les aider. Six étapes, catalogue, pré-filtrage et verbatim conservés.
- **Sources de travail** : copie récupérée à `8f2d673`. Le correctif de contenu court de la révision backend 0043 ne figure pas intégralement dans ce commit ; il doit être conservé et couvert par les tests avant livraison.
- **CHAT-04/05/06 préparés** : durée 2h12 de travail actif estimé (somme des étapes, hors test terrain), accès au prompt existant sans déplacer les étapes, rôle générique à compléter. Backend : `app/parcours_util.py`. Dépôt parcours associé : `pipeline/genere.py`, `templates/page.html.j2`.
- **CHAT-01/02** : corrections mobile et état interface/backend préparées localement ; revue ciblée clôturée sans blocage connu. **CHAT-03 partiel** : repli abandonnant le secteur supprimé, variantes multi-sectorielles/secteurs composés préservées et classement lexical corrigé ; exclusion des quasi-correspondances sémantiques non calibrée.
- **Excel** : seule la référence désignée par Eneric doit être utilisée ; audit M365 en lecture seule, pas de copie locale historique employée comme source actuelle. Toute modification produira un nouveau fichier au même nom, `vXXX` incrémenté, source préservée. Aucun classeur modifié.
- **Livraison** : pas de push, de commit ou de déploiement dans ce lot à ce stade. Les pages statiques déjà embarquées sont inchangées ; les gabarits seuls ne les mettent pas à jour.
- **Traçabilité** : voir `ROADMAP.md`, `CHANGELOG.md` et l'addendum du `HANDOFF.md`. Les autres sujets restent à la main d'Eneric.
- **Bilan local final** : 62 tests backend/gabarits et 18 régressions frontend passent ; build/typecheck passent. Contrôles de rendu isolé mobile/ordinateur rapportés dans le changelog. Ne pas assimiler ce bilan à une validation de toutes les données ou à une mise en ligne.

### Update 2026-08-31 (3) — Axe 3.4 : sortie de parcours (lien Retour) — DÉPLOYÉ ✅ · 3.3 abandonné
- 🎯 Ne plus laisser l'utilisateur dans un cul-de-sac quand le parcours s'ouvre dans un nouvel onglet.
- ✅ **Pages parcours :** lien **« ← Retour à Avoulia »** en tête + rappel en pied (« Revenir à Avoulia
  pour explorer d'autres cas d'usage ») pointant vers l'app chat, sur les **1025 pages**.
- ✅ **Sans régression :** au lieu de régénérer (le générateur `generate_parcours_pages.py` produit un
  template ANCIEN, à ne pas utiliser), un script **idempotent** `add_backlink_parcours.py` injecte 2
  lignes par page (marqueur `id="avoulia-back"`). URL app via `AVOULIA_APP_URL` (défaut front,
  cohérent Axe 4.5).
- ✅ **Relance côté chat :** déjà couverte par le **stepper cliquable** (« Cas d'usage » → retour à la
  liste) — pas de doublon ajouté (C1).
- 🧪 **Validé (prod) :** page parcours affiche les 2 liens ; clic → atterrit sur l'app ; template
  intact (aucune régression visuelle) ; smoke 7/7.
- ✅ Déployé `avoulia-backend--0000040` (`v2-backlink-1788170089`).
- ❌ **3.3 (A/B testing CTA/pitch) abandonné définitivement** (décision Eneric).
- 📄 Doc : CHANGELOG §3.11, HANDOFF (section « Lien Retour à Avoulia »), ROADMAP (3.4 ✅ / 3.3 ❌).

### Update 2026-08-31 (2) — Axe 4.5 : URL backend = variable de config unique — DÉPLOYÉ ✅
- 🎯 Faciliter la reprise Simplon (C1/C2) : héberger ailleurs = changer **une variable**, sans éditer
  le code. Les URL backend étaient codées en dur à ~6 endroits.
- ✅ **Backend :** `parcours_util.py` lit `config.parcours_base_url` (env `PARCOURS_BASE_URL`, un seul
  défaut) via `_parcours_base_url()` — suppression des 2 URL codées en dur.
- ✅ **Frontend :** `nginx.conf` → **`nginx.conf.template`** avec `${BACKEND_ORIGIN}` (envsubst natif de
  l'image nginx au démarrage) ; Host dérivé via `$proxy_host` (une seule variable). Défaut posé dans
  `frontend/Dockerfile` (`ENV BACKEND_ORIGIN`).
- ✅ **CI Pages + smoke test :** déclaration unique (`env.BACKEND_ORIGIN`, `SMOKE_BASE_URL`/`PARCOURS_BASE_URL`).
- ✅ **docker-compose :** hint commenté pour proxifier le backend local.
- 🧪 **Validé (prod) :** défaut + override `PARCOURS_BASE_URL` (→ `https://example.test/...`) ; frontend
  redéployé **Healthy** ; proxy `/api/` OK (welcome **et streaming SSE** à travers nginx) ; smoke 7/7 ;
  14/14 tests backend.
- ✅ Déployé `avoulia-backend--0000039` (`v2-cfg-1788165180`) + `avoulia-frontend--0000022` (`v2-cfg-1788165520`).
- 📄 Doc : CHANGELOG §3.10, HANDOFF (section « URL backend = variable unique »), ROADMAP (4.5 ✅).

### Update 2026-08-31 (1) — Axe 4.1 + 4.3 : CI GitHub Actions & détection de code mort — POUSSÉ ✅
- 🎯 Garde-fous industriels pour C1 (Simplon livre sans expertise dev) et C2 (traçabilité) : plus
  aucune régression silencieuse ne part en prod.
- ✅ **CI (`.github/workflows/ci.yml`)** sur push/PR `main`, **sans secret**, **ne déploie rien** :
  backend (`compileall` + 14 tests) · frontend (`type-check` + `check:dead` + `build` + lint informatif).
- ✅ **Détection de code mort (4.3, `frontend/scripts/check-dead-code.mjs`)** : échoue si un `.vue` de
  `src/` n'est importé nulle part (garde-fou anti-`ChatView.vue`). Exposé via `npm run check:dead`.
- ✅ **Nettoyage :** suppression du scaffolding Vite mort (HelloWorld, TheWelcome, WelcomeItem,
  `icons/*`) — 8 fichiers. Build front OK après suppression, `check:dead` vert (5 composants réels).
- 🧪 Validé localement (compileall OK, 14/14 tests, type-check + build OK, check:dead OK) puis
  **CI GitHub Actions vérifiée au vert** après push.
- 📄 Doc : CHANGELOG §3.9, HANDOFF (section « CI/CD & déploiement » + chemin pour brancher le CD).
- ⏭️ CD auto volontairement non branché (identifiants spécifiques au tenant Simplon) — procédure
  documentée dans HANDOFF.

### Update 2026-08-27 (5) — Axe 3.2 : feedback 👍/👎 sur les cas — DÉPLOYÉ ✅
- 🎯 Mesurer la **qualité perçue** des cas recommandés (pas juste le volume), pour prioriser
  l'amélioration de la base. Reste simple et intégré (C1), aucun produit externe.
- ✅ **UI (`HomeView.vue`) :** sous la carte d'un cas, « Ce cas vous semble-t-il pertinent ? » +
  boutons **👍/👎** (cibles tactiles 40px). Un clic → remerciement, boutons masqués, **un seul vote**
  par cas.
- ✅ **Backend :** endpoint `POST /api/v1/chat/feedback` → `stats.record("feedback_up"/"feedback_down")`
  avec le **titre verbatim** du cas. `/stats` : KPI **taux de satisfaction** (`N👍/M👎`) + 2
  classements (cas jugés utiles / peu pertinents).
- ✅ **Libellé propre :** le frontend envoie `cas_utilisation` (exposé dans `suggested_cases`), pas le
  `content` brut (rag_text à pipes). Validé : `/stats` affiche « Concevoir des modèles d'infographies… ».
- 🧪 **Validation E2E navigateur (prod) :** 👍 sur un cas puis 👎 sur un autre → remerciement affiché,
  `/stats` montre le taux + libellés propres. Backend compile, 14/14 tests, build front OK, smoke 7/7.
- ✅ Déployé `avoulia-backend--0000038` (image `v2-fb-1787845376`) + `avoulia-frontend--0000021`
  (`v2-fb2-1787846331`). Doc à jour : CHANGELOG §3.8, HANDOFF (section feedback).

### Update 2026-08-27 (4) — Axe 3.1 : statistiques d'usage intégrées — DÉPLOYÉ ✅
- 🎯 Besoin d'Eneric : savoir **ce qui est le plus visité** (rôles/problématiques/cas) + les **clics
  bouton parcours**, **sans** ajouter de repo/produit/dashboard séparé (contrainte C1 : package simple
  pour Simplon).
- 💡 **Choix (validé) :** #1 « stats intégrées » maintenant ; le mono-conteneur (#2) au moment du
  packaging Simplon.
- ✅ **Backend :** nouveau module `stats.py` — **append blob Azure** (`stats/events.jsonl`) si
  `STORAGE_ACCOUNT_NAME/KEY` configurés, sinon **repli mémoire**. Page **`/stats`** (HTML server-rendered)
  + **`/api/v1/stats.json`** ajoutées dans `main.py` **avant** le mount statique catch-all. Endpoint
  `POST /api/v1/chat/parcours-click` dans `routes/chat.py`.
- ✅ **Enregistrement branché :** domaine (à la sélection) + problème (texte libre Q3) via
  `_record_usage_stats` ; cas (ouverture carte verbatim) via `stats.record("cas", …)` dans
  `haystack_rag.py` ; clic parcours via `trackParcoursClick` (`chat.ts`) câblé sur `onParcoursClick`
  (`HomeView.vue`), fire-and-forget (n'empêche jamais l'ouverture de l'onglet).
- ✅ **Storage branché** sur `stavoulia97186` (env vars sur `avoulia-backend`) → stats **durables**.
- 🧪 **Validation E2E navigateur (prod) :** parcours réel domaine → secteur → objectif → problème →
  cas → clic parcours ; `/stats` affiche les **4 types** (domaine « Marketing & visibilité », cas
  « Créer des infographies… », problème saisi, 2 clics). Compilation backend OK, 14/14 tests, build
  frontend OK, smoke test 7/7. Blob de test **purgé** (état propre).
- ✅ Déployé `avoulia-backend--0000037` (image `v2-stats-1787843585`) + `avoulia-frontend--0000019`.
- 📄 Doc mise à jour : `CHANGELOG.md` (§3.7), `HANDOFF.md` (section « Usage Stats » + troubleshooting).

### Update 2026-08-27 (3) — Axe 2.3 : retour arrière / correction — DÉPLOYÉ ✅ (clôt l'Axe 2)
- 🎯 Permettre de corriger un choix (domaine/secteur/objectif…) **sans tout recommencer**.
- 💡 **Choix UX (validé avec Eneric) :** stepper cliquable plutôt que « Étape N/4 » chiffré, AVEC de vrais
  signaux d'interactivité (le point faible d'un stepper = on ne devine pas qu'il est cliquable).
- ✅ **Archi :** le backend étant **stateless** (il re-déduit l'état à partir de l'historique + des choix
  renvoyés), « revenir en arrière » = opération **100 % frontend** : `goBackToStep()` tronque l'historique
  local jusqu'à la question voulue + réinitialise les choix en aval. **Aucune modif backend.**
- ✅ **UI (`HomeView.vue`) :** les étapes **faites** (✓) du stepper deviennent cliquables — curseur main,
  surbrillance au survol, **↩ au survol**, tooltip « Modifier : <étape> », accessible clavier (role/tabindex/Enter).
  Reset ciblé : Domaine efface tout ; Objectif garde domaine+secteur ; etc. « Cas d'usage » ramène à la liste.
- ✅ **Mobile :** les libellés des étapes **faites** restent affichés (donc éditables au doigt) ; seuls les
  libellés des étapes **à venir** sont masqués. Pas de débordement de page.
- 🧪 **Validation E2E navigateur (prod) :**
  - À Q3, clic « Objectif » → retour à Q2 (question + 6 chips réaffichées), historique tronqué (9→7), stepper à jour.
  - Re-réponse → le flux repart correctement vers Q3 (backend re-déduit), 0 erreur console.
  - Clic « Domaine » → reset total (Q1, 14 chips, tout réinitialisé).
  - Mobile 390×844 : étapes faites labellisées + cliquables, pas de débordement.
- ✅ Déployé `avoulia-frontend--0000018`.
- ✅ **Axe 2 (Fluidité UX) terminé :** 2.1 accueil · 2.2 chips questions · 2.2b chips cas · 2.3 retour arrière ·
  2.4 stepper (6 étapes) · 2.5 carte miroir verbatim · mobile.

### Update 2026-08-27 (2) — Stepper : ajout des étapes « Cas d'usage » et « Parcours » — DÉPLOYÉ ✅
- 🎯 Rendre tout le parcours visible et **matérialiser la destination** (« Parcours ») pour renforcer le bouton.
- ✅ `HomeView.vue` : le stepper passe à **6 étapes** — `Domaine › Secteur › Objectif › Problème › Cas d'usage › Parcours`.
  - « Cas d'usage » = **en cours** quand la liste de cas est affichée.
  - « Parcours » = **en cours** sur la fiche détail (là où le bouton apparaît) → pointe vers le CTA.
  - Le stepper reste visible jusqu'au détail (plus masqué aux résultats).
- ✅ **Mobile** : 6 pastilles + **seul le libellé de l'étape courante** affiché (media `≤580px`) → aucun débordement/scroll.
- 🧪 **Validation E2E navigateur (prod) :** liste → « Cas d'usage » current / « Parcours » upcoming ; détail →
  « Cas d'usage » done / « Parcours » current + bouton présent. Mobile 390×844 : 6 pastilles, label « Parcours » seul, pas de débordement. 0 erreur console.
- ✅ Déployé `avoulia-frontend--0000017`.

### Update 2026-08-27 — Axe 2.4 : indicateur de progression (stepper) — DÉPLOYÉ ✅
- 🎯 Situer le dirigeant dans le questionnaire (éviter l'abandon) sans dénominateur trompeur.
- ✅ `HomeView.vue` : **stepper compact** au-dessus du chat — `Domaine › Secteur › Objectif › Problème`.
  Phase courante détectée depuis le dernier message assistant (libellés fixes). États : à venir / en
  cours / fait (✓) / **sauté** (« – ») pour le secteur quand le domaine n'en a pas (ex. Direction).
  Masqué dès qu'on arrive aux résultats (liste de cas / détail). 100 % frontend, aucun risque backend.
- 🧪 **Validation E2E navigateur (prod) :**
  - Domaine **avec** secteur (Marketing) : Domaine→Secteur→Objectif→Problème progressent, stepper masqué aux résultats.
  - Domaine **sans** secteur (Direction) : « Secteur » affiché **sauté**, Objectif devient l'étape courante.
  - Mobile 390×844 : stepper 35 px, tient sans débordement ni scroll. 0 erreur console.
- ✅ Déployé `avoulia-frontend--0000016`.

### Update 2026-08-26 (6) — Carte de cas « miroir » verbatim (Axe 2.5) — DÉPLOYÉ ✅
- 🎯 **Objectif :** rendre la réponse détaillée d'un cas plus courte et orientée « donne envie de
  cliquer sur le bouton parcours », en **répartissant** le contenu : la réponse chat garde ce qui
  crée l'envie, le **parcours** garde le détail opérationnel (on supprime le doublon).
- 🔍 **Constat :** ~60 % de l'ancienne fiche était déjà dans le parcours (prérequis → étape 2,
  guardrails → étape 3, première action → étape 4, auto-diagnostic → étape 1). Et un seul bloc était
  **généré par l'IA** (« Pourquoi c'est pertinent », `_run_pertinence_llm`) — contraire à la règle
  **D1 (verbatim)**.
- ✅ **Fix (`backend/app/haystack_rag.py`) :** `build_niveau2_block(case)` réécrite en **carte miroir
  100 % verbatim** depuis la base : Titre (`cas_utilisation`) · badges (`mode_execution` mappé via un
  dictionnaire figé + `effort` + `sensibilite_donnees`) · « Ce que ça vous apporte » (`description_
  cas_utilisation`) · « Particulièrement utile si vous rencontrez » (`declencheurs_typiques`). **Appel
  LLM de pertinence supprimé** ; prérequis/première action/guardrails/auto-diagnostic retirés (→ parcours).
- ✅ **Tests :** 2 tests de non-régression (carte verbatim & lean, mapping mode_execution). **14/14.**
- 🐛🔧 **Bug d'infra corrigé au passage (récurrent) :** l'image ACR embarquait une **couche `COPY`
  périmée** (le `.py` déployé ne contenait pas le nouveau code alors que la source locale, oui). Fix
  durable : `backend/Dockerfile` ajoute `ARG CACHEBUST` avant `COPY app` ; build avec
  `--build-arg CACHEBUST=<timestamp>` → la copie du code est toujours refaite à neuf.
- ✅ **Déploiement :** `avoulia-backend:ux-carte-miroir2-20260826`, révision `avoulia-backend--0000036`.
- 🧪 **Validation E2E navigateur (prod) :** sélection d'un cas → carte **891 car.** (vs ~1800 avant),
  badges + description verbatim + déclencheurs, **0 pertinence IA**, **0 champ opérationnel**, bouton
  présent, pitch unique. Smoke test 7/7.
- ➡️ **Suite (Option B, base) :** possibilité d'ajouter une colonne `accroche_chat` (prompt Copilot
  Excel fourni à Eneric) affichée verbatim en tête de carte pour une accroche encore plus vendeuse.

### Update 2026-08-26 (5) — J1 : UX (accueil + chips) & smoke test — DÉPLOYÉ ✅
Premiers chantiers de la ROADMAP (Axe 2 UX, Axe 4 fiabilité). Livrés et validés E2E navigateur.

**Axe 4.2 — Smoke test post-déploiement**
- ✅ `smoke-test.mjs` à la racine : script **Node sans dépendance** (fetch natif) lançable via
  `node smoke-test.mjs [baseUrl]`. Vérifie en quelques secondes : `/health`, endpoint welcome,
  sélection d'un cas → `parcours_url` top-level + pas d'erreur ChatMessage + pitch unique,
  page parcours = 200, et garde-fou timing (pas de bouton sur une question). **7/7 vert.**
- Pensé pour **C1 (Simplon sans dev)** : aucune install, aucun navigateur à télécharger.

**Axe 2.1 — Message d'accueil non répété**
- 🐛 Le `RAG_PROMPT` fait ré-afficher l'accueil au début de CHAQUE réponse (déjà montré au chargement).
- ✅ `routes/chat.py` : `_strip_repeated_welcome()` retire ce préambule dans `_sanitize_answer_text`
  (donc sur tous les chemins). **Insensible au type d'apostrophe/guillemet** (le LLM produit des
  apostrophes typographiques `’` là où `WELCOME_MESSAGE` a des apostrophes droites `'`) via une
  normalisation 1:1 qui préserve les indices. Déployé `avoulia-backend--0000034`.

**Axe 2.2 — Chips de choix cliquables**
- ✅ `HomeView.vue` : les questions guidées Q1 (14), Q1.5 (secteur), Q2 (objectif) affichent des
  **boutons cliquables** (`parseSimpleChoices` + `.choice-chip`). Le clic envoie le **numéro**
  (100 % fiable côté backend) ; le texte de la question est conservé (aucune transformation risquée).
- ✅ Chips uniquement sur le **dernier** message assistant. La **liste de cas** (paragraphes entre
  les items) et **Q3** (texte libre) n'affichent **pas** de chips — préservés. Déployé
  `avoulia-frontend--0000012`.
- 🧪 **Validation E2E navigateur (prod) :** Q1→14 chips, clic « RH » → « 3 » → Q1.5 5 chips → clic →
  Q2 8 chips (apostrophe « Gérer l'administration RH » OK) → clic → Q3 **0 chip** → liste **0 chip**
  → sélection cas → **bouton parcours visible**, pitch unique, accueil absent. 0 erreur console.
- ⚠️ **Pour Simplon :** le clic-chip envoie le numéro (pas le libellé) pour rester robuste ; la
  sélection d'un cas reste au clavier (liste « riche » volontairement non transformée en chips).

**Mobile-friendly (vérifié au navigateur en viewport 390×844)**
- ✅ Aucun débordement horizontal (Q1 14 chips, liste, détail).
- 🐛 Chips à 25 px de haut = cible tactile trop petite sur mobile.
- ✅ Media query `max-width:580px` : `.choice-chip` passe à **40 px** de haut / police **13 px** /
  gap 8 px. Bouton parcours CTA : 84 px de haut, pleine largeur utile, sans débordement.
  Déployé `avoulia-frontend--0000013`.

**Axe 2.2b — Chips de sélection de cas (« Cas 1 / Cas 2… »)**
- ✅ Sur la **liste de cas**, on garde le **texte complet** (les descriptions « Pourquoi c'est
  pertinent » / « Ce que cela permet » sont utiles) et on ajoute des chips courtes **« Cas N »**
  qui envoient le numéro du cas → sélection en un clic (`HomeView.vue` : `parseCaseChoices` +
  `choicesFor`). Détection robuste par **≥2 lignes « N. » en début de ligne** (indépendante du
  format LLM, qui met parfois « --- »/« approfondir », parfois non). Q3 (texte libre) et la fiche
  détail n'ont pas de lignes « N. » → pas de faux positif.
- 🧪 **Validation E2E navigateur (prod) :** liste → chips « Cas 1…Cas 5 » + texte complet préservé ;
  clic « Cas 2 » → envoie « 2 » → détail du bon cas + **bouton parcours** (href OK), **pitch unique**,
  **0 chip** sur le détail. Chips de cas héritent du dimensionnement tactile mobile (40 px).
  Déployé `avoulia-frontend--0000015`.
- ⚠️ **Note test :** après un `containerapp update`, prévoir un délai de propagation (l'ancienne
  révision peut répondre quelques secondes) — utiliser un cache-buster à la navigation. Les réponses
  LLM peuvent dépasser 10 s : attendre la fin du streaming (`.typing` disparu) avant d'assert.

### Update 2026-08-26 (4) — Bouton parcours affiché trop tôt (pendant les questions) — DÉPLOYÉ ✅
- 🐛 **Symptôme :** le bouton « 🚀 Démarrer mon parcours » apparaissait dès qu'on répondait à une **question** par un chiffre (Q1.5 secteur, Q2 objectif, Q3 problème), alors qu'aucun cas n'était encore sélectionné.
- 🔍 **Cause :** le *fallback* de `resolveParcoursCta` (dans `HomeView.vue`) devinait un cas à partir du chiffre saisi (`/^[1-5]$/`) même quand la réponse backend était une simple question — il piochait alors dans les cas précédents et affichait un bouton à tort.
- ✅ **Fix :** suppression totale du fallback. Le bouton s'appuie désormais **uniquement** sur le champ autoritaire `payload.parcours_url` (envoyé par le backend seulement sur une vraie réponse-détail après sélection d'un cas). `resolveParcoursCta(payload)` ne prend plus qu'un argument.
- ✅ **Validation E2E navigateur (Playwright, prod, scénario RH du bug) :**
  - Q1.5 secteur / Q2 objectif / Q3 problème → **aucun bouton** ✅
  - liste de 5 cas → **aucun bouton** ✅
  - sélection d'un cas → bouton **visible**, bon `href` (page 200), pitch **une seule fois** ✅
- ✅ **Build & déploiement :** `avoulia-frontend:fix-cta-timing-20260826`, révision `avoulia-frontend--0000011`.
- ⚠️ **Pour Simplon (handoff) :** le bouton parcours est **strictement piloté par le backend** (`payload.parcours_url`). Ne jamais réintroduire de résolution par chiffre/index côté frontend — c'est exactement ce qui faisait apparaître le bouton pendant les questions.

### Update 2026-08-26 (3) — LE bouton parcours enfin fonctionnel (composant mort + cache) — DÉPLOYÉ ✅
- 🐛 **Symptôme persistant :** malgré tous les correctifs CTA précédents, le bouton parcours **ne s'affichait toujours pas** dans l'UI.
- 🔍 **Cause racine n°1 (composant mort) :** tout le code du bouton (résolution CTA, template, CSS) avait été écrit dans `frontend/src/views/ChatView.vue`… **qui n'est importé nulle part** dans l'application. Le vrai composant de chat rendu à l'écran est **`frontend/src/views/HomeView.vue`**, qui n'avait aucune logique de bouton. Vite tree-shakait `ChatView.vue` → mes changements n'apparaissaient jamais dans le bundle (hash JS identique build après build). Vérifié : le bundle ne contenait pas la classe `parcours-cta`, et `grep ChatView` dans `src/` ne renvoyait **aucune** référence.
  - ✅ Fix : implémentation du bouton dans **`HomeView.vue`** (helper `resolveParcoursCta` priorisant `payload.parcours_url` du backend, attache `parcoursUrl`/`parcoursCtaLabel` au dernier message dans `onDone`, rendu `<a class="parcours-cta">` + CSS). `ChatView.vue` (fichier mort) **supprimé** pour éviter toute confusion future.
- 🔍 **Cause racine n°2 (cache navigateur) :** `nginx.conf` ne posait aucun en-tête de cache. Le navigateur servait un `index.html` en cache qui référençait l'ancien bundle JS → même après déploiement, l'utilisateur chargeait l'ancien code.
  - ✅ Fix : `index.html` servi en `no-cache, no-store, must-revalidate` ; assets hashés (`/assets/`) en `max-age=1an, immutable`.
- ✅ **Validation E2E navigateur (Playwright, prod) :** parcours complet Marketing → Commerce & retail → Créer des contenus marketing → problème → liste → sélection cas 1. Le bouton **« 🚀 Démarrer mon parcours (6 étapes, ~2h) »** est présent dans le DOM, **visible** (548×53px, fond bleu), `target="_blank"`, `href` = page parcours réelle (HTTP 200). Pitch affiché **une seule fois**. 0 erreur console.
- ✅ **Build & déploiement :** frontend `avoulia-frontend:fix-cta-final-20260826`, révision `avoulia-frontend--0000010`.
- ⚠️ **Pour Simplon (handoff) — leçon capitale :** le composant de chat réellement utilisé est **`HomeView.vue`**, PAS `ChatView.vue` (supprimé). Toute évolution de l'UI de chat se fait dans `HomeView.vue`. Et `index.html` doit rester en `no-cache` pour que les déploiements soient pris en compte immédiatement.

### Update 2026-08-26 (2) — Bloc « Passez à l'action » dupliqué + bytecode périmé — DÉPLOYÉ ✅
- 🐛 **Symptôme :** après sélection d'un cas, le bloc CTA « 🚀 Passez à l'action… » s'affichait **deux fois** de suite.
- 🔍 **Cause 1 (double ajout) :** le suffixe parcours était ajouté à la fois dans `_build_niveau2_detail_payload` (haystack_rag) **et** dans `_append_parcours_links_to_answer` (routes/chat) — ce dernier ne dédupliquait que si une URL brute était présente, or on ne met plus l'URL en texte.
  - ✅ Fix : sentinelle unique `PARCOURS_PITCH_SENTINEL` (« Passez à l'action ») dans `parcours_util.py` ; les deux points d'ajout sont désormais **idempotents** (n'ajoutent le pitch que s'il n'est pas déjà présent).
- 🔍 **Cause 2 (LA vraie, insidieuse — bug « fantôme ») :** malgré le correctif présent dans le `.py` déployé (vérifié par `grep` dans le conteneur), la prod gardait l'ancien comportement. Root cause : des fichiers **bytecode périmés** (`__pycache__/*.pyc`, y compris des `cpython-314.pyc` venant de la machine de dev) étaient embarqués dans l'image et **exécutés à la place de la source à jour**. Résultat : plusieurs déploiements sans effet visible.
  - ✅ Fix : `backend/Dockerfile` purge tout `__pycache__` après `COPY app` (`find /app -name __pycache__ -prune -exec rm -rf {} +`) et fixe `PYTHONDONTWRITEBYTECODE=1` / `PYTHONUNBUFFERED=1`. `__pycache__` local nettoyé avant build.
- ✅ **Tests :** 1 test de non-régression ajouté (pitch unique). **12/12 tests passent.**
- ✅ **Build & déploiement :** ACR run `dd1f` (Succeeded) → image `avoulia-backend:fix-pitch-dedup-clean-20260826`, révision `avoulia-backend--0000032`, `/health` → 200.
- 🧪 **Validation E2E (prod) :** sélection cas 1 et cas 2 → pitch affiché **une seule fois**, `parcours_url` top-level correct par cas, aucun crash `ChatMessage`.
- ⚠️ **Pour Simplon (handoff) — leçon importante :** si un correctif présent dans le code source semble « ne pas prendre » en prod, suspecter du **bytecode `.pyc` périmé** embarqué dans l'image. Le Dockerfile purge désormais `__pycache__` ; ne jamais committer/copier de `__pycache__` dans le contexte de build (déjà couvert par `.dockerignore`, renforcé au niveau Dockerfile).

### Update 2026-08-26 — Bouton parcours fiable + fix ChatMessage — DÉPLOYÉ ✅
- 🐛 **Bug 1 (crash sélection) :** après la migration vers l'API chat de Haystack, la sélection d'un cas plantait avec `'ChatMessage' object has no attribute 'strip'`. Cause : la nouvelle API expose le texte via `ChatMessage.text` (et non plus `.content`), donc un objet `ChatMessage` était laissé là où une chaîne était attendue.
  - ✅ Fix : helper unique `_reply_to_text()` (gère `.text`, l'ancien `.content` et les chaînes brutes), appliqué aux deux points de lecture du générateur (`_run_pertinence_llm`, `query_rag_haystack`).
- 🐛 **Bug 2 (bouton parcours absent/non fiable) :** le bouton n'apparaissait pas systématiquement après la sélection d'un cas. Cause racine : le frontend **devinait** le cas sélectionné en re-matchant `suggested_cases[index]` via le chiffre saisi — fragile selon le flux (affirmation « ok », détail textuel, numéro non capté…).
  - ✅ Fix (backend autoritaire) : sur toute réponse détail, `get_rag_prompt_and_sources` renvoie désormais explicitement `parcours_url` + `parcours_cta_label` du cas **réellement** sélectionné (via `build_parcours_info`), transmis en **champs top-level** du payload SSE `done`.
  - ✅ Fix (frontend) : `resolveParcoursCta` utilise en **priorité** ces champs backend ; l'ancienne résolution par id/index/chiffre ne sert plus que de fallback. Le bouton `.parcours-cta` s'affiche donc de façon déterministe.
- ✅ **Tests :** 2 tests de non-régression ajoutés (extraction `_reply_to_text` ; URL/libellé parcours autoritaires pour le cas sélectionné). **11/11 tests passent.** `npm run build` (type-check + vite) OK.
- ✅ **Build & déploiement :**
  - Backend : ACR run `dd1c` (Succeeded) → image `avoulia-backend:fix-cta-chatmsg-20260826`, révision `avoulia-backend--0000030`, `/health` → 200.
  - Frontend : ACR run `dd1d` (Succeeded) → image `avoulia-frontend:fix-cta-chatmsg-20260826`, révision `avoulia-frontend--0000007`, HTTP 200.
- 🧪 **Validation E2E (prod) :** sélection d'un cas via l'API stream → aucun crash `ChatMessage`, payload `done` avec `parcours_url` top-level pointant vers le cas choisi (UC-0471 → `action-sj9mh8h8ft.html`), page parcours accessible (200).
- ⚠️ **Pour Simplon (handoff) :** l'API chat de Haystack renvoie des `ChatMessage` (texte via `.text`) — toujours passer par `_reply_to_text()`. Et le bouton parcours doit rester **piloté par le backend** (`parcours_url`/`parcours_cta_label` du payload `done`), jamais reconstruit par index côté frontend.

### Update 2026-08-25 (4) — Compatibilité générateur Haystack — DÉPLOYÉ ✅
- 🐛 La sélection d'un cas déclenchait une erreur car `AzureOpenAIGenerator` n'existe plus dans la version Haystack installée.
- ✅ Migration vers `AzureOpenAIChatGenerator` / `OpenAIChatGenerator`, `ChatPromptBuilder` et `ChatMessage`.
- ✅ Nouvelle révision backend `avoulia-backend--0000029`, 100% du trafic, `/health` → `200 OK`.
- 🧪 Le parcours de sélection d'un cas peut désormais être rejoué en production.

### Update 2026-08-25 (2) — Lien parcours cliquable + CTA industrialisé — DÉPLOYÉ ✅
- 🎯 **Problème UX :** le lien vers la page parcours était affiché en texte brut dans le chat (copier-coller obligatoire), et le message qui l'accompagnait n'invitait pas assez à cliquer.
- ✅ **Fix appliqué :**
  - Frontend (`ChatView.vue`) : le lien parcours n'est plus concaténé en texte — il est désormais rendu comme un vrai **bouton CTA cliquable** (`<a class="parcours-cta">`), sourcé sur `SuggestedCase.parcours_url` reçu du backend. Les autres URLs éventuelles dans le texte du chat sont aussi rendues cliquables (`linkifyParts`, sans `v-html` pour éviter tout risque XSS).
  - Backend — nouvelle **source de vérité unique** `app/parcours_util.get_parcours_pitch()` : calcule dynamiquement le nombre d'étapes (6) et la durée active du parcours (arrondie à la demi-heure la plus proche, ex. `~2h`) à partir de la structure réelle des pages parcours générées (`generate_parcours_pages.py`), puis produit un libellé de bouton (`cta_label`, ex. *"🚀 Démarrer mon parcours (6 étapes, ~2h)"*) et un texte incitatif (`message_suffix`) cohérents entre eux.
  - `routes/chat.py` et `haystack_rag.py` utilisent désormais tous les deux `get_parcours_pitch()` au lieu d'un texte dupliqué en dur à deux endroits — si la structure du parcours change un jour (nb d'étapes, durée), **un seul endroit à modifier** (`parcours_util.py`).
  - `models.SuggestedCase` expose un nouveau champ `parcours_cta_label` : le frontend affiche donc exactement le même libellé que celui utilisé dans le texte du chat, sans duplication ni risque de désynchronisation.
- ✅ **Build & déploiement :**
  - Backend : ACR build (run `dd11`, Succeeded) → image `acravoulia97186.azurecr.io/avoulia-backend:v2-parcours-pitch-202608251558`, déployé sur `avoulia-backend` (`rg-avoulia-fr-dev`), `/health` → `200 OK`.
  - Frontend : ACR build (run `dd12`, Succeeded) → image `acravoulia97186.azurecr.io/avoulia-frontend:v2-parcours-pitch-202608251558`, déployé sur `avoulia-frontend` (`rg-avoulia-fr-dev`).
  - `npm run build` (type-check + vite build) et `python -m py_compile` passent sans erreur.
- 🧪 **À valider en prod :** poser une question, obtenir un cas suggéré, vérifier que le bouton parcours s'affiche bien avec le libellé dynamique et s'ouvre dans un nouvel onglet.
- ⚠️ **Pour Simplon (handoff) :** si la structure des pages parcours générées change (plus/moins d'étapes, durées différentes), mettre à jour uniquement les constantes `PARCOURS_STEPS_COUNT` / `PARCOURS_ACTIVE_MINUTES` dans `backend/app/parcours_util.py` — le texte du chat et le libellé du bouton se mettront à jour automatiquement partout, sans autre modification de code.

### Update 2026-08-25 (3) — Après sélection d'un cas : réponse terminale — DÉPLOYÉ ✅
- ✅ Après le choix d'un cas, le bot fournit directement les informations utiles puis le bouton du parcours personnalisé.
- ✅ Suppression des faux choix « détail complet / plan synthétique » et des questions « Répondez 1 ou 2 » en fin de réponse.
- ✅ Le contexte de sélection est conservé dans le flux SSE afin de rattacher le bouton au bon cas, même lorsque la réponse streamée ne renvoie pas de liste de cas.

### Update 2026-08-25 — Fix filtrage RAG (mélange d'intentions marketing) — DÉPLOYÉ ✅
- 🐛 **Bug 1 (mismatch marketing) :** en choisissant l'objectif "Créer des contenus marketing", les exemples de reformulation (Q3) et certains cas suggérés appartenaient à d'autres intentions marketing (acquisition, analyse de marché, campagnes...).
- 🐛 **Bug 2 (sélection impossible) :** le bot affichait 5 cas numérotés mais refusait le choix "4" ou "5" ("Le choix « 4 » n'est pas disponible... 1, 2 ou 3"), preuve que moins de cas réels que de cas affichés étaient retournés.
- 🔍 **Root cause commune :** deux "fallbacks silencieux" dans `backend/app/haystack_rag.py` qui, faute de résultats sur le filtre strict (domaine+intention+secteur), retombaient sur **tous les documents du domaine** (toutes intentions confondues) au lieu de renvoyer un résultat vide/restreint :
  - `build_pool()` : `docs = filtered if filtered else docs` → mélange d'intentions.
  - `_retrieve_docs_for_question()` : une étape de repli abandonnait le filtre "intention" pour ne garder que domaine+secteur.
  - En parallèle, le prompt RAG imposait un "minimum 3 cas" sans garantie que 3 documents réels existaient : le LLM inventait alors des cas supplémentaires pour respecter la consigne, d'où l'écart entre cas affichés (jusqu'à 5, dont certains inventés) et cas réellement sélectionnables (`suggested_case_ids`).
- ✅ **Fix appliqué :**
  - `build_pool()` : suppression du repli "tous les docs du domaine" — retourne une liste vide si l'intention ne matche rien plutôt que de mélanger.
  - `_retrieve_docs_for_question()` : réordonnancement de la cascade de repli pour que **l'intention ne soit jamais abandonnée** (domaine+intention+secteur → domaine+intention+secteur-élargi → domaine+intention seul avec post-filtre secteur en Python).
  - `RAG_PROMPT` : remplacement de la règle "Minimum 3 / Maximum 5 cas" par une règle absolue d'anti-hallucination — ne jamais présenter plus de cas que ceux réellement fournis, ne jamais en inventer pour atteindre un minimum.
  - `_build_rag_prompt_from_docs()` : suppression du bloc mort qui laissait croire à un minimum de 3 cas forcé (jamais atteint en pratique).
- ✅ **Tests de non-régression ajoutés** (`backend/tests/test_haystack_rag.py`) : 3 nouveaux tests couvrant (1) `build_pool` ne mélange plus les intentions, (2) `build_pool` filtre toujours correctement quand un vrai match existe, (3) `_retrieve_docs_for_question` ne supprime jamais la condition d'intention dans sa cascade de repli. **9/9 tests passent.**
- ✅ **Build & déploiement :**
  - ACR build (run `ddy`, Succeeded) → image `acravoulia97186.azurecr.io/avoulia-backend:v2-fix-marketing-intent-202608251231`
  - Container App `avoulia-backend` mis à jour sur `rg-avoulia-fr-dev` → nouvelle révision `avoulia-backend--0000023`, 100% du trafic, `/health` → `200 OK`, démarrage confirmé sain dans les logs.
- 🧪 **À valider en prod :** rejouer le scénario "objectif = Créer des contenus marketing" et vérifier que Q3 et les cas suggérés restent cohérents avec l'intention choisie, et que le nombre de cas affichés correspond toujours au nombre de cas réellement sélectionnables.
- ⚠️ **Pour Simplon (handoff) :** cette classe de bug vient d'un anti-pattern récurrent ("fallback silencieux vers tous les documents/toutes intentions quand le filtre strict est trop restrictif"). Si de nouveaux mismatches apparaissent après reprise du code, chercher d'abord des patterns similaires `... if ... else docs` / abandon de filtre dans `haystack_rag.py` avant d'ajouter un nouveau fallback.

### Update 2026-07-15
- 🔧 Régression frontend identifiée sur le bundle Azure Container Apps (`lastSuggestedCases is not defined`)
- ✅ `HomeView.vue`, `ChatView.vue` restaurés, et `frontend/env.d.ts` complété pour les imports `.vue`
- ✅ Image frontend reconstruite et poussée: `acravoulia97186.azurecr.io/avoulia-frontend:v2-202607151604`
- ✅ Container App `avoulia-frontend` mis à jour sur `rg-avoulia-fr-dev`
- ✅ Validation live réussie sur la révision `avoulia-frontend--0000003` et sur l’URL principale avec cache-buster
- 🔧 Nouveau point à corriger: les liens parcours doivent inclure un court texte d'accompagnement, et le backend doit utiliser le mapping local des slugs statiques plutôt qu’un hash de fallback

### Update 2026-07-15 — parcours fix
- ✅ `backend/app/parcours_util.py` lit désormais `backend/app/static/parcours/mapping_uc_hash.csv` par défaut
- ✅ Mapping généré à partir des pages statiques existantes (1025 lignes)
- ✅ Backend redeployé sur `avoulia-backend--0000019`
- ✅ Parcours UC-0569 vérifié en live: la page s’ouvre bien sur `action-8khzcn5jmb.html`

---

## 📐 Vision & Architecture

### Objectif V2
Ajouter au système Avoulia existant (backend RAG + frontend Vue) :
1. **Parcours pages** — Guidance step-by-step post-diagnostic (6 étapes ~ 2.5h)
2. **Telemetry** — Tracking complet du funnel chat → RAG → parcours → completion
3. **Dashboard** — KQL queries + Azure Workbook pour monitoring

### Flux utilisateur complet
```
PME accède chatbot
    ↓ [TELEMETRY: chat_session_start]
Pose question libre
    ↓ [TELEMETRY: user_message_sent]
Backend RAG cherche cas dans Excel + retourne réponse
    ↓ [TELEMETRY: rag_result_returned]
Chatbot propose URL parcours
    ↓ [TELEMETRY: parcours_url_proposed]
PME clique sur URL → Page parcours
    ↓ [TELEMETRY: parcours_page_opened]
Étape 1: PME valide cas (3 questions)
    ↓ [TELEMETRY: parcours_step_1_completed]
Étapes 2-6: PME effectue actions de mise en œuvre
    ↓ [TELEMETRY: parcours_step_*_completed]
Quick win: Option copy/test prompt
    ↓ [TELEMETRY: quickwin_copy/open/close]
Session end
    ↓ [TELEMETRY: chat_session_end]
Dashboard agrège tous les événements → Funnel, retention, bounce rate
```

### Contraintes non-négociables
- ⚠️ **Restitution verbatim octet-pour-octet** des champs Excel (jamais reformuler LLM)
- ⚠️ **Pré-filtrage métadonnées** AVANT recherche vectorielle (domaine, secteur, intention)
- ⚠️ **Parcours non-indexées** (`X-Robots-Tag: noindex`, meta noindex)
- ⚠️ **AVOULIA_SALT fixe en prod** — rotation = 404 cascade (toutes hashes changent)
- ⚠️ **Base Excel privée** — jamais exposée publiquement

---

## 📊 Décisions prises (D1-D7)

| ID | Sujet | Décision | Rationale | Statut |
|---|---|---|---|---|
| **D1** | Restitution données | Verbatim octet-pour-octet, pas reformulation LLM | Confiance PME + compliance | ✅ Validée |
| **D2** | Pré-filtrage metadata | Avant vector search (domaine/secteur/intention) | Réduit bruit + améliore pertinence | ✅ Validée |
| **D3** | Base Excel protégée | Jamais exposée publiquement ; accès via API seulement | Sécurité données clients | ✅ Validée |
| **D4** | Plateforme pilote | Azure Static Web Apps (parcours pages statiques) + SWA Deployment | Free tier, itération rapide | ✅ Déployée |
| **D5** | UX Reordering | Étape 1 (validation) en haut → Quickwin en bas accordion | Psychology: valider d'abord, engagement mental | ✅ Implémentée (commit 99d5cbb) |
| **D6** | Chantiers A/C/D | Config paramétrisée + Bicep IaC + App Insights 8 events + KQL 8 queries | Production-ready, handoff-easy | ✅ Créés |
| **D7** | Chantier E (mapping) | Load `mapping_uc_hash.csv` depuis Azure Blob Storage (vs hardcoded) | Clean, scalable, versioned | ✅ Approuvée |

---

## 📁 Chantiers & Livrables

### Chantier A: Configuration & Infrastructure as Code

#### A.1 — Config Files ✅
- **Files:**
  - `config/environments/dev.perso.json` — Params dev (francecentral, rg-avoulia-fr-dev)
  - `config/environments/prod.officiel.sample.json` — Template prod (westeurope, rg-avoulia-fr-prod)
- **Content:** Environment-specific settings (region, resource names, SKUs, retention)
- **Status:** ✅ Created

#### A.2 — Bicep IaC ✅
- **File:** `infra/main.bicep`
- **Deploys:**
  - Log Analytics Workspace (30/90 days retention)
  - Application Insights (tied to LAW)
  - Storage Account + Blob Container (for mapping CSV)
- **Outputs:** Instrumentation key, connection string, storage key
- **Status:** ✅ Created

#### A.3 — Deployment Guide ✅
- **File:** `HANDOFF.md` (Phase 1: Azure Infrastructure)
- **Instructions:** Step-by-step Bicep deployment + outputs capture
- **Status:** ✅ Created

---

### Chantier B: Parcours Pages (Pilot Phase)

**Status:** ✅ COMPLETE (deployed 2026-07-10)
- 28 parcours pages live on SWA
- UX reordered (Étape 1 first, quickwin bottom accordion)
- All pages HTTP 200, noindex headers, verbatim verified
- CI/CD pipeline: SWA GitHub Actions workflow

**Note:** Pilot uses 28 sample cases from `pilote.txt`. Production will regenerate 1025 pages from full Excel.

---

### Chantier C: App Insights Instrumentation ✅

#### Frontend Telemetry
- **File:** `frontend/src/appinsights-instrumentation.html`
- **Events tracked:**
  1. `chat_session_start` — Page load (chatbot)
  2. `user_message_sent` — PME asks question
  3. `rag_result_returned` — Backend returns case
  4. `parcours_url_proposed` — Chatbot shows URL link
  5. `parcours_page_opened` — PME clicks parcours URL
  6. `parcours_step_*_completed` (1-6) — Étape completion
  7. `quickwin_copy` — Quick win copy action
  8. `quickwin_open/close` — Accordion toggle
- **Attributes:** Session ID (sessionStorage hash), Case hash, Score, Timestamps
- **RGPD:** No cookies, no persistent ID, no IP, no PII; anonymous session hash
- **Status:** ✅ Created

#### Integration Points
- Import snippet into `frontend/index.html` `<head>` OR `frontend/src/main.ts`
- Add `data-case-hash="{{ case_id }}"` to parcours page body
- Ensure `VITE_APPINSIGHTS_INSTRUMENTATION_KEY` env var is set (GitHub Secret)

---

### Chantier D: Analytics & Dashboard ✅

#### KQL Queries
- **File:** `infra/kql-queries.kql`
- **Queries (8):**
  1. **Funnel completion %** — Chat → RAG → Parcours → Step 1 → Step 6
  2. **Top 10 cases** — Most visited parcours pages
  3. **Quickwin copy rate** — % sessions with copy action
  4. **Retention (J+1/3/7)** — Returning sessions
  5. **Mode execution split** — Outil vs no_code (needs mapping join)
  6. **Timeline** — Events per hour (last 24h)
  7. **Bounce rate** — Chat start → no RAG hit
  8. **Avg steps completed** — Per session median
- **Status:** ✅ Created

#### Azure Workbook
- **File:** `infra/dashboards/avoulia-parcours-dashboard.json`
- **Panels:**
  - Funnel completion % (stacked column)
  - Top 10 cases (table)
  - Quickwin engagement (donut)
  - Events timeline (area chart, last 24h)
- **Status:** ✅ Created

#### Deployment
- Import via CLI: `az monitor workbooks create --definition @infra/dashboards/avoulia-parcours-dashboard.json`

---

### Chantier E: Backend Enhancement ✅

#### Endpoint Modification
- **File:** `backend/CHANTIER_E_BACKEND_ENDPOINT.py` (template)
- **Change:** Chat endpoint `/api/v1/chat` returns:
  ```json
  {
    "answer": "Steps Q2-Q3",
    "case_id": "UC-0042",
    "case_hash": "vn38reuyw7",
    "parcours_url": "https://avoulia.azurewebsites.net/action/vn38reuyw7/",
    "matching_score": 0.92
  }
  ```
- **Hash generation:** Deterministic via `SHA256(case_id + AVOULIA_SALT)`
- **Key env vars:**
  - `AVOULIA_SALT` — Fixed forever (prod)
  - `PARCOURS_BASE_URL` — Hardcoded domain
  - `APPINSIGHTS_INSTRUMENTATION_KEY` — For backend telemetry (optional)

#### Mapping Strategy
- **Option 1 (Current):** Deterministic hash generation (no storage needed)
- **Option 2 (Future):** Load mapping CSV from Blob (`mapping_uc_hash.csv` in `parcours-mappings` container)
  - If using: backend queries Blob on startup, caches in memory
  - Migration: Pre-generate CSV from Excel, upload once

- **Status:** ✅ Template created; implementation needed (Phase 2 for Simplon)

---

### Handover & Documentation ✅

- **File:** `HANDOFF.md`
- **Content:**
  - Overview (flow, components)
  - Phase 1: Azure Infrastructure (Bicep)
  - Phase 2: Backend enhancement (chat endpoint)
  - Phase 3: Frontend integration (telemetry)
  - Phase 4: Parcours pages (reference)
  - Phase 5: Dashboard setup
  - Environment variables table
  - Validation checklist
  - Troubleshooting guide
- **Status:** ✅ Created (production-ready for handover to Simplon)

---

## 🔄 Dependencies & Roadmap

### Completed (Chantiers A-D)
```
[Config Files (A1)] ✅
        ↓
[Bicep IaC (A2)] ✅
        ↓
[App Insights (C)] ✅
        ↓
[KQL Queries (D)] ✅
        ↓
[Workbook Dashboard (D)] ✅
```

### Ready for Next Phase
```
[Backend Enhancement (E)] → Implement chat endpoint (Simplon)
        ↓
[Integration Testing] → Verify telemetry flow
        ↓
[Production Deployment] → Deploy to prod tenant
        ↓
[Monitoring & Optimization] → Monitor funnel metrics, tune retention
```

---

## 📈 Success Metrics (Post-Launch)

| Metric | Target | Measurement |
|---|---|---|
| **Funnel completion** | >50% (chat → RAG) | KQL Query #1 |
| **Parcours page open rate** | >40% (from chat) | KQL Query #1, funnel_step3 |
| **Step 1 completion** | >70% (of opens) | KQL Query #1, funnel_step4 |
| **End-to-end (step 6)** | >30% (of opens) | KQL Query #1, funnel_step6 |
| **Quickwin engagement** | >20% (copy/test) | KQL Query #3 |
| **Retention (J+1)** | >15% | KQL Query #4 |
| **Bounce rate** | <20% | KQL Query #7 |
| **Avg steps** | >3 (median) | KQL Query #8 |

---

## 🚀 Deployment Checklist (For Simplon)

### Pre-Deployment
- [ ] Code review: backend changes (chat endpoint), frontend integration
- [ ] Security review: RGPD, AVOULIA_SALT, storage access
- [ ] Testing: local E2E (chat + parcours + telemetry)

### Deployment
- [ ] Bicep: Deploy infrastructure to prod RG
- [ ] Secrets: Set all env vars in Container Apps / Key Vault
- [ ] Backend: Build & push new image to ACR, update Container App
- [ ] Frontend: Build & deploy (App Insights key injected)
- [ ] Pages: Generate 1025 parcours pages, upload to hosting

### Post-Deployment
- [ ] Smoke test: Chat endpoint returns parcours URL
- [ ] Telemetry: Events flowing to App Insights (5-10 min delay)
- [ ] Dashboard: Workbook shows data, KQL queries non-empty
- [ ] Monitoring: Set up alerts (e.g., bounce rate > 30%)

---

## 📝 Journal

- **2026-07-08** — V2 project initiated; clarified requirements (telemetry chat → parcours)
- **2026-07-09** — Designed chantiers roadmap (A/C/D/E)
- **2026-07-10 17:48** — UX reordering decision (D5); template updated, deployed to SWA
- **2026-07-10 18:38** — Chantiers A/C/D/E created:
  - A1: Config files (dev/prod)
  - A2: Bicep IaC
  - C: App Insights snippet (8 events, RGPD-safe)
  - D: KQL queries (8) + Workbook JSON
  - E: Backend endpoint template
- **2026-07-10 18:45** — HANDOFF.md created (production-ready guide for Simplon)

---

## 🔐 Security & Compliance Checklist

- [ ] **Verbatim compliance:** No LLM reformulation of Excel fields
- [ ] **Metadata filtering:** Pre-filter domain/intention BEFORE vector search
- [ ] **Excel protection:** Never expose base publicly; API access only
- [ ] **AVOULIA_SALT:** Fixed forever in prod; never rotate (hash stability)
- [ ] **Noindex headers:** All parcours pages have `X-Robots-Tag: noindex`
- [ ] **RGPD:** No cookies, no persistent ID, no IP logging (Azure masks); session hash only
- [ ] **Secrets management:** Key Vault (prod), GitHub Secrets (dev)
- [ ] **Access control:** Storage access via SAS/connection string (no hardcoded keys)

---

## 📞 Questions & Escalations

**Q:** Can we rotate AVOULIA_SALT in production?  
**A:** ❌ NO. All case hashes depend on it. Rotation = 404 cascade. Keep forever.

**Q:** Should backend handle mapping CSV or frontend?  
**A:** Backend (server-side lookup) — cleaner, no exposure of mapping logic. Frontend just displays URL.

**Q:** What if telemetry key expires?  
**A:** Update GitHub Secret + re-deploy frontend. App Insights resources don't expire, key can be regenerated.

**Q:** How to backfill telemetry for old sessions?  
**A:** Can't; telemetry only tracks new sessions. Historical analysis via Excel + manual audit.

---

**Document maintained by:** Eneric (with Copilot assistance)  
**Last updated:** 2026-07-10 18:45 UTC+2  
**Next review:** Post-handover to Simplon (post-implementation)
