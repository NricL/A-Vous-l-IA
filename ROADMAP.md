# Avoulia V2 — Roadmap produit

**Rôle du document :** feuille de route priorisée des évolutions d'Avoulia V2.
Décisions prises en tant que Product Owner (Eneric) ; ce fichier est versionné dans le
repo pour rester traçable côté Eneric **et** côté Simplon.

**Dernière mise à jour :** 2026-08-26

---

## 0. Contexte & proposition de valeur

Avoulia aide un **dirigeant de PME non technique** à, en quelques minutes :
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
| 3.1 | **Funnel instrumenté + dashboard** | Exploiter les events App Insights : % arrivant à une fiche, % clics parcours, % étape 1 complétée. Dashboard lisible par le PO. | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 3.2 | **Feedback ↑/↓** | Pouce haut/bas sur chaque cas et sur le parcours → signal de pertinence, alimente l'Axe 1. | ⭐⭐⭐⭐ | ⭐⭐ |
| 3.3 | **A/B testing du CTA & du pitch** | On a itéré « au feeling » ; tester wording du bouton et du pitch avec des données. | ⭐⭐⭐ | ⭐⭐⭐ |
| 3.4 | **Expérience de sortie parcours** | Le parcours s'ouvre dans un nouvel onglet backend — vérifier le meilleur flux (retour au chat ? relance ?). | ⭐⭐⭐ | ⭐⭐ |

**Quick wins :** 3.1 (funnel/dashboard) et 3.2 (feedback). *Sans mesure, on pilote à l'aveugle.*

---

## Axe 4 — Fiabilité, CI/CD & observabilité

**Problème :** dette révélée cette semaine — bugs « fantômes » (bytecode `.pyc` périmé,
composant mort `ChatView.vue`, cache navigateur). Manque de garde-fous industriels.
**Cet axe sert directement C1 (simplicité pour Simplon) et C2 (traçabilité).**

| # | Amélioration | Détail | Impact | Effort |
|---|---|---|---|---|
| 4.1 | **CI/CD GitHub Actions** | Build + tests + lint + déploiement automatisés. Aujourd'hui tout est manuel (`az acr build`). **Clé pour C1 : Simplon déploie sans savoir-faire dev.** | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 4.2 | **Smoke test post-déploiement** | Script Playwright rejouant « sélection d'un cas → bouton présent → page 200 » à chaque release (fait à la main aujourd'hui). | ⭐⭐⭐⭐ | ⭐⭐ |
| 4.3 | **Détection de code mort (lint)** | Ne plus jamais éditer un fichier non importé (cf. `ChatView.vue`). | ⭐⭐⭐ | ⭐ |
| 4.4 | **Alerting** | Erreurs backend (ex. crash `ChatMessage`), latence, taux d'erreur remontés proactivement. | ⭐⭐⭐ | ⭐⭐ |
| 4.5 | **Découpler l'URL backend codée en dur** | Backend en dur dans `nginx.conf` et `parcours_util.py` → variable d'environnement/config unique. **Facilite la reprise Simplon (C1/C2).** | ⭐⭐⭐ | ⭐⭐ |

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
