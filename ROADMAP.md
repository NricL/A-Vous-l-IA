# Avoulia V2 — Roadmap produit

**Rôle du document :** feuille de route priorisée des évolutions d'Avoulia V2.
Décisions prises en tant que Product Owner (Eneric) ; ce fichier est versionné dans le
repo pour rester traçable côté Eneric **et** côté Simplon.

**Dernière mise à jour :** 2026-09-13

## État actif du 13 septembre — v461 servie sur DEV

INT-01 et INT-02 sont intégrés au backend déployé ; INT-03 a passé la bascule contrôlée et les essais sur l'URL habituelle. Révision active `avoulia-backend--v461-20260913-r3`. Les comptes rendus du 12 septembre ci-dessous décrivent la préparation et sont historiques.

| Suite | État |
|---|---|
| Catalogue, index isolé et parcours v461 | Déployés ; fichiers Excel/audit/mapping non servis, hashes conservés. |
| Questions guidées et sélection des cas | Correctifs réels intégrés, questions déterministes et prompt de sélection distinct ; scénarios répétés passés. |
| Sources du dernier déploiement | Publiées : chatbot `24e145b`, parcours `a500a22`. |
| Chiffres et libellés de la vitrine | Publiés sur Pages et frontend Azure : `1 021`, `Domaines métier`. |
| Calibrage métier à plus grande échelle | Ouvert ; les essais de livraison ne garantissent pas toutes les formulations. |
| Package et production Simplon | Toujours différés. |

### Lot actif — fluidité après livraison, autorisé le 13 septembre

La finalisation frontend est terminée ; les états de préparation et « à publier » dans l'historique sont remplacés par l'état ci-dessus. La présente remise à jour documentaire est locale tant qu'elle n'est pas publiée.

| Ordre | Lot | Résultat attendu | État |
|---|---|---|---|
| 1 | UX-01 — cas unique | Bouton « Choisir ce cas » issu des identités serveur ; liste et ordre restaurés lors du retour depuis une fiche. | Implémenté localement |
| 2 | UX-02 — lisibilité Q3 | Au plus quatre situations individuelles, dédoublonnées après séparation des pipes ; source inchangée. | Implémenté localement |
| 3 | UX-03 — pertinence des exemples | Même éligibilité sectorielle pour Q2/Q3, filtre objectif conservé, aucun remplissage par un autre secteur. | Implémenté localement |
| 4 | UX-04 — besoin initial | Objectifs et constats explicites français reconnus ; présentations seules exclues, nouvelle précision prioritaire, ancien Q3 invalidé après changement de choix. | Implémenté localement |
| 5 | UX-05 — hypothèses non exprimées | Prompt de sélection excluant les conditions métier non établies, sans interdire les garde-fous conditionnels légitimes. | Implémenté localement ; huit réponses réelles conformes aux scénarios fictifs |

Arbitrages techniques délégués. Pas de changement de base, de schéma métier, d'ordre des six étapes, de modèle ni d'instrumentation. La qualification, les pré-filtres et le détail verbatim restent les contrats de référence. Publication du code et documentation après aperçu exact confirmé ; Azure et Pages sont des livraisons distinctes.

Contrôles locaux : 171 tests backend ciblés, 31 tests frontend, types/build et composants actifs ; navigateur sur le frontend construit à 390/1280 px avec SSE fictif. Ces contrôles ne sont ni un déploiement, ni une mesure exhaustive de pertinence du catalogue. Le banc existant dispose de `--suite stock-assumptions` pour l'évaluation bornée de UX-05 avec des cas entièrement fictifs.

Évaluation UX-05 terminée sur le modèle existant : quatre scénarios dans les deux ordres de candidats, huit réponses complètes, aucune divergence aux attentes techniques, aucune troncature ni erreur de transport. Saisonnalité exclue lorsqu'absente du besoin, retenue lorsqu'explicite ; garde-fou conditionnel conservé et refus sans cas adapté. Cette mesure ciblée n'est pas un taux de précision utilisateurs. Les cinq correctifs restent locaux ; publication GitHub/Pages et mise à jour Azure à confirmer sur leur aperçu exact.

## Historique de préparation du 12 septembre — intégrer la base consolidée

