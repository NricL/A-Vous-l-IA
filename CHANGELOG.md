# Avoulia — Changelog v1 → v2 (synthèse d'onboarding)

## Candidate de test Azure — préparation du 13 septembre

Hébergement cloud explicite pour PUBLIC_PAGES, distinct du bot stable : origines/HTTPS/pairs proxy contrôlés, authentification Azure par configuration existante sans CLI/fallback, requêtes bornées et sessions monoréplique. Packaging en liste blanche et image finale sans payload privé hérité ; dépendance du lecteur public déclarée, contrôles Python 3.11 et démarrage sous utilisateur non privilégié.

Frontend `/preview` compatible Azure et base GitHub Pages, identité AVIA bleue restaurée, télémétrie désactivée sur tout le périmètre preview. La racine stable ne change pas de flux. L'ouverture cross-site des seuls documents parcours est admise et conserve les contrôles de révision ; import de type HTTP corrigé pour Python 3.11.

La livraison de test a été demandée, pas la promotion du site principal. Les images sont préparées en privé avant aperçu exact/confirmation du lot. La v462 privée n'est pas incluse ; latence et portée de certaines suggestions restent des travaux ouverts. Les mentions « non publié/non déployé » ci-dessous décrivent les étapes historiques.

## Préversion PUBLIC_PAGES — correctif local de récupération et RAG réel

**Non publié/non déployé.** Suppression de la troncature des candidats à5 avant sélection ; plafond conservé après rapprochement des résultats. Filtres métier et identités inchangés. Tests intrafiltre et script de diagnostic borné ajoutés.

Snapshot privé de champs **déjà publiés** :1 021fiches v4.6.1 et4historiques exclues. Embeddings/sélection Azure existants, qualification locale explicite, vérification indépendante de portée, consentement et diagnostic de source. Aucun chargement du classeur General ni de la candidate privée v462 dans ce mode.

Rendu des vrais cas publics dans les nouveaux parcours locaux, sans inventer le mode absent, avec contexte séparé et URL liée à la révision. PUBLIC_API conserve son ancienne page publiée. Télémétrie locale supprimée aussi pour les alias de `/preview`.

Essais réels ont retrouvé le cas marketing attendu et écarté plusieurs correspondances injustifiées. Une suggestion secondaire web reste trop permissive et la latence doit être améliorée avant production. Les contrôles ne constituent pas une certification de toute formulation possible.

## 13 septembre — revue complète privée après autorisation locale

Accès local brut explicitement autorisé à16:43. Copie v461 identique et étiquette préservée, inventaire complet et revue documentaire des1 021cas consolidés dans un classeur de revue labellisé. Aucune modification des cellules source ; propositions et arbitrages restent distincts de leur application.

La documentation de reprise est actualisée sans exporter le contenu des revues. Nouveau diagnostic à traiter : un cas peut être manqué dans le périmètre initial, même si une réorientation retrouve une alternative. Aucun changement applicatif, déploiement ou raccordement au RAG réel dans ce lot.

## 13 septembre — préversion locale du protocole et des parcours

**Non publié, non déployé.** Nouveau serveur `app.preview:create_app` et route frontend `/preview` explicitement activables uniquement en local.16cas fictifs servent à essayer les états/transitions, pas à simuler une couverture réelle des1 021cas ou une recherche RAG.

Choix canoniques, validation des versions/question, rejet des retours périmés et requêtes doubles, saisie déterministe de numéros/libellés, recherche principale séparée de la proposition de réorientation, acceptation/refus et retour arrière. Fiche source courte puis seul bouton parcours ; pas de coaching après sélection.

Raccordement au générateur parcours associé via `preview_parcours.py`, rendu sans lecture de workbook, contexte local distinct, échappement, protections d'origine/loopback et liens liés à la révision sélectionnée. Le frontend conserve les brouillons après erreur sans transition et affiche les erreurs de récupération. Tests spécifiques et essais navigateur locaux, sans changement de production.

Dans le dépôt parcours associé : gabarit et prompts de préparation/vérification/réutilisation révisés avec six étapes inchangées. Les données privées et pages en ligne ne sont pas modifiées. Lecture complète du catalogue encore bloquée ; aucune correction Excel ni revue exhaustive revendiquée.

## 13 septembre à 12:36 — banc QUAL-01 local et recommandations révisées

- Contrat dans HANDOFF ; corpus `backend/tests/fixtures/qualification_reference.json`, banc `backend/scripts/evaluate_qualification.py` et tests `backend/tests/test_qualification_reference.py`.66scénarios mécaniques,63conformes,3écarts cibles visibles,14domaines couverts par numéro/libellé. Pas de précision métier générale ni de correction runtime déduite du résultat.
-102tests ciblés réussis ; code1 de l'évaluateur maintenu pour ses trois écarts. Entrées invalides, sorties écrasées et appels réseau/données réelles refusés ; absence de Git explicitée dans les contextes exportés. Les futurs paquets de validation doivent inclure le script et sa fixture, pas seulement les tests Python.
- Premier essai conjoint : réorientation humaine confirmée nécessaire pour retrouver un cas existant classé ailleurs. Proposition ORI-01 ajoutée à la roadmap, sans changement silencieux des filtres et sans implémentation. Maintien des recommandations sur contenu complet, premier essai, contrôle du résultat et réutilisation.

Travaux locaux non publiés. Application `d02ffad`, catalogue v461 et parcours en ligne inchangés ; aucune autorisation de nouveau déploiement à ce stade.

## 13 septembre à 11:55 — roadmap qualification/contenu révisée, non implémentée

**Quoi / pourquoi :** priorité donnée à la bonne qualification et à la fidélité au catalogue, avant le naturel. Qualification explicite domaine/secteur/objectif conservée ; classification automatique par LLM et pivot généraliste exclus du prochain lot. Amélioration de contenu et des parcours prévue sur les **1 021 cas**, et non sur vingt cas seulement.

**Où :** plan détaillé et critères de sortie dans `ROADMAP.md`, implications de protocole et points de reprise dans `HANDOFF.md`, décision et périmètre dans `SUIVI_PROJET.md`, résumés dans README/IMPLEMENTATION_SUMMARY et distinction du déploiement dans `.azure/plan.md`.

