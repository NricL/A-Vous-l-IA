# Avoulia V2 — Roadmap produit

**Rôle du document :** feuille de route priorisée des évolutions d'Avoulia V2.
Décisions prises en tant que Product Owner (Eneric) ; ce fichier est versionné dans le
repo pour rester traçable côté Eneric **et** côté Simplon.

**Dernière mise à jour :** 2026-09-13

## État actif du 13 septembre — v461 servie sur DEV

INT-01/02/03 et UX-01 à UX-05 sont livrés sur le dev. Révision active `avoulia-backend--ux-20260913-d02ffad`, frontend Azure de même suffixe et Pages sur `d02ffad`. La v461 et les pages sont inchangées. Les comptes rendus de préparation ci-dessous sont historiques.

| Suite | État |
|---|---|
| Catalogue, index isolé et parcours v461 | Déployés ; fichiers Excel/audit/mapping non servis, hashes conservés. |
| Questions guidées et sélection des cas | Correctifs réels intégrés, questions déterministes et prompt de sélection distinct ; scénarios répétés passés. |
| Sources du dernier déploiement | Publiées : chatbot `d02ffad`, parcours inchangé `a500a22`. |
| Chiffres et libellés de la vitrine | Publiés sur Pages et frontend Azure : `1 021`, `Domaines métier`. |
| Calibrage métier à plus grande échelle | Ouvert ; les essais de livraison ne garantissent pas toutes les formulations. |
| Package et production Simplon | Toujours différés. |

## Prochain programme — qualification fiable, naturel maîtrisé et catalogue complet

### Décision à 20:47 — tester sur une candidate Azure isolée

Eneric demande la livraison de test sur GitHub et Azure personnel, sans attendre la fin des essais locaux. Préparation cloud engagée : identité AVIA conservée, route `/preview`, vraie qualification/RAG PUBLIC_PAGES et six étapes, source publique v4.6.1 uniquement. Le classeur privé v462 reste hors de ce lot.

Les images sont préparées dans le registre privé ; l'activation attend l'aperçu exact et sa confirmation. La version stable garde 100% du trafic principal. Les limitations de pertinence secondaire et de latence restent ouvertes et doivent être observées sur la candidate : aucune promotion ni garantie que l'hébergement Azure accélérera les modèles. Cette décision remplace la séquence « finir les essais locaux avant tout déploiement de test », pas les critères de promotion. Configuration et rollback dans HANDOFF et `.azure/plan.md`.

### État après poursuite demandée à17:45 — préversion RAG réelle, non déployée

`http://127.0.0.1:4178/preview` dispose maintenant du mode **PUBLIC_PAGES** :1 021pages v4.6.1 déjà publiées,14domaines, index sémantique local et modèles Azure existants. Quatre pages historiques sont exclues selon leur version observée. Les fichiers labellisés et la candidate privée v462 n'ont pas alimenté cet index : il contient uniquement les champs déjà publics. Les modes PUBLIC_API (ancien RAG distant) et SYNTHETIC restent explicitement distincts.

La cause du faux négatif marketing a été reproduite :26candidats éligibles récupérés, cas attendu classé8–9 par le classement lexical puis exclu par une coupe à5 avant le modèle. Correctif local : laisser examiner le pool récupéré, limiter à5 après sélection et rapprochement des identités. Pas de changement silencieux des filtres ou du domaine. Le cœur en production n'a pas été redéployé.

Le RAG PUBLIC_PAGES retrouve le cas marketing sur la demande initiale. Il ajoute une vérification indépendante de l'adéquation tâche/livrable, sans contexte de domaine susceptible de biaiser la décision ; réponses non structurées ou erreurs restent explicites. Les contrôles de non-correspondance, canal et population spécialisés ont progressé, mais une piste secondaire web reste trop permissive sur un essai répété. La latence observée,70–305secondes selon le flux, est trop élevée pour une livraison publique ; quota existant respecté, aucune hausse de ressources décidée.