La consolidation éditoriale du classeur privé est terminée et une nouvelle version est sauvegardée. **Elle n'est pas encore intégrée au chatbot.** Les journaux exacts, décomptes et arbitrages restent dans le classeur et le suivi privé, pas dans ce dépôt public. Les anciens états « audit Excel partiel » ci-dessous sont historiques.

Eneric délègue les corrections éditoriales et de cohérence dans le cadre produit existant, puis demande à 15:25 d'exécuter la suite avec des tests à chaque étape. Il n'est plus nécessaire de solliciter une validation pour chaque formulation. Cette délégation ne vaut pas publication du classeur, suppression des anciennes versions ou autorisation de diffuser ses données.

| Ordre | Lot | État | Condition de clôture |
|---|---|---|---|
| 1 | BASE-01/02/03 — intégrité, cohérence et premières actions | Terminé dans le classeur privé | Version conservée, journal avant/après et limites explicites ; pas de certification juridique ou de pertinence universelle. |
| 2 | INT-01 — import et secteurs | Implémenté et testé localement | Sélection du catalogue, contrôles d'entrée et menus complétés par métadonnées ; ordre historique et pré-filtres conservés. |
| 3 | INT-02 — source, index et parcours cohérents | Préparation locale testée ; aucun index réel construit | Génération explicite vers un dossier neuf, mapping conservé et contrôle en mémoire du catalogue ; construction d'index et publication restent conditionnées à la destination autorisée. |
| 4 | INT-03 — recette de bout en bout puis livraison dev | Non déployé | Qualification, cas sélectionné, détail verbatim et bonne page ; mobile et HTTP/SSE ; cible et exposition autorisées, rollback identifié. |
| 5 | CHAT-03 — calibrage métier | Ouvert | Scénarios attendus et pertinence évalués séparément des seuls contrôles techniques. |

Les gabarits CHAT-04/05/06 sont à intégrer dans le lot de parcours, pas à publier seuls face à des pages anciennes. Le package Simplon reste différé. Aucun nouveau chantier d'instrumentation, pivot produit ou réorganisation des six étapes.

**Résultat local :** 182 tests backend/générateur et 19 tests frontend réussis, types frontend contrôlés. L'import et le rendu de l'ensemble du catalogue réel ont aussi été parcourus en mémoire, sans publication ni embeddings. La génération est un staging privé ; le workflow parcours est désormais manuel et exclut le mapping de la racine web. Ces changements du dépôt parcours associé doivent être livrés séparément, pas assimilés à un push du seul chatbot.

**Blocage avant INT-03 :** clarifier l'accès autorisé aux textes du catalogue avant toute exposition par API/page publique, confirmer la cible Azure et effectuer la validation de déploiement. La règle de non-publication des données privées reste active ; aucun contrôle d'accès ne peut être remplacé par `noindex` ou par le hash d'une URL.

**Livraison documentaire et livraison applicative sont distinctes** : le code et les documents seront synchronisés dans GitHub après revue du contenu publiable ; un push documentaire ne réindexe pas le catalogue et ne déploie pas le backend.

## Décision active du 9 septembre — améliorer sans pivot

**Synchronisation GitHub clôturée le 10 septembre** : commit `4033e8e` sur `main`, workflows Pages et CI réussis ; https://nricl.github.io/A-Vous-l-IA/ sert les corrections mobile, qualification et récupération sans correspondance. Documentation publique nettoyée et versionnée avec le code. Les changements de gabarits, l'audit Excel structuré et le calibrage métier restent distincts et non déclarés livrés ; package Simplon toujours différé.

**Référence de livraison confirmée le 10 septembre à 11:20** : code et documentation doivent être synchronisés dans `NricL/A-Vous-l-IA`, puis publiés et contrôlés sur https://nricl.github.io/A-Vous-l-IA/. Azure reste le backend d'exécution ; sa seule mise à jour ne suffit pas à clôturer une livraison. Rattrapage Pages effectué, voir état ci-dessus.