**Ordre retenu :** QUAL-01 référence de qualification → QUAL-02 état explicite → QUAL-03 dialogue maîtrisé ; CONT-01 revue complète après fixation des critères, en parallèle lorsque possible → PAR-01 parcours ; puis REC-01 et LIV-01. Les critères distinguent validité technique, pertinence métier et facilité d'usage. Les situations adverses et la conservation des versions/hashes sont explicites.

**Statut :** documentation locale uniquement. Aucun nouveau comportement, code, schéma métier ou contenu source implémenté ; ni nouvelle version Excel ni publication. Le dernier code livré reste `d02ffad`, reçu `e895cab`. Les sections suivantes décrivent les réalisations antérieures.

## 13 septembre — publication et déploiement du lot UX-01 à UX-05

Commit `d02ffad`, Pages `34746510034` et CI `34746509999` réussies. Backend `avoulia-backend--ux-20260913-d02ffad` et frontend Azure de même suffixe Healthy, 100 % du trafic. Les entrées « locales » ci-dessous décrivent la préparation désormais livrée.

Images construites depuis le commit approuvé : backend `058fe52822fea24c4e52e17b27242480f3ab96771b883243d8bad7efb2aaaafb` (ACR `dd2k`) et frontend `2ae5e263bb60ecf245c4ad59658de07323a902da858d60c42cb26c22d4cfee18` (`dd2m`). Overlay backend limité aux deux modules Python modifiés ; classeur, mapping et 1 021 pages actuelles plus quatre historiques hérités sans modification.

Recette dans l'image Python 3.11 : 212 tests backend (un test Node ignoré), huit de rapprochement, contrôle du payload hérité. Candidate puis URL normale : quatre exemples Q3 sans pipes pour Cabinet & conseil, besoin magasin réutilisé, détail verbatim HTTP/SSE, refus hors sujet et reprise, neuf pages inchangées et quatre exports privés en404. Pages mobile390px : bouton unique puis bonne fiche/lien, retour à une liste de trois cas et choix du troisième ; frontend Azure desktop sans débordement. Les exemples restent les formulations de la base, pas une réécriture éditoriale.

Mode Single rétabli, ancienne r3 inactive ; anciennes images et définitions conservées pour rollback. L'index local de la nouvelle réplique a été reconstruit depuis la v461 embarquée, sans effacer l'ancien. Pas de livraison Simplon ou de publication du classeur.

## 13 septembre — finalisation publiée ; corrections UX engagées

**Livré :** chatbot `24e145b`, parcours `a500a22`, GitHub Pages et frontend Azure `avoulia-frontend--v461-20260913`. Vitrine : 1 021 cas, 14 domaines métier, 71 intentions ; backend r3 et catalogue v461 inchangés.

**Ce lot documentaire :** état de finalisation rapproché entre README, suivi, roadmap et handoff. Les mentions anciennes de publication à terminer ne décrivent plus l'état courant.

**Corrections locales UX-01 à UX-05, non déployées :**

- `frontend/src/views/HomeView.vue` : le seuil de deux lignes numérotées empêchait le bouton du cas unique. Les boutons utilisent maintenant les métadonnées de la réponse, conservées par message ; un cas donne « Choisir ce cas », plusieurs donnent « Cas N », avec titre accessible. Le retour à la liste restaure également ses identités et son ordre. Aucune sélection sur Q3/refus/détail ; le CTA parcours reste autoritaire côté backend.
- `backend/app/haystack_rag.py`, `build_pool` : les exemples étaient des groupes de situations, simplement triés par score de secteur. Les secteurs non applicables restaient dans le pool. Filtre d'éligibilité partagé avec Q2, intention conservée, séparation des pipes puis dédoublonnage ; `rag_constants.py` borne l'affichage à quatre situations. L'intention non résolue n'élargit plus les exemples.
- `_user_probleme_q3_text` : élargissement prudent des formulations explicites de tâche, objectif et difficulté ; exclusion des salutations, présentations seules et commandes de sélection. Les besoins initiaux restent réutilisables ; les réponses Q3 liées à d'anciens choix sont invalidées. La dernière clarification utile prévaut.
- `_build_rag_prompt_from_docs` : contrôle explicite des conditions nécessaires à chaque recommandation, y compris secondaire. Une justification « si vous… » ne compense pas un fait métier absent du besoin. Les conditions d'exécution et garde-fous légitimes ne sont pas interdits lexicalement.
- `backend/scripts/evaluate_chat_relevance.py` : suite opt-in `stock-assumptions`, quatre scénarios fictifs (saisonnalité absente/présente, garde-fou conditionnel, aucun cas adapté), deux ordres possibles, huit appels maximum. Le banc chantier par défaut reste inchangé.

Régressions dans les suites existantes `test_haystack_rag`, `test_chat_regressions`, `test_chat_relevance`, `test_case_selection_prompt`, `test_relevance_evaluation` et `frontend/scripts/check-chat-state.mjs`. 171 tests backend ciblés avec intégration catalogue, 31 frontend ; build/types et contrôle des composants actifs réussis. Frontend construit parcouru à 390/1280 px avec un backend SSE fictif, notamment sélection du cas unique et retour au deuxième cas. Une première invocation backend avait omis le chemin des helpers de tests ; relance avec `PYTHONPATH=tests`, sans installation supplémentaire.

**Évaluation modèle UX-05 terminée :** huit appels sur le `gpt-5-mini` existant, quatre scénarios fictifs dans les deux ordres de candidats ; huit réponses complètes conformes aux attentes, pas de troncature, erreur réseau ou divergence d'ordre. Le cas saisonnier n'est retenu que lorsque le besoin l'établit ; un « si » de garde-fou n'exclut pas le bon cas. Rapport brut privé, sans lecture du catalogue ni modification des attentes après résultat. Ce passage ne mesure pas la précision de production ou tout le parcours utilisateur.

Pas de changement Excel, index, mapping, gabarit parcours, modèle ou déploiement par ce lot local. La reconnaissance française reste déterministe et ne garantit pas toutes les formulations.

## 13 septembre — v461 et parcours déployés sur DEV