Les vrais cas publics ouvrent désormais les **nouveaux parcours locaux** : six étapes, besoin original éditable et distinct de la source, contrôles et réutilisation. Le mode d'exécution absent des pages publiques reste inconnu ; les étapes5/6 utilisent explicitement une présentation commune, pas une valeur métier inventée. Les champs publics sont inchangés et aucune donnée privée v462 n'est exposée.

CONT-01 a produit une candidate **privée, labellisée, non publiée** après arbitrage des propositions. Les changements de mode proposés massivement n'ont pas été appliqués mécaniquement. Les réserves nécessitant une expertise externe sont conservées. La candidate n'est ni la base du site actuel ni celle de PUBLIC_PAGES.

**Avant toute livraison :** essais conjoints sur ce vrai RAG local, traitement de la pertinence secondaire et de la latence, décision sur la candidate de contenu, parité explicite avec le runtime cible et aperçu/publication autorisés. Ne pas présenter cette préversion comme la reproduction exacte de l'index Chroma ni comme une certification de pertinence universelle.

**Cadrage du 13 septembre à 11:55.** Mise à jour documentaire demandée par Eneric après analyse du positionnement, du contenu et de l'expérience. Les lots ci-dessous sont **planifiés, non implémentés**. La livraison `d02ffad` et son reçu `e895cab` restent la référence en ligne ; cette roadmap ne déclenche ni modification Excel ni déploiement.

**Avancement à 12:36 :** QUAL-01 dispose d'un contrat et d'un banc mécanique local ; QUAL-02 et les changements applicatifs restent non implémentés. L'essai conjoint a montré qu'un choix naturel pour l'utilisateur peut exclure un cas classé dans un autre domaine. Ajouter ORI-01 à la conception et aux essais, sans remplacer les autres recommandations de l'analyse Bpifrance/DGE/France Num : contenu des 1 021 cas, premier essai faisable, contrôle du résultat, réutilisation et relais humains.

**Lot lancé à13:37 — préversion locale disponible, programme incomplet :** `http://127.0.0.1:4178/preview` exécute un protocole serveur distinct avec14domaines et16cas explicitement fictifs. Choix par boutons/numéros/libellés reconnus, réorientation acceptée/refusée, fiche terminale courte puis un seul lien vers les six étapes locales. Les filtres et transitions sont réels dans ce moteur d'essai ; la recherche est une règle de fixture, **pas le RAG de production ni la v461**. Ne pas prendre sa réussite comme validation sémantique ou feu vert au déploiement.

CONT-01 reste bloqué avant revue exhaustive : six appels M365 ont permis d'énumérer48IDs, mais ni l'inventaire complet/versionné ni des valeurs exactes suffisantes pour accepter des corrections de tous les cas. **Aucun cas déclaré relu complètement dans ce nouveau lot, aucun classeur corrigé.** Un accès intégral fiable et autorisé est nécessaire pour brancher/évaluer la vraie base et réaliser la revue demandée. Ne pas contourner ce blocage par lecture d'une copie cloud synchronisée sans autorisation explicite de traitement local.

**Actualisation après autorisation de traitement local à16:43 :** l'accès complet à la v461 a été établi, son empreinte rapprochée de la version déployée et les1 021IDs lus sans doublon. La revue documentaire par groupes disjoints est terminée et consolidée dans un classeur de revue conservant l'étiquette d'origine. Les corrections sont des **propositions non appliquées** ; la source, ses formules et ses feuilles restent intactes. Le blocage de lecture décrit au paragraphe précédent est historique.

CONT-01 passe à l'arbitrage cohérent des propositions, notamment des modes d'exécution ; ne pas appliquer des changements de classement en masse sur la seule foi d'un résultat d'agent. Le raccordement au RAG réel reste à traiter dans une destination respectant la classification : aucune copie de contenu vers la fixture, des fichiers texte/HTML ou un index non labellisé. La préversion reste explicitement fictive.