**Livraison dev du 10 septembre** : CHAT-01/02 et corrections techniques CHAT-03 (qualification, filtres, listes et récupération après absence de correspondance) déployés sur backend0045/frontend0023 après accord explicite. Contrôles live de la chaîne utilisateur et des endpoints effectués. Le calibrage sémantique global reste ouvert. CHAT-04/05/06 restent locaux : pages et pitch conservés pour ne pas régénérer depuis une base non validée. Excel v454 inchangé ; package Simplon toujours différé. Le statut « aucun changement en ligne » des notes antérieures est historique et remplacé par cet état.

**Avancement du 10 septembre — CHAT-03** : premier passage réel sur candidats fictifs effectué avec le modèle streaming configuré. La reprise ciblée donne quatre réponses complètes, confirme deux rejets de candidats hors sujet et révèle deux alternatives sur une demande vague ainsi qu'une limite de diagnostic pour les questions numérotées. Le calibrage métier reste ouvert : attentes techniques non validées par utilisateurs, échantillon restreint, recherche vectorielle et base v454 non évaluées. Pas de seuil arbitraire, nouveau modèle ou changement en ligne.

**Avancement complémentaire CHAT-03** : liste plus courte autorisée, identités/ordre/sources alignés avec les cas affichés, variantes Markdown courantes couvertes. Lot source relu et contrôlé (76 tests backend/gabarits). Le calibrage sémantique réel demeure ouvert : ces contrôles fictifs ne prouvent pas la pertinence de toutes les suggestions. Pas de changement en ligne.

**Précision Eneric à 15:41 : package Simplon différé.** Ne pas préparer ni assembler ce package à ce stade. Continuer à documenter les corrections pour permettre une reprise simple ultérieure ; packaging et déploiement restent distincts et non engagés.

Cette décision remplace le séquencement d'août ci-dessous, conservé comme historique. À Vous l'IA reste un outil de **découverte de pistes d'usage pour les employés de PME qui ne savent pas encore comment l'IA pourrait les aider**.

Deux axes seulement sont engagés :
1. **Chatbot** : mobile et accessibilité de la saisie (CHAT-01), qualification sans répétition et état cohérent (CHAT-02), classement sans remplissage hors sujet (CHAT-03), durées cohérentes (CHAT-04), accès visible au prompt existant (CHAT-05), rôle à compléter dans les gabarits génériques (CHAT-06).
2. **Excel** : contrôler puis améliorer les colonnes existantes, uniquement sur les points faibles. Depuis le 12 septembre, les arbitrages éditoriaux sont délégués à Scout et tracés ; les contraintes de confidentialité et de versionnement restent inchangées. Toute modification doit produire un nouveau fichier au même nom avec `vXXX` incrémenté, sans écraser la source ni une version existante.

Conserver la qualification guidée, le catalogue, les identifiants, le pré-filtrage métadonnées, le détail verbatim et l'ordre des six étapes. Pas de nouveau schéma métier, nouvelle entrée de découverte, assistant généraliste ou pilote remplaçant le catalogue. Eneric prend en charge les observations utilisateurs et les autres suites ; aucun chantier supplémentaire d'instrumentation n'est relancé.

**État actuel** : CHAT-01/02 et les corrections techniques CHAT-03 ont été livrés sur dev et Pages le 10 septembre ; CHAT-04/05/06 restent à intégrer aux parcours. Le classeur privé consolidé est sauvegardé, sans indexation ni régénération déployée. La recette de la nouvelle chaîne reste à faire. Détail dans `SUIVI_PROJET.md`, `CHANGELOG.md` et `HANDOFF.md`.

---

## 0. Contexte & proposition de valeur

Le cadrage historique ci-dessous doit être lu avec la décision active : Avoulia aide les **employés de PME non spécialistes de l'IA**, y compris les dirigeants lorsqu'un cas concerne leurs responsabilités, à :
1. identifier **1 cas d'usage IA pertinent** pour SA situation (métier, secteur, problème) ;
2. **passer à l'action** via un parcours personnalisé concret (6 étapes, ~2h, quick win + prompts).

Tout se juge à l'aune de deux résultats : **pertinence perçue** et **passage à l'action**
(clic sur le bouton parcours → quick win réalisé).

Parcours conversationnel actuel :
`Q1 domaine → Q1.5 secteur (optionnel) → Q2 objectif → Q3 problème → liste de ~5 cas →
sélection d'un cas → fiche détail + bouton parcours`.