**Résultat :** backend `avoulia-backend--v461-20260913-r3`, image `sha256:9c356b0643a3313709f434d73505b6c7e98b49fca735ad869983b0e835410c1b`,100% trafic, mode Single. Texte des fiches et parcours autorisé explicitement par Eneric à06:42 ; classeur, audits et mapping restent privés.

**Pourquoi / où :**
- `app/parcours_static.py` et `app/main.py` : seules les pages et ressources web attendues sont servies ; refus des classeurs, CSV, exports et chemins privés.
- `app/scripts/validate_release_payload.py`, `Dockerfile.dev-catalogue-release` et `Dockerfile.dev-catalogue-code-fix` : contrôle de la cohérence source/mapping/pages, conservation des pages historiques, mise à l'écart des exports hérités et tests dans l'image avant publication.
- `app/haystack_rag.py` : questions Q1.5/Q2/Q3 déterministes à partir de l'état validé ; sélection des cas confiée à un prompt dédié, sans instructions contradictoires de qualification. Pré-filtres, ordre source et détail verbatim maintenus.
- Dépôt parcours associé, merge local `a500a22` : rapprochement des évolutions distantes et de la génération sûre, avec contexte métier dans les prompts et consignes d'essai autorisé.

**Recette :**198 tests backend,8 de rapprochement, tests d'image Python3.11 avec un test Node explicitement ignoré ; scénarios réels sur candidate puis URL normale, trois refus hors sujet consécutifs à chaque passage, HTTP/SSE, pages et mobile390px. Une régression de sélection a déclenché un rollback de r2 avant la correction finale ; aucun échec n'est masqué.

**Publication finalisée :** les chiffres de vitrine (`1 025` → `1 021`, `Secteurs couverts` → `Domaines métier`) et les derniers commits source/documentation sont publiés. Le catalogue v461 reste servi par le backend r3.

## 12 septembre — consolidation privée et préparation de l'intégration

**Quoi / pourquoi :** nouvelle version du classeur privé sauvegardée après revue des situations, classements, premières actions, prérequis et garde-fous. Les textes de recherche dépendants sont synchronisés et le catalogue est placé avant les onglets de travail. Les données, preuves exactes et décomptes restent hors du dépôt public.

**Impact applicatif identifié :** import dépendant de la première feuille ; options de secteurs statiques ne couvrant pas tous les rattachements métier. Les travaux INT-01/02 doivent corriger ces contrats et préparer une génération depuis une source explicite, avec conservation du mapping et des six étapes.

**Où / statut :** cadrage dans `ROADMAP.md`, `SUIVI_PROJET.md`, `HANDOFF.md` et `.azure/plan.md`. Les contrôles de l'ancienne livraison ne valent pas validation de ce nouveau lot. Aucun index, page parcours ou backend mis à jour par la sauvegarde Excel ou cette documentation.

**Autorité et limites :** arbitrages de contenu délégués par Eneric, pas de validation individuelle à redemander ; versionnement, confidentialité et confirmation préalable des publications demeurent requis. Package Simplon toujours différé.

**Indexation préparée localement :** `backend/app/scripts/index_documents.py` propose `--validate-only` sans Chroma/embeddings et `--require-empty` pour un index candidat. Toutes les sources sont chargées avant un éventuel `--clear` ; source absente, vide ou invalide et nombre écrit incohérent donnent un échec. `backend/entrypoint.sh` ne transforme plus une erreur de lecture en index vide et ne démarre plus après une indexation échouée. Couverture synthétique dans `test_index_preflight.py` et `test_index_entrypoint.py`. Aucun index réel reconstruit par ces modifications.

**Import et secteurs implémentés :** sélection explicite de la feuille métier et validation des données dans `backend/app/services/ingest.py` ; secteurs dérivés des métadonnées, numéros historiques conservés et cache invalidé dans `backend/app/haystack_rag.py`. Un conflit de dimension d'embeddings ne supprime plus automatiquement la collection. Tests dans `test_catalogue_integration.py` et `test_chat_regressions.py`.

**Parcours, dépôt associé :** `pipeline/genere.py` prépare un dossier neuf à partir de source/mapping explicites, garde les associations historiques, supporte les layouts existant et backend et un lien de retour HTTP(S) paramétrable dans le gabarit. `publish.yml` est manuel et nécessite l'autorisation de publication ; le mapping n'est ni servi ni exporté en artefact. Couverture dans `test_catalogue_integration.py`, `test_parcours_ux.py` et `test_parcours_publication_gate.py` du chatbot. Ces fichiers du dépôt associé ne sont pas livrés par un commit du seul dépôt chatbot.

**Résultat :** 182 tests backend/générateur et 19 tests frontend, types contrôlés. Vérification en mémoire sur le catalogue réel sans embeddings ni pages écrites. Limites conservées dans le suivi : runtime local différent de l'image de production, exposition des contenus et cible à confirmer avant mise en ligne.

## Publication effective du 10 septembre

**Commit** `4033e8e` : corrections chatbot et documentation publique synchronisées dans `main`. Workflow Pages34461697021 et CI34461697054 réussis ; contrôles sur https://nricl.github.io/A-Vous-l-IA/ : nouveau bundle, mobile390px, qualification et retour arrière après absence de correspondance. Le backend reste0045 ; ni les données ni les gabarits parcours n'ont été redéployés par Pages. Détails et limites de la CI dans `SUIVI_PROJET.md`.

## 10 septembre — synchronisation publique du code et de la documentation

Publication autorisée après nettoyage : correction de la mention de dépôt privé, identifiant d'abonnement retiré au profit d'un paramètre explicite, aucune donnée source ni rapport privé ajouté. Les workflows CI/Pages exécutent les régressions d'état frontend avant publication. Le build Pages utilise le sous-chemin du dépôt et appelle le backend dev0045. Résultat effectif du workflow à consigner dans le suivi.

## 10 septembre à 11:20 — canal GitHub de référence

**Décision** : toutes les mises à jour doivent synchroniser code et documentation dans `NricL/A-Vous-l-IA`, et être contrôlées sur https://nricl.github.io/A-Vous-l-IA/. Publication Pages de rattrapage non encore effectuée.