L'examen direct a également montré que l'essai conjoint pouvait manquer un cas dans le périmètre initial. **Diagnostiquer la récupération et la sélection intrafiltre avant de considérer la réorientation comme la solution.** Le cas exact et les observations sont conservés dans le classeur de revue labellisé, pas dans ce dépôt.
Les gabarits PAR-01 sont implémentés localement : décision d'adéquation explicite, prérequis disponibles/à préparer/exemple fictif, contexte utilisateur séparé dans le prompt copié, contrôles métier, comparaison et réutilisation. Ils sont raccordés aux16cas fictifs, pas régénérés sur les1 021cas. Le bot s'arrête à la fiche et au bouton ; aucun coaching ou questionnaire après sélection.

**Point de validation demandé à 12:16 :** tester la proposition avec Eneric avant déploiement, puis attendre son accord explicite. Une répétition de dialogue peut valider la compréhension des questions, pas le fonctionnement du nouveau protocole ni la qualité du RAG. La préversion technique doit ensuite permettre de voir les choix validés, les filtres effectivement envoyés et les cas récupérés. Ni un écran simulé, ni un nouveau frontend branché sur l'ancien backend ne constituent une recette du comportement futur. Aucun déploiement du nouveau programme n'est autorisé à ce stade.

### Cap produit et limites

La force d'AVIA est sa base métier, pas sa capacité à converser comme un assistant généraliste. L'ordre de priorité est **qualité de qualification et fidélité au catalogue, puis fluidité**. Un parcours plus agréable qui oriente moins bien est une régression.

Conserver la chaîne **domaine explicitement choisi → secteur si applicable → objectif → problème concret → cas du catalogue → fiche verbatim → parcours en six étapes**. Le domaine n'est pas déduit silencieusement du métier ou du secteur. Les boutons, numéros et libellés reconnus restent les moyens de qualification ; une ambiguïté exige une clarification. Le prochain lot n'ajoute pas de sélection sémantique automatique des domaines, secteurs ou objectifs par un LLM.

Le naturel porte sur la présentation : formulations maîtrisées, choix lisibles, transitions courtes, contexte conservé et absence de répétitions. Le problème concret reste libre ; l'IA recherche et sélectionne dans le périmètre validé. Ni la reformulation du besoin, ni une justification de pertinence ne doivent inventer une condition métier ou remplacer les exclusions exprimées par l'utilisateur.

**Périmètre de contenu : tous les 1 021 cas et leurs parcours.** Un échantillon ou des lots de travail internes servent à apprendre et organiser la revue, jamais à remplacer le catalogue ou limiter la livraison à vingt parcours. Les IDs, domaines et structure métier restent stables ; pas de nouveau schéma ni de refonte de taxonomie implicite. Un défaut de classement éventuel est tracé et arbitré séparément, pas corrigé en abandonnant les filtres.

### ORI-01 — récupération guidée entre domaines, proposition à éprouver

Le pré-filtrage demeure la règle de la recherche principale, mais ne doit pas devenir une impasse. En cas d'absence de résultat ou de rejet explicite des propositions par l'utilisateur, examiner une **recherche secondaire d'orientation dans le catalogue**, séparée des résultats normaux. Elle peut proposer un cas réel et son autre classement si tâche, résultat et contraintes correspondent ; elle ne valide ni ne change automatiquement la qualification.

La proposition indique les choix à modifier et attend l'accord de l'utilisateur. Refus : conserver l'état initial. Acceptation : appliquer explicitement les choix confirmés, revalider les dépendances puis relancer la recherche principale. Une différence de secteur doit être signalée, jamais résolue en inventant l'activité de l'utilisateur. Conserver la formulation initiale du besoin et distinguer les éléments fournis (audience, format) des conditions métier absentes qu'il serait abusif de supposer.