---

## 1. Modèle de livraison — contraintes structurantes (Simplon)

Cette V2 est **co-construite par Eneric puis livrée à Simplon**, qui l'héberge chez eux.
Ces deux contraintes ne concernent pas que cette roadmap : elles **régissent l'intégralité
du projet** (tout ce qui a été fait depuis la v1 et tout ce qui sera fait) — voir le
principe projet en tête de [`README.md`](./README.md). Elles s'appliquent donc à **chaque**
chantier ci-dessous :

- **C1 — Simplicité (pas de dev chez Simplon au quotidien).** Le déploiement et la
  maintenance courante doivent rester accessibles sans compétence dev pointue :
  procédures documentées pas-à-pas, automatisation maximale, un minimum de pièces mobiles,
  éviter les dépendances exotiques.
- **C2 — Traçabilité v1 → v2 (onboarding d'un futur dev).** Simplon pourra affecter un
  dev qui **a participé à la v1**. Il doit pouvoir comprendre **tout ce qui a changé
  depuis la v1** : chaque évolution doit être documentée (le *quoi*, le *pourquoi*, le
  *où dans le code*). Références d'onboarding :
  - [`HANDOFF.md`](./HANDOFF.md) — reprise du projet, pièges connus, décisions techniques.
  - [`SUIVI_PROJET.md`](./SUIVI_PROJET.md) — journal chronologique des correctifs et déploiements.
  - [`README.md`](./README.md) — installation & lancement local.

> **Règle d'or :** aucune évolution n'est « terminée » tant qu'elle n'est pas documentée
> pour C1 (procédure simple) et C2 (traçabilité).

---

## 2. Périmètre retenu

Axes **retenus** pour cette roadmap (issus de l'analyse PO du 2026-08-26) :

| Axe | Thème | Ordre convenu |
|---|---|---|
| **Axe 2** | Fluidité conversationnelle & UX | **Prioritaire (1er)** |
| **Axe 3** | Activation & conversion vers le parcours | **Prioritaire (1er)** |
| **Axe 4** | Fiabilité, CI/CD & observabilité | **Prioritaire (1er)** |
| **Axe 1** | Qualité du contenu & taxonomie (la base) | **En dernier** |

Axes **écartés** de cette roadmap : Axe 5 (personnalisation sectorielle profonde) et
Axe 6 (conformité/accessibilité approfondie). *Non abandonnés définitivement — simplement
hors périmètre pour l'instant.*

**Séquencement global :** on avance d'abord en parallèle sur **2, 3 et 4**, puis on
attaque **1** (chantier éditorial lourd, à faire ensemble).

---

## Axe 2 — Fluidité conversationnelle & UX

**Problème :** parcours rigide (navigation 100 % par chiffres), redondances, pas de retour
arrière, densité des fiches. Irritants observés en test réel.

| # | Amélioration | Détail | Impact | Effort |
|---|---|---|---|---|
| 2.1 | **Message d'accueil non répété** | Le « Bonjour, je vais vous aider… » se réaffiche à chaque tour — à n'afficher qu'une fois. | ⭐⭐⭐ | ⭐ |
| 2.2 | **Choix par boutons/chips cliquables** | Pour Q1, Q1.5, Q2 : proposer des boutons au lieu d'imposer un numéro (lève l'ambiguïté « 5 = secteur ou intention ? »). Texte libre conservé pour Q3. | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 2.3 | **Retour arrière / correction** | Permettre de modifier un choix sans tout recommencer. | ⭐⭐⭐ | ⭐⭐⭐ |
| 2.4 | **Indicateur de progression** | « Étape 3/4 » pour situer le dirigeant. | ⭐⭐ | ⭐⭐ |
| 2.5 | **Affichage progressif des fiches** | Résumé d'abord, puis « voir le détail » (les fiches détail sont très denses). | ⭐⭐⭐ | ⭐⭐ |

**Quick wins :** 2.1 (welcome), puis 2.2 (chips).

---

## Axe 3 — Activation & conversion vers le parcours

**Problème :** c'est l'objectif business, mais on ne mesure quasiment rien. App Insights
est déjà branché — reste à exploiter les events.

| # | Amélioration | Détail | Impact | Effort |
|---|---|---|---|---|
| 3.1 | **Funnel instrumenté + dashboard** | Exploiter les events App Insights : % arrivant à une fiche, % clics parcours, % étape 1 complétée. Dashboard lisible par le PO. | ⭐⭐⭐⭐⭐ | ⭐⭐ | ✅ Stats intégrées (`/stats`) |
| 3.2 | **Feedback ↑/↓** | Pouce haut/bas sur chaque cas et sur le parcours → signal de pertinence, alimente l'Axe 1. | ⭐⭐⭐⭐ | ⭐⭐ | ✅ Feedback 👍/👎 |
| 3.3 | **A/B testing du CTA & du pitch** | On a itéré « au feeling » ; tester wording du bouton et du pitch avec des données. | ⭐⭐⭐ | ⭐⭐⭐ | ❌ Abandonné (décision Eneric 2026-08-31) |
| 3.4 | **Expérience de sortie parcours** | Le parcours s'ouvre dans un nouvel onglet backend — vérifier le meilleur flux (retour au chat ? relance ?). | ⭐⭐⭐ | ⭐⭐ | ✅ Lien « Retour à Avoulia » (haut + pied) + relance via stepper |

**Quick wins :** 3.1 (funnel/dashboard) et 3.2 (feedback). *Sans mesure, on pilote à l'aveugle.*

---

## Axe 4 — Fiabilité, CI/CD & observabilité

**Problème :** dette révélée cette semaine — bugs « fantômes » (bytecode `.pyc` périmé,
composant mort `ChatView.vue`, cache navigateur). Manque de garde-fous industriels.
**Cet axe sert directement C1 (simplicité pour Simplon) et C2 (traçabilité).**

| # | Amélioration | Détail | Impact | Effort |
|---|---|---|---|---|
| 4.1 | **CI/CD GitHub Actions** | Build + tests + lint + déploiement automatisés. Aujourd'hui tout est manuel (`az acr build`). **Clé pour C1 : Simplon déploie sans savoir-faire dev.** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ CI faite (build+tests+code mort, sans secret) ; CD documenté |
| 4.2 | **Smoke test post-déploiement** | Script Playwright rejouant « sélection d'un cas → bouton présent → page 200 » à chaque release (fait à la main aujourd'hui). | ⭐⭐⭐⭐ | ⭐⭐ | ✅ `smoke-test.mjs` |
| 4.3 | **Détection de code mort (lint)** | Ne plus jamais éditer un fichier non importé (cf. `ChatView.vue`). | ⭐⭐⭐ | ⭐ | ✅ `check-dead-code.mjs` en CI |
| 4.4 | **Alerting** | Erreurs backend (ex. crash `ChatMessage`), latence, taux d'erreur remontés proactivement. | ⭐⭐⭐ | ⭐⭐ |
| 4.5 | **Découpler l'URL backend codée en dur** | Backend en dur dans `nginx.conf` et `parcours_util.py` → variable d'environnement/config unique. **Facilite la reprise Simplon (C1/C2).** | ⭐⭐⭐ | ⭐⭐ | ✅ `PARCOURS_BASE_URL` (backend) + `BACKEND_ORIGIN` (nginx template) |