**Changement GitHub préparé** : ajout du contrôle existant `npm run check:chat` dans CI et dans le build Pages, avec typecheck avant publication Pages. Aucun nouveau runner ou dépendance. Les workflows n'ont pas encore été exécutés sur GitHub pour ce lot.

## 10 septembre — livraison dev sans modification des données (déployée)

**Quoi** : message explicite lorsqu'aucun cas fiable ne peut être proposé, possibilité de préciser le besoin ou revenir via le stepper conservé ; aucun ID/source/CTA fictif. Diagnostic du banc corrigé pour distinguer questions numérotées de clarification et liste inconnue (rapports initiaux conservés).

**Où** : `backend/app/haystack_rag.py`, `backend/app/routes/chat.py`, tests de pertinence ; `frontend/src/views/HomeView.vue`, contrôle Node d'état ; script/tests du banc d'évaluation. Les corrections qualification/mobiles/listes précédemment locales sont incluses.

**Déploiement initial** : ACR dd2a/dd2b, backend0044/frontend0023 (tag `v2-nomatch-20260910`). Overlay backend code-only sur digest0043, sans remplacement des pages, du mapping ou de la base. Le pitch et les changements de gabarit CHAT-04/05/06 restent exclus pour éviter une livraison partiellement régénérée.

**Réserve en cours** : test live révèle une sélection initiale numérique « 13 » ignorée après le seul accueil ; correction complémentaire requise avant clôture. Les contrôles live du flux guidé normal, no-match et clarification sont positifs. Détails des images et résultats dans `SUIVI_PROJET.md`.

**Clôture** : la réserve initiale est levée par backend0045 (build ACR dd2c, tag `v2-nomatch-20260910-r2`, digest `9408ae9a6d8ffc1275a6b6c03f5bba5bbfbb59120f14d4b20b87c44b06b414ea`). Frontend0023 conservé. Parcours live complet recontrôlé à partir du premier13, puis absence de correspondance, clarification, liste/détail/lien et retour arrière. No-match non-stream confirmé sur0045 ;106 tests backend/19 frontend. Données et pages héritées de0043 inchangées, modifications de gabarits locales exclues, package Simplon toujours différé.

**Diagnostic d'évaluation v2** : questions numérotées reconnues uniquement après un refus explicite et avec formulations de clarification bornées ; listes inconnues toujours rejetées/inconclusives. Relecture hors ligne du rapport existant : deux refus sans correspondance conformes, deux divergences aux hypothèses synonymes inchangées. Rapports initiaux préservés, aucun nouvel appel modèle pour cette relecture.

**But de ce document :** permettre à un dev Simplon — **notamment celui qui a participé à la
v1** — de comprendre **en une lecture** tout ce qui a changé entre la v1 publique et la v2
livrée. C'est le point d'entrée « traçabilité » du projet (contrainte C2, cf.
[`README.md`](./README.md)).

- **Détail chronologique fin :** [`SUIVI_PROJET.md`](./SUIVI_PROJET.md)
- **Reprise technique & pièges :** [`HANDOFF.md`](./HANDOFF.md)
- **Évolutions à venir :** [`ROADMAP.md`](./ROADMAP.md)
- **Historique exact :** `git log` (34 commits, `ab4b21a` → `d02ad1d` au 2026-08-26)

> Convention : chaque entrée indique **Quoi / Pourquoi / Où (fichiers)** et le **commit**.

## Travaux locaux du 9 septembre 2026 — non publiés, non déployés

### Complément du 10 septembre — banc d'évaluation du modèle réel

**Quoi / pourquoi** : ajout d'un script opt-in comparant les cas retenus par le modèle réel à des attentes techniques sur cas fictifs, en distinguant exclusion sémantique, échec de parsing, troncature et erreur de transport. Les tests précédents simulaient les réponses du modèle et ne mesuraient pas cette étape.

**Où** : `backend/scripts/evaluate_chat_relevance.py`, `backend/tests/test_relevance_evaluation.py`. Premier rapport privé de session : `chat03-real-model-evaluation.json`. Le script n'est pas appelé par l'application ; aucun changement du code de production dans ce lot.

**Premier résultat borné** : 16 tentatives sur le modèle configuré pour la route streaming, une 429, huit troncatures avec plafond de 1 200 tokens (raisonnement compris). Six attentes satisfaites et une divergence sur les réponses complètes évaluables ; pas de taux global ni de preuve sur tout le catalogue. Reprise ciblée de quatre appels maximum en cours, sans changer le modèle.

**Résultat de la reprise du 10 septembre** : quatre réponses complètes sous plafond total de 6 000 tokens, même modèle/prompt, sans réglage de raisonnement supplémentaire. Deux rejets de tous les candidats hors sujet ; un diagnostic de format déclenché par des questions de suivi numérotées. Deux réponses par synonymes ajoutent le suivi d'actions à la synthèse : divergence aux attentes techniques, pas preuve d'irrélevance jugée par des utilisateurs. Résultat strict du banc conservé (1/4), sans réécrire les attentes pour faire passer les tests. Aucun correctif de production fondé sur ce seul petit échantillon.

**Reproductibilité** : sélection de scénarios, répétitions bornées, plafond 1–6 000 tokens, cible Azure explicite pour les appels réels, arrêt/non-succès en cas de troncature ou problème de transport et contrôle des empreintes à la reprise. Suite globale 95 tests ; script hors ligne par défaut. Voir `HANDOFF.md` pour l'exécution sans packaging.

**À 15:41 — périmètre confirmé** : package Simplon différé par Eneric avant toute création. Lectures de documentation seulement dans la phase envisagée ; reprise des corrections restantes, notamment CHAT-03. La procédure de reprise reste documentée sans assembler de livrable maintenant.

**Périmètre** : corrections ciblées approuvées, pas de pivot produit. Sources récupérées depuis le dépôt à `8f2d673`. Les réalisations du 31 août présentes dans la copie de déploiement doivent être préservées avant une future livraison ; la branche distante n'est pas une preuve de parité avec l'image déployée.