Cette capacité existe dans la préversion PUBLIC_PAGES, pas dans le bot stable : le premier essai avait nécessité une intervention humaine. La recherche secondaire, sa pertinence, sa latence, l'abstention et la reprise après acceptation/refus restent à éprouver avant promotion. Ne pas présenter un simple score vectoriel comme une preuve d'adéquation, ni ajouter des pistes périphériques pour remplir une liste.

### Lots ordonnés et critères de sortie

| Ordre | Lot | Livrable et critère de sortie | Dépendance / état |
|---|---|---|---|
| 1 | QUAL-01 — contrat de qualification et référence métier | Contrat et corpus versionné : 66 scénarios mécaniques, 14 domaines par numéros/libellés. 63 conformes, trois écarts cibles documentés. Les attentes de pertinence réelle et les essais utilisateurs restent distincts. | Référence mécanique locale préparée ; essais conjoints en cours |
| 2 | QUAL-02 — état explicite backend/frontend | Protocole isolé avec étape/question/révision, choix canoniques et validation serveur ; inconnus/périmés refusés, historique et saisie conservés. | Raccordé au vrai RAG local PUBLIC_PAGES ; pas migré en production |
| 3 | CONT-01 — revue d'adoption des 1 021 cas | Revue complète puis arbitrage, journal et candidate privée labellisée ; source préservée et réserves externes explicites. | Candidate v462 préparée ; non publiée, non indexée dans la préversion |
| 4 | QUAL-03 — dialogue et UI plus naturels | Première question de domaine immédiate, questions courtes, listes lisibles, saisie ou boutons ; fiche et parcours sans questions supplémentaires. | Implémenté dans l'interface d'essai ; retours utilisateur attendus |
| 4 bis | ORI-01 — orientation catalogue en cas d'impasse | Piste fondée sur un cas existant, autre classement expliqué, accord avant modification, abstention possible et recherche principale relancée sous les filtres confirmés. | Fonctionne sur snapshot public réel ; portée des suggestions et latence à affiner |
| 5 | PAR-01 — parcours opérationnels sur tout le catalogue | Six étapes, décision explicite, traitement honnête des prérequis, contexte séparé, livrable/contrôles et réutilisation. | Rendu local des1 021cas publics ; candidate privée v462 non utilisée |
| 6 | REC-01 — non-régression métier et robustesse | Contrôles structurels sur tous les cas, corpus conversationnel couvrant les domaines et situations difficiles, revue des erreurs sémantiques et essais d'usage ciblés. Pas de clôture fondée uniquement sur HTTP200, présence de boutons ou validité des IDs. | Régressions et premiers essais réels réalisés ; portée secondaire/latence ouvertes, essais conjoints sur candidate demandés |
| 7 | LIV-01 — livraison cohérente DEV | Code, catalogue, index, mapping, pages et documentation identifiés ; candidate isolée, recette sur Pages/HTTP/SSE/mobile, bascule contrôlée et retour arrière. Le classeur et les preuves privées ne sont pas publiés avec le code. | Préparation GitHub/Azure personnel engagée ; activation isolée après aperçu exact, promotion non autorisée |

### Recommandations de contenu et de parcours

Pour CONT-01, améliorer les **colonnes existantes**, pas ajouter d'emblée des champs métier. Distinguer dans les textes l'usage cible, ce que réalise réellement le premier essai et ce qui reste un projet à intégrer. « Sans code », « avec un outil » et « effort faible » ne suffisent pas à décrire autonomie, accès aux données ou risque ; leur présentation doit rester fidèle au cas, sans nouveau classement automatique opaque.

Chaque cas doit préciser un livrable contrôlable et les prérequis qui le rendent possible : éléments disponibles, droit d'accès, autorisation d'utilisation dans l'outil et éventuelle validation d'un responsable. Un assistant conversationnel ne recrée pas des historiques réels absents ; distinguer préparation d'un modèle, données fictives de démonstration et analyse des données réelles. Pour calculs, sources réglementaires et intégration technique, indiquer les capacités nécessaires de l'outil, les sources de vérité et les contrôles humains.