**Quick wins :** 4.2 (smoke test) et 4.3 (lint code mort).

---

## Axe 1 — Qualité du contenu & taxonomie (EN DERNIER)

**Problème :** intentions trop larges, cas quasi-doublons (« Créer des infographies » vs
« Concevoir des modèles d'infographies »), mélanges d'intentions dans une même liste.
C'est le **levier de pertinence n°1**, mais c'est un chantier éditorial lourd à faire
**ensemble** — planifié après 2/3/4 (et nourri par le feedback 3.2).

| # | Amélioration | Détail | Impact | Effort |
|---|---|---|---|---|
| 1.1 | **Dédupliquer & clarifier la base** | Regrouper les cas jumeaux, resserrer les libellés d'intentions. | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 1.2 | **Règle de diversité des 5 cas** | Éviter 3 cas quasi-identiques dans une même liste. | ⭐⭐⭐⭐ | ⭐⭐ |
| 1.3 | **Gouvernance de la base** | Pipeline de validation : qui édite, versioning, contrôle qualité avant prod (aujourd'hui XLSX manuel). | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 1.4 | **Métadonnées de scoring** | Effort réel, prérequis, maturité data → meilleure priorisation. | ⭐⭐⭐ | ⭐⭐⭐ |

---

## 3. Séquencement (jalons)

| Jalon | Contenu | Objectif |
|---|---|---|
| **J1 — Quick wins (immédiat)** | 2.1 · 3.1 · 3.2 · 4.2 · 4.3 | Débloquer la **mesure**, corriger les irritants visibles, sécuriser les releases |
| **J2 — Consolidation UX & industrialisation** | 2.2 · 2.5 · 3.3 · 3.4 · 4.1 · 4.4 · 4.5 | Fluidifier le parcours, automatiser le déploiement (C1), A/B |
| **J3 — Confort UX** | 2.3 · 2.4 | Retour arrière, progression | ✅ Fait (stepper cliquable + 6 étapes) |
| **J4 — Base (en dernier, ensemble)** | 1.1 · 1.2 · 1.3 · 1.4 | Refonte éditoriale de la taxonomie, nourrie par le feedback J1 |

> L'ordre exact au sein d'un jalon reste ajustable ; la règle fixe est : **2/3/4 avant 1**.

---

## 4. Métriques de pilotage

- **North Star :** nombre de parcours démarrés / semaine (clic bouton).
- **Activation :** % sessions arrivant à une fiche cas · % clics parcours · % étape 1 complétée.
- **Pertinence :** taux de feedback positif (3.2) · taux d'abandon par étape (Q1→Q3).
- **Qualité base :** % de listes contenant un doublon · diversité moyenne des cas proposés.
- **Fiabilité :** taux d'erreur backend · succès du smoke test (4.2) à chaque release.

---

## 5. Journal des décisions de roadmap

| Date | Décision |
|---|---|
| 2026-08-26 | Création de la roadmap. Axes retenus : 2, 3, 4, 1. Axes 5 et 6 écartés. Ordre : 2/3/4 d'abord, 1 en dernier. Contraintes de livraison Simplon (C1 simplicité, C2 traçabilité v1→v2) posées comme transverses. |
| 2026-08-26 | **J1 livré** : ✅ 4.2 smoke test (`smoke-test.mjs`) · ✅ 2.1 message d'accueil non répété · ✅ 2.2 chips de choix cliquables (Q1/Q1.5/Q2). Validés E2E navigateur en prod. Détails dans `SUIVI_PROJET.md` (entrée « J1 : UX (accueil + chips) & smoke test »). |
| 2026-08-31 | **Axe 3 + 4 avancés** : ✅ 3.1 stats d'usage intégrées (page `/stats`) · ✅ 3.2 feedback 👍/👎 (taux de satisfaction) · ✅ 4.1 CI GitHub Actions (build+tests+code mort, sans secret, ne déploie rien) · ✅ 4.3 détection de code mort (`check-dead-code.mjs`) + suppression du scaffolding Vite mort. CD auto documenté mais non branché (identifiants tenant Simplon). Détails dans `CHANGELOG.md` §3.7–3.9 et `SUIVI_PROJET.md`. |
| 2026-08-31 | **Axe 4.5 livré** : ✅ URL backend = variable de config unique (`PARCOURS_BASE_URL` côté backend via `config.py` ; `BACKEND_ORIGIN` côté frontend via `nginx.conf.template` + envsubst). Reprise Simplon = changer une variable, sans éditer le code. Validé E2E (proxy `/api/` + SSE). Détails `CHANGELOG.md` §3.10. |
| 2026-08-31 | **Axe 3.4 livré + 3.3 abandonné** : ✅ 3.4 lien « Retour à Avoulia » (haut + pied) sur les 1025 pages parcours via script idempotent `add_backlink_parcours.py` (relance au lieu du cul-de-sac ; relance chat déjà assurée par le stepper cliquable). ❌ 3.3 (A/B testing CTA/pitch) **abandonné définitivement** (décision Eneric). Détails `CHANGELOG.md` §3.11. |