**CHAT-01 — mobile et accessibilité : changements source préparés.**
- **Quoi / pourquoi** : contraintes minimales flex/grid corrigées pour que la saisie et l'envoi restent visibles à 390 px ; retour à la ligne des chips, textes et boutons ; noms accessibles et focus clavier.
- **Où** : `frontend/src/views/HomeView.vue`.
- **Contrôles** : 23 observations de rendu isolé Edge, 320 à 1440 px et six phases simulées, sans backend réel. À 390 px, saisie x45..290 et bouton x298..330, au lieu d'un envoi hors écran. Ces contrôles de rendu n'ont pas été ajoutés comme suite persistante.

**CHAT-02 — qualification et état : changements source préparés, revue ciblée clôturée.**
- **Quoi / pourquoi** : réponse numérique interprétée dans l'étape attendue, réutilisation prudente des informations explicites antérieures, dépendances réinitialisées lors d'une correction ; le frontend applique l'état complet du serveur sans effacer ensuite son secteur. Les champs absents et les champs explicitement nuls restent distincts.
- **Où** : `backend/app/haystack_rag.py`, `frontend/src/views/HomeView.vue`, `frontend/src/api/chat.ts`.
- **Fiabilité** : retour arrière désactivé pendant le streaming et verrouillage immédiat de l'envoi ; correction du détail à contenu court mais champs riches conservée depuis le précédent déploiement.
- **Contrôles persistants** : `backend/tests/test_chat_regressions.py` et `frontend/scripts/check-chat-state.mjs` (`npm run check:chat`). Qualification en texte libre volontairement conservatrice : pas de compréhension sémantique universelle revendiquée.
- **Correctifs issus de revue** : filtres cohérents avec les secteurs composés et variantes multi-sectorielles, rejeu partagé de l'état et du besoin, fusion prudente d'un historique partiel avec l'état client, acquiescements reconnus comme réponses entières. Une phrase Q3 contenant « détails » reste un problème ; les demandes explicites comme « Donne-moi plus de détails » restent des sélections de cas, et non de nouvelles recherches.

**CHAT-03 — amélioration partielle uniquement.**
- **Quoi / où** : maintien des filtres métadonnées, suppression du repli abandonnant le secteur et de la surpondération lexicale par répétition, dans `backend/app/haystack_rag.py`.
- **Limite** : les quasi-correspondances sémantiques nécessitent une évaluation calibrée avant tout seuil d'exclusion ; pas de seuil arbitraire ajouté. Ce chantier reste partiellement ouvert.
- **Suite après report du package** : le prompt demandait de présenter tous les candidats, même périphériques. Cette contrainte est retirée ; la réponse peut retenir un sous-ensemble. `_reconcile_generated_case_list` rapproche les titres des sources et leurs IDs, écarte les identités ambiguës/inconnues, puis aligne ordre affiché et sélectionnable dans les chemins HTTP/SSE.
- **Où / preuve finale de ce lot** : `backend/app/haystack_rag.py`, `backend/app/routes/chat.py`, `backend/tests/test_chat_relevance.py`. Quatorze tests de pertinence sur données fictives, total backend/gabarits 76. Numéros Markdown en gras pris en charge ; frontières de candidats séparées de la validation du titre pour empêcher la fuite d'un bloc inconnu dans un cas valide. Contre-revue ciblée : 20 reproductions HTTP/SSE indépendantes, aucun blocage connu dans ce périmètre. Ne pas conclure à une précision sémantique réelle mesurée.

**CHAT-04/05/06 — parcours : changements source préparés.**
- **Quoi** : somme des durées d'étapes affichée comme 2h12 de travail actif estimé, hors test terrain ; lien « Tester rapidement » révélant et focalisant le prompt existant ; rôle à compléter au lieu de dirigeant imposé ; rappel d'utiliser un outil autorisé sans promesse universelle de gratuité.
- **Pourquoi** : corriger l'écart chat/page (~2 h/~2,5 h), rendre le prompt accessible sans modifier les six étapes et permettre l'usage par un employé.
- **Où** : `backend/app/parcours_util.py` ; dans le dépôt parcours associé, `pipeline/genere.py` et `templates/page.html.j2`. Les textes propres aux cas ne sont pas réécrits.
- **Contrôles** : `backend/tests/test_parcours_ux.py`, rendu de cas fictifs, ordre des six étapes, échappement HTML et texte restitué, accès au prompt et contrats URL. Définir `PARCOURS_SOURCE_ROOT` si le dépôt parcours n'est pas au chemin relatif attendu.
- **Limite de livraison** : ces changements de gabarit ne modifient pas les pages déjà embarquées. Régénération avec la source validée et les mappings existants nécessaire avant publication. Ne pas lancer le générateur historique du backend à la place du générateur parcours.
- **Commit** : aucun ; modifications locales uniquement.

**Bilan local final** : 62 tests backend/gabarits fictifs (40 CHAT, 14 baseline, 8 parcours) et 18 tests frontend passent ; build et typecheck frontend passent. Contre-revue ciblée : aucun blocage connu sur les scénarios examinés, pas une garantie d'absence de tout défaut. Avertissement de taille de bundle préexistant ; règle ESLint de langue du script HomeView déjà en échec avant intervention, non corrigée hors périmètre. Pas de validation exhaustive de la base, de parcours cloud réels ou de la production officielle.

---

## 1. Point de départ — v1 (référence)

- **Commit :** `ab4b21a` — « Public release » (2026-05-19), dépôt d'origine Simplon
  (`github.com/simplonco/avouslia`).
- **Ce qu'est la v1 :** un chatbot RAG open source aidant à explorer des cas d'usage IA.
  - **Backend :** FastAPI + **Haystack** (pipelines RAG) + **Chroma** (store vectoriel),
    LLM OpenAI/Azure.
  - **Frontend :** Vue 3 (Vite).
  - Restitution des fiches de cas depuis une base (Excel) de cas d'usage.

La v2 **ne réécrit pas** la v1 : elle l'étend (parcours guidés, télémétrie, industrialisation)
puis corrige une série de bugs de fond découverts en production.

---

## 2. Ce que la v2 ajoute — vue d'ensemble

1. **Parcours personnalisés** : après la sélection d'un cas, un **bouton** mène à une page
   « parcours » (6 étapes ~2h, quick win + prompts). ~1025 pages statiques générées.
2. **Parcours conversationnel guidé** : `Q1 domaine → Q1.5 secteur (optionnel) → Q2 objectif
   → Q3 problème → liste de ~5 cas → sélection → fiche détail + bouton parcours`.