Dans PAR-01, ne pas se contenter d'ajouter une phrase générique dans toutes les pages. Adapter les réponses aux questions ouvertes ou fermées ; une case cochée n'est pas une preuve d'adéquation. Montrer ce que l'essai produit et ne produit pas, les erreurs à rechercher, puis la décision de recommencer, ajuster ou demander un accompagnement. Ne pas remplacer une durée uniforme par une promesse universelle de résultat en cinq ou quinze minutes.

Les exemples de résultats doivent être qualifiés (illustration fictive, contenu relu, retour réel documenté) ; « vérifié » ne signifie pas gain mesuré. Ne pas assimiler clic, prompt copié ou progression cochée à une adoption effective. Une observation volontaire d'un essai utile puis réutilisé est une piste de mesure ultérieure, pas un nouveau chantier de télémétrie engagé.

**Continuité chat → essai :** une page statique de cas peut conserver le contexte métier générique sans reprendre le besoin particulier exprimé dans le chat. PAR-01 doit proposer un complément utilisateur explicite et distinct du contenu source (audience, description à retravailler, contraintes), sans réécrire la fiche validée ni fabriquer des caractéristiques de l'audience. Ne pas mettre du texte libre sensible dans une URL publique ni le transmettre automatiquement à un assistant externe.

### Garde-fous et décision de livraison

Les invariants à faire respecter par le code sont : aucun choix de qualification inventé ou changé silencieusement ; aucune réponse numérique appliquée à la mauvaise question ; aucun cas ajouté hors du périmètre validé ; aucune réponse généraliste de remplacement lorsque le catalogue ne répond pas ; aucune divergence entre cas affiché, ID, détail et lien. Une violation connue bloque la livraison.

Pour ORI-01, une piste extérieure est une **proposition de réorientation identifiée**, pas un résultat ajouté discrètement à la liste filtrée. Ajouter aux essais : bon cas dans un autre domaine, aucune piste adaptée, piste à condition non fournie, refus de réorientation, acceptation puis reprise, changement de secteur non autorisé et conservation du besoin. Le cas conjoint de description produit destinée à la Gen Z sert de référence ciblée, pas de preuve générale de récupération.
Le corpus adverse doit couvrir au minimum : secteur confondu avec domaine, objectif vague, négations et exclusions, plusieurs besoins, problème fourni dès le départ, changement de domaine/secteur/objectif, réponses tardives/doubles, ancien bouton, liste de choix changée, historique partiel, interruption réseau, absence de correspondance et reprise. Une correction invalide seulement les dépendances concernées, sans réutiliser des cas périmés.

Comparer les qualifications et les cas pertinents avec la référence QUAL-01, en documentant les réponses multiples acceptables et les demandes qui exigent une clarification. Un choix canonique valide peut rester un mauvais choix métier ; une justification plausible ne prouve pas sa fidélité aux sources. Ne pas modifier les attentes après coup pour obtenir un meilleur score ni fixer un seuil de confiance LLM arbitraire. Toute dégradation observée doit être expliquée et résolue ou explicitement arbitrée avant livraison ; aucune promesse de zéro bug en conditions réelles.

QUAL-02 doit prévoir une migration compatible et un périmètre de recette séparant changement de protocole et changement de contenu. Le schéma exact des échanges reste à concevoir ; un champ « étape » seul ne résout pas les anciens numéros, réponses en retard ou listes modifiées. Aucun changement de modèle ni appel génératif supplémentaire pour chaque question n'est nécessaire à l'amélioration de présentation visée.

### Versionnement, exclusions et suites différées

La v461 reste la source déployée jusqu'à une nouvelle livraison explicitement identifiée. Chaque modification du classeur produit une nouvelle version `vXXX` disponible, au même nom/suffixe, sans écraser la source, les formules ou les journaux. La revue complète requiert un accès suffisamment précis aux valeurs courantes ; une restitution textuelle partielle ne doit pas être présentée comme une couverture exhaustive. Garder les audits et journaux hors du dépôt public.