3. **Télémétrie** (Azure App Insights) : événements du funnel chat → RAG → parcours.
4. **Industrialisation** : IaC (Bicep), config par environnement, requêtes KQL, docs de
   handover.
5. **Fiabilisation** : nombreux correctifs RAG/UX/déploiement (section 4).

### Architecture v2 (déployée)

| Composant | Techno | Hébergement Azure |
|---|---|---|
| Backend | FastAPI + Haystack + Chroma + Azure OpenAI | Container App `avoulia-backend` (`rg-avoulia-fr-dev`) |
| Frontend | Vue 3 (build Vite) servi par nginx | Container App `avoulia-frontend` |
| Pages parcours | HTML statiques (`action-<hash>.html`) | servies par le backend |
| Registry images | — | `acravoulia97186.azurecr.io` |
| Télémétrie | App Insights + Log Analytics + Workbook | — |

**Contraintes non-négociables (héritées, toujours valables) :**
- Restitution **verbatim** des champs de la base (pas de reformulation LLM à l'affichage).
- **Pré-filtrage par métadonnées** (domaine/secteur/intention) **avant** la recherche vectorielle.
- Base Excel **jamais exposée** publiquement.
- **`AVOULIA_SALT` fixe en prod** : le changer casse tous les liens parcours (cascade de 404).
- Pages parcours **non indexées** (`noindex`).

---

## 3. Évolutions fonctionnelles v2 (par thème)

### 3.1 Parcours : génération, routage, liens
- **Quoi :** génération des pages parcours, puis simplification du routage vers des pages
  **statiques** servies par le backend ; liens parcours **toujours** présents dans une fiche
  détail ; mapping `UC-xxxx → hash` via CSV local (fallback hash déterministe).
- **Pourquoi :** fiabiliser l'ouverture des pages (éviter les 404) et garder un déploiement simple.
- **Où :** `backend/app/parcours_util.py`, `backend/app/static/parcours/…`,
  `backend/scripts/generate_parcours_pages.py`, `avoulia-parcours/` (générateur public).
- **Commits :** `0f4588c`, `cdf885c`, `a491eec`, `0d8ebaa`, `9237492`, `6b83542`, `fe6a9f1`,
  `6249fb1`, `34af4ee` (2026-07).

### 3.2 Télémétrie & industrialisation
- **Quoi :** App Insights (8 événements funnel), config par environnement, Bicep IaC,
  requêtes KQL, Workbook, guide de handover.
- **Pourquoi :** mesurer l'usage et rendre la reprise/déploiement simples pour Simplon (C1).
- **Où :** `frontend/src/appinsights.ts`, `infra/` (Bicep, KQL, dashboards),
  `config/environments/…`, `HANDOFF.md`.
- **Commits :** `5929370`, `0f4588c`, `f0abacc` (2026-07).

### 3.3 Qualité du parcours guidé (Q1→Q3) & sélection de cas
- **Quoi :** meilleur classement de certains cas ; clarification que « Autre / Non spécifique »
  est ajouté automatiquement aux secteurs ; cohérence entre cas **affichés** et cas
  **sélectionnables**.
- **Pourquoi :** éviter les incohérences de sélection (« je ne peux détailler que 1 à 3 »).
- **Où :** `backend/app/haystack_rag.py`, `backend/app/rag_constants.py`.
- **Commits :** `753b3ba`, `1b702fa`, `cb8179b`.

### 3.4 Réponse terminale après choix d'un cas
- **Quoi :** après sélection d'un cas, le bot donne les **infos utiles** puis **propose le
  parcours** — sans reposer de question ni offrir de faux choix (« détail complet / plan
  synthétique », « Répondez 1 ou 2 »).
- **Pourquoi :** comportement attendu = terminal, orienté action.
- **Où :** `backend/app/haystack_rag.py` (prompt + nettoyage), `backend/app/routes/chat.py`.
- **Commits :** `d4104a5`, `fd77fff`.

### 3.5 Bouton parcours cliquable & pitch industrialisé
- **Quoi :** le lien parcours n'est plus du texte brut à copier — c'est un **bouton
  cliquable**. Le texte du pitch et le libellé du bouton viennent d'une **source unique**
  (`get_parcours_pitch()`), dérivée de la structure réelle du parcours (6 étapes, ~2h).
- **Pourquoi :** donner envie de cliquer + éviter la désynchronisation texte/bouton.
- **Où :** `backend/app/parcours_util.py`, `backend/app/routes/chat.py`,
  `backend/app/models.py`, `frontend/src/views/HomeView.vue`.
- **Commits :** `955b574`, `3bd7d85`, `6a6a7fa`, `eb198c1`.

### 3.6 UX guidée v2 (chips, stepper, retour arrière) & carte cas verbatim
- **Quoi :** message d'accueil non répété ; **chips cliquables** à chaque étape (Q1/secteur/objectif,
  puis « Cas 1…5 ») ; **stepper de progression** 6 étapes (Domaine → Secteur → Objectif →
  Problème → Cas d'usage → Parcours) avec **retour arrière** cliquable ; carte de cas
  **100 % verbatim** de la base (titre, badges effort/mode/données, description, déclencheurs) —
  **plus aucun texte de pertinence généré par le LLM** (règle D1).
- **Pourquoi :** parcours plus lisible et « cliquable » ; conformité stricte à la restitution
  verbatim ; mobile-friendly (cibles tactiles ≥ 40 px).
- **Où :** `frontend/src/views/HomeView.vue` (LE composant chat), `backend/app/haystack_rag.py`
  (`build_niveau2_block`), `backend/app/routes/chat.py`, `frontend/nginx.conf`, `smoke-test.mjs`.

### 3.7 Statistiques d'usage intégrées (Axe 3.1) — page `/stats`
- **Quoi :** suivi **simple et intégré** (aucune infra ni dashboard externe) des éléments les
  plus visités — **domaines (rôles)**, **problématiques (Q3)**, **cas d'usage consultés** — plus
  les **clics sur le bouton parcours** (conversion clé). Consultable sur la page `/stats` servie
  par le backend ; endpoint JSON `/api/v1/stats.json`.
- **Pourquoi :** répondre au besoin « savoir ce qui est le plus visité » **sans** ajouter de
  repo/produit/complexité pour Simplon (C1). Compatible avec le futur mono-conteneur.
- **Comment :** un module `stats.py` écrit un **append blob** Azure (`STORAGE_ACCOUNT_NAME/KEY`),
  avec **repli en mémoire** si le stockage n'est pas configuré. Enregistrement branché dans le
  flux chat (domaine à sa sélection, problème sur texte libre Q3, cas à l'ouverture de la carte)
  et un endpoint `POST /api/v1/chat/parcours-click` appelé par le frontend au clic du bouton.
- **Où :** `backend/app/stats.py` (nouveau), `backend/app/main.py` (routes `/stats`,
  `/api/v1/stats.json`), `backend/app/routes/chat.py` (`_record_usage_stats`, `parcours-click`),
  `backend/app/haystack_rag.py` (`stats.record("cas", …)`), `frontend/src/api/chat.ts`
  (`trackParcoursClick`), `frontend/src/views/HomeView.vue` (`onParcoursClick`).
- **Validé :** E2E navigateur (domaine → secteur → objectif → problème → cas → clic parcours),
  `/stats` affiche les 4 types ; storage branché sur `stavoulia97186` (durabilité).

### 3.8 Feedback 👍/👎 sur les cas (Axe 3.2)
- **Quoi :** sous la carte d'un cas (après le bouton parcours), deux boutons **👍 / 👎**
  « Ce cas vous semble-t-il pertinent ? ». Un clic enregistre le retour, remplace les boutons par
  un remerciement, et **une seule fois** par cas. La page `/stats` gagne un **taux de satisfaction**
  (KPI `N👍 / M👎`) et deux classements : **cas jugés utiles** / **cas jugés peu pertinents**.
- **Pourquoi :** mesurer la **qualité perçue** des recommandations (pas seulement le volume), pour
  prioriser l'amélioration de la base — signal actionnable, toujours sans produit externe (C1).
- **Comment :** endpoint `POST /api/v1/chat/feedback` (`{useful, case_label}`) → `stats.record`
  `feedback_up`/`feedback_down` avec le **titre verbatim** du cas (`cas_utilisation`, déjà exposé
  dans le payload `suggested_cases`). Frontend : `sendCaseFeedback` (fire-and-forget) câblé sur
  `onCaseFeedback`.
- **Où :** `backend/app/stats.py` (agrégats + KPI satisfaction + rendu), `backend/app/routes/chat.py`
  (endpoint `feedback`), `frontend/src/api/chat.ts` (`sendCaseFeedback`, champ `cas_utilisation`),
  `frontend/src/views/HomeView.vue` (boutons 👍/👎, remerciement, `onCaseFeedback`).
- **Validé :** E2E navigateur — 👍 puis 👎 sur de vrais cas ; `/stats` affiche le taux + le libellé
  **propre** du cas. Compilation OK, 14/14 tests, build front OK, smoke 7/7.

### 3.9 CI GitHub Actions + détection de code mort (Axe 4.1 / 4.3)
- **Quoi :** un workflow **`.github/workflows/ci.yml`** tourne à chaque push/PR sur `main` :
  (1) **backend** — install `requirements.txt`, `compileall`, `unittest` (14 tests) ;
  (2) **frontend** — `type-check`, **détection de composants Vue morts**, `build`, lint (informatif).
  Nettoyage au passage : suppression du **code mort de scaffolding Vite** (HelloWorld, TheWelcome,
  WelcomeItem, `icons/*`).
- **Pourquoi :** garde-fou industriel = **C1** (Simplon peut livrer sans expertise dev : une
  régression casse la CI, visible avant déploiement) et **C2** (traçabilité : chaque PR est vérifiée).
  La détection de code mort empêche de rééditer un fichier fantôme (cf. bug `ChatView.vue`).
- **Comment :** `frontend/scripts/check-dead-code.mjs` (zéro dépendance) échoue si un `.vue` de `src/`
  n'est importé nulle part (exception : `App.vue`). Exposé via `npm run check:dead`. La CI ne
  **déploie rien** et ne requiert **aucun secret**.
- **Où :** `.github/workflows/ci.yml`, `frontend/scripts/check-dead-code.mjs`, `frontend/package.json`
  (script `check:dead`), suppression de `frontend/src/components/{HelloWorld,TheWelcome,WelcomeItem}.vue`
  et `frontend/src/components/icons/`.

### 3.10 URL backend = source de configuration unique (Axe 4.5)
- **Quoi :** l'URL du backend n'est plus codée en dur à plusieurs endroits. **Backend :**
  `parcours_util.py` lit désormais `config.parcours_base_url` (variable d'env `PARCOURS_BASE_URL`,
  un seul défaut). **Frontend :** `nginx.conf` devient `nginx.conf.template` avec `${BACKEND_ORIGIN}`
  substitué au démarrage (envsubst natif de l'image nginx) ; le Host est dérivé via `$proxy_host`
  (pas de 2ᵉ variable). **CI Pages** et **smoke test** pointent aussi vers une déclaration unique.
- **Pourquoi :** **reprise Simplon (C1/C2)** — pour héberger ailleurs (autre tenant/URL), il suffit de
  changer **une variable** (`PARCOURS_BASE_URL` côté backend, `BACKEND_ORIGIN` côté frontend), sans
  éditer le code. Évite les URL éparpillées et désynchronisées.
- **Où :** `backend/app/parcours_util.py` (`_parcours_base_url()`), `backend/app/config.py`
  (`parcours_base_url`, défaut unique), `frontend/nginx.conf.template` (+ `frontend/Dockerfile`
  `ENV BACKEND_ORIGIN`), `frontend/docker-compose` (hint), `.github/workflows/pages.yml`
  (`env.BACKEND_ORIGIN`), `smoke-test.mjs`.
- **Validé :** défaut + override `PARCOURS_BASE_URL` testés ; frontend redéployé **Healthy**,
  proxy `/api/` OK (welcome + **streaming SSE** à travers nginx), smoke 7/7.

### 3.11 Expérience de sortie du parcours (Axe 3.4)
- **Quoi :** chaque page parcours (ouverte dans un nouvel onglet) gagne un **lien « ← Retour à
  Avoulia »** en tête ET un rappel en pied (« ← Revenir à Avoulia pour explorer d'autres cas
  d'usage »), pointant vers l'app chat. Fini le cul-de-sac : l'utilisateur peut relancer une
  exploration. Côté chat, la relance existait déjà (le **stepper cliquable** « Cas d'usage » ramène
  à la liste des cas).
- **Pourquoi :** transformer la fin de parcours en **relance** (re-engagement) plutôt qu'en impasse.
- **Comment (sans régression) :** les 1025 pages servies utilisent un template abouti dont le
  générateur canonique n'est pas `generate_parcours_pages.py`. Plutôt que de régénérer (risque de
  régression visuelle), un script **idempotent** `add_backlink_parcours.py` **injecte** les deux
  liens dans les fichiers existants (marqueur `id="avoulia-back"` → ré-exécutable sans doublon).
  URL de l'app via `AVOULIA_APP_URL` (défaut = front Container App), cohérent Axe 4.5.
- **Où :** `backend/scripts/add_backlink_parcours.py` (nouveau), `backend/app/static/parcours/action-*.html`
  (1025 pages, 2 lignes ajoutées chacune).
- **Validé :** page prod affiche les 2 liens, clic → atterrit sur l'app ; template intact ; smoke 7/7.

---

## 4. Bugs de fond corrigés — « pièges à connaître » ⚠️

Ces bugs ont été coûteux à diagnostiquer : un dev qui reprend le code **doit** les connaître.

| # | Symptôme | Cause racine | Correctif | Commit |
|---|---|---|---|---|
| B1 | Cas d'une **autre intention** dans la liste ; moins de cas sélectionnables qu'affichés | « Fallbacks silencieux » retombant sur **tous les docs du domaine** ; prompt imposant « min 3 cas » → le LLM inventait des cas | Supprimer les fallbacks élargissants ; ne jamais lâcher l'intention ; règle anti-hallucination | `2aafe0f` |
| B2 | `'ChatRequest' object has no attribute 'pending_case_index'` | Référence à un champ inexistant du modèle | Suppression de la référence | `953455a` |
| B3 | Bouton parcours qui ne s'affichait pas (contexte cas perdu en SSE) | Le contexte du cas n'était pas conservé côté flux | Conserver le contexte cas + payload backend | `b2d872e`, `f497a02` |
| B4 | `cannot import name 'AzureOpenAIGenerator'` (crash à la sélection) | API Haystack : les générateurs **texte** ont disparu | Migrer vers `AzureOpenAIChatGenerator`/`OpenAIChatGenerator`, `ChatPromptBuilder`, `ChatMessage` | `816c1e5` |
| B5 | `'ChatMessage' object has no attribute 'strip'` | L'API chat renvoie un `ChatMessage` (texte via **`.text`**, plus `.content`) | Helper unique `_reply_to_text()` | `3bd7d85` |
| B6 | Bloc « 🚀 Passez à l'action » **dupliqué** | Pitch ajouté à deux endroits, dédup uniquement si URL brute présente | Sentinelle `PARCOURS_PITCH_SENTINEL` + ajout **idempotent** | `fb2e773` |
| B7 | Un correctif présent dans le `.py` déployé **sans effet** en prod | **Bytecode `.pyc` périmé** embarqué dans l'image et exécuté à la place de la source | Dockerfile purge `__pycache__` + `PYTHONDONTWRITEBYTECODE=1` | `fb2e773` |
| B8 | Le bouton n'apparaissait jamais dans l'UI | Le code du bouton était dans **`ChatView.vue`… jamais importé** (mort) ; le vrai composant est **`HomeView.vue`** | Implémenter le bouton dans `HomeView.vue` ; supprimer `ChatView.vue` | `6a6a7fa` |
| B9 | Déploiement non pris en compte (ancien JS chargé) | `index.html` mis en cache par le navigateur | nginx : `index.html` en `no-cache`, assets hashés `immutable` | `6a6a7fa` |
| B10 | Bouton affiché **trop tôt** (pendant Q1.5/Q2/Q3) | Fallback frontend devinant un cas dès qu'on tapait un chiffre | Bouton piloté **uniquement** par `payload.parcours_url` (backend) | `eb198c1` |

**Règle générale tirée de B1/B7/B8/B10 :** privilégier une **source de vérité unique et
autoritaire** (backend) plutôt que des fallbacks/devinettes ; se méfier des artefacts
périmés (`.pyc`, cache, code mort).

---

## 5. Carte de la documentation (où trouver quoi)

| Besoin | Document |
|---|---|
| Principe projet (livraison Simplon, traçabilité) | [`README.md`](./README.md) (en-tête) |
| Vue d'ensemble v1 → v2 (ce fichier) | `CHANGELOG.md` |
| Détail chronologique de chaque correctif/déploiement | [`SUIVI_PROJET.md`](./SUIVI_PROJET.md) |
| Reprise technique, pièges, API Haystack, CTA autoritaire, cache, bytecode | [`HANDOFF.md`](./HANDOFF.md) |
| Évolutions prévues & priorités | [`ROADMAP.md`](./ROADMAP.md) |
| Installation & lancement local | [`README.md`](./README.md), [`frontend/README.md`](./frontend/README.md) |

---

## 6. Comment vérifier une reprise (checklist express)

1. **Lancer local** (cf. README) → chat accessible, `/health` = 200.
2. **Rejouer le parcours** : domaine → secteur → objectif → problème → liste → sélectionner un cas.
3. **Vérifier le bouton parcours** : il n'apparaît **qu'après** sélection d'un cas, une seule
   fois, et ouvre une page `action-<hash>.html` (HTTP 200).
4. **Tests backend** : `python -m unittest discover -s tests` (doit être vert).
5. **Smoke test post-déploiement** : `node smoke-test.mjs [url-backend]` — script sans dépendance
   qui vérifie en quelques secondes le contrat critique (health, welcome, sélection → parcours_url,
   page 200, garde-fou timing). À lancer après **chaque** déploiement.
6. En cas de « le fix ne prend pas en prod » : penser **bytecode `.pyc`** (B7) et **cache
   navigateur** (B9) avant tout.