Hors prochain lot : qualification automatique par LLM, remplacement de l'entrée par domaines, assistant généraliste/exécutant, réordonnancement des six étapes, changement de modèle, nouveau schéma métier, connecteurs et package Simplon. Les relais contextuels vers un accompagnateur, une fiche pour le responsable et le bilan du deuxième usage restent des recommandations de second temps, dans les parcours, sans partage automatique ni compte imposé.

**Repères publics pour le positionnement, pas preuves de performance d'AVIA :** [Bpifrance — Accélérez avec l'IA](https://conseil.bpifrance.fr/accelerez-ia), [France Num — Baromètre 2025](https://www.francenum.gouv.fr/guides-et-conseils/strategie-numerique/comprendre-le-numerique/barometre-france-num-2025-le), [Bpifrance — Projet IA](https://www.bpifrance-universite.fr/formation/projet-ia-la-serie-de-tutos-conduire-un-projet-ia-dans-votre-entreprise-etapes-cles-bonnes-pratiques/). AVIA complète ces ressources par une découverte guidée fondée sur sa base ; la seule taille du catalogue n'est pas une preuve d'utilité.

### Lot livré — fluidité après livraison, autorisé le 13 septembre

La finalisation frontend et les cinq corrections UX sont livrées après confirmation du 13 septembre à 09:57. Pages `34746510034` et CI `34746509999` réussies ; backend et frontend Azure Healthy, 100 % du trafic. Les états « locaux » plus bas décrivent la préparation.

| Ordre | Lot | Résultat attendu | État |
|---|---|---|---|
| 1 | UX-01 — cas unique | Bouton « Choisir ce cas » issu des identités serveur ; liste et ordre restaurés lors du retour depuis une fiche. | Livré sur dev et Pages |
| 2 | UX-02 — lisibilité Q3 | Au plus quatre situations individuelles, dédoublonnées après séparation des pipes ; source inchangée. | Livré sur dev |
| 3 | UX-03 — pertinence des exemples | Même éligibilité sectorielle pour Q2/Q3, filtre objectif conservé, aucun remplissage par un autre secteur. | Livré sur dev |
| 4 | UX-04 — besoin initial | Objectifs et constats explicites français reconnus ; présentations seules exclues, nouvelle précision prioritaire, ancien Q3 invalidé après changement de choix. | Livré sur dev |
| 5 | UX-05 — hypothèses non exprimées | Prompt de sélection excluant les conditions métier non établies, sans interdire les garde-fous conditionnels légitimes. | Livré ; calibrage général toujours ouvert |

Arbitrages techniques délégués. Pas de changement de base, de schéma métier, d'ordre des six étapes, de modèle ni d'instrumentation. La qualification, les pré-filtres et le détail verbatim restent les contrats de référence. Publication du code et documentation après aperçu exact confirmé ; Azure et Pages sont des livraisons distinctes.

Contrôles locaux : 171 tests backend ciblés, 31 tests frontend, types/build et composants actifs ; navigateur sur le frontend construit à 390/1280 px avec SSE fictif. Ces contrôles ne sont ni un déploiement, ni une mesure exhaustive de pertinence du catalogue. Le banc existant dispose de `--suite stock-assumptions` pour l'évaluation bornée de UX-05 avec des cas entièrement fictifs.

Évaluation UX-05 terminée sur le modèle existant : quatre scénarios dans les deux ordres de candidats, huit réponses complètes, aucune divergence aux attentes techniques, aucune troncature ni erreur de transport. Saisonnalité exclue lorsqu'absente du besoin, retenue lorsqu'explicite ; garde-fou conditionnel conservé et refus sans cas adapté. Cette mesure ciblée n'est pas un taux de précision utilisateurs. Les cinq correctifs ont ensuite été publiés et déployés, avec recette de la candidate puis de l'URL normale.

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
