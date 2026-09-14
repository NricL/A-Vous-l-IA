# Avoulia V2 — Implementation Handover Guide for Simplon

## Révision de préparation publiée — accord du 14 septembre à14:48

Backend `avoulia-backend--v463-preparation-20260914-r1`,100% main traffic, Healthy.
Image `sha256:a8a6cf7cde6cb48f59ffe4e15e1943229f962fcbbb084d434bc2447426917ff8`,
build `dd2v`. Précédent `v463-20260914-r1` / image `5de8ca8c…` conservé pour rollback.
Le frontend Azure et GitHub Pages gardent leur code ; les liens pointent sur les pages actualisées.

La soumission CLI avait échoué avant tout run (archive lente puis reset10054).
Reprise via APIs ARM documentées et transfert HTTPS natif de l'archive exactement
vérifiée, sans URL signée persistée. Build réussi :239contrôles backend et20parcours,
un contrôle Node ignoré dans chaque suite,1021pages+4historiques et exports privés
contrôlés. Les codes ANSI du journal ont été normalisés pour reconnaître les deux
résultats OK ; aucun build relancé pour ce seul problème de lecture de log.

Portée : uniquement générateur/gabarits du dépôt parcours et sorties HTML.
`prompt_preparation(c, element)` produit un bloc pour chaque prérequis par position
(les doublons de libellé ne sont pas écrasés). Le rôle à compléter reste au début ;
les champs source et les règles restent verbatim. Les formats sont des consignes à
l'assistant, pas un classifieur ni une nouvelle taxonomie.

Le prompt principal réutilise les entrées et les informations déjà fournies dans la
conversation de l'assistant choisi par l'usager ; ce n'est pas un transfert automatique
du chat AVIA. Aucune donnée libre supplémentaire n'est stockée par les pages.
Le raccourci reste le même prompt que l'étape4, et5/6 ne recommencent pas la préparation.

Revue :1 021IDs /3 774entrées, quatre rapports disjoints, mêmes empreintes de source.
Candidate finale locale : `release-preparation-20260914/revision-2` dans les artefacts
de session, générateur SHA256 `594662ed81ae2d80f0687bd4fb8af2c598d60563f5336f7f7d9652ad39264aa9`.
1 021pages actuelles, quatre historiques identiques,3 774blocs rapprochés et32contrôles
locaux réussis. Ce snapshot final est celui du build et des pages déployées. Ne pas utiliser
le premier snapshot dont les sources avaient changé pendant la préparation.

Six appels IA bornés sur exercices fictifs ont aidé à supprimer les sorties répétées.
La séparation des étapes est observée, pas la justesse universelle des réponses :
longueur, hypothèses de profil et conseils d'outils non vérifiés restent à relire.
Trace : `../_local-trace/2026-09-14-preparation-prompts/`.

Recette réelle, sans nouvel appel modèle : neuf empreintes de pages (cinq actuelles,
quatre historiques), API existante disponible, cinq chemins privés404 ; quatre pages
à390px avec préparation, passage au prompt principal, six étapes et absence de contexte
automatique. Les mêmes contrôles statiques passent sur l'URL principale après bascule.

## Historique — première livraison v463 du 14 septembre

Sources de livraison : public `830d2b0976d99a1622fc373437c873d1d90c7e1c`,
parcours privé `e61e4873a6d714aae24eb67003123d73a74def26`.
Pages `34835285869` et CI `34835285888` réussis. Bundle Pages `index-CI2eR9Mu.js`,
sans le moteur preview ; les révisions backend/frontend `qual-20260913-r1` sont
confirmées inactives. Le frontend Azure reste sur `ux-20260913-d02ffad` à100%.
Les mentions « candidate privée/non publiée » dans les onglets d'audit sont les états
historiques de préparation ; le présent reçu établit la livraison du périmètre autorisé.

Révision `avoulia-backend--v463-20260914-r1`,100% du trafic principal, image
`sha256:5de8ca8cc8f46828b8a62ddf83b7a47f0c9afb767b2d75720f6558a6e0c95182`.
Construction privée `dd2u`, Python3.11.16 :239contrôles backend et17parcours,
un contrôle Node ignoré dans chaque suite Python. `dd2t` avait échoué sur un ancien
libellé de titre attendu par un test ; l'assertion suit le gabarit approuvé, comportement inchangé.

Le payload contient le classeur labellisé dans `/app/private/catalogue.xlsx`, le mapping
et le manifeste privés,1 021pages v4.6.3 et quatre pages historiques byte-identiques.
Seul `Sheet1` alimente l'index ; aucune feuille d'audit ne devient document RAG.
Le mapping CSV est retiré du HEAD public et reste dans le payload privé ; son ancienne
présence dans l'historique Git n'est pas effacée. Les hashes de parcours ne sont pas des secrets.

Recette avant/après bascule : pages exactes et exports privés404, GenZ avec cas attendu
présent parmi les propositions, détail HTTP/SSE fidèle et lien correct, demande domestique
hors sujet sans cas. Navigateur : quatre parcours à390px sans débordement, prompt accessible,
progression conservée après rechargement ; vrai flux Pages → cas → popup v463 générique.
La zone de saisie historique du bot est conservée ; aucune question de coaching n'est ajoutée.

Rollback rapide : remettre100% sur `avoulia-backend--ux-20260913-d02ffad` (image
`058fe528…`), sans toucher à ses données/mapping. L'index v463 utilise
`/app/data/chroma-v463-20260914-r1`, collection `documents-v463-20260914-r1`,
locale à la réplique. Le frontend Azure conserve sa révision et son image stables.

### Autorisation et périmètre

Autorisation explicite : publier les1 021fiches `Sheet1` et les six étapes génériques,
en gardant classeur/audits/commentaires/mapping privés. La base du dossier de référence
réenregistrée par Excel a une autre empreinte binaire, mais toutes ses cellules,
formules et valeurs en cache sont identiques à la copie relue.

La nouvelle image part du stable `058fe528…`, utilise `app.main` et les consignes
de sélection existantes ; seul le correctif de pool est ajouté. Ne pas utiliser
`dd2s`, le moteur preview, ni le template Azure de la dernière révision expérimentale.
Cloner le template de `ux-20260913-d02ffad`, conserver les références de secrets,
préparer un index local à la réplique distinct et garder100% du trafic stable pendant
la recette. Cette séquence a été appliquée avant la bascule ; le frontend Azure est réutilisé sans changement visuel.

Trace de cette livraison : `../_local-trace/2026-09-14-v463-publication/`.
Les jalons « privé/non autorisé » ci-dessous sont historiques, pas une interdiction
du périmètre précisément autorisé à12:13. Le classeur complet reste exclu du public.

## Historique de préparation du contenu et du nettoyage

**Jalon contenu du 14 septembre à11:29 :** v463 privée, construite depuis la v462
inchangée par Excel natif, avec étiquette préservée. Quatre corrections éditoriales,
1 021IDs/modes/taxonomie identiques,6 158formules et24feuilles d'origine conservées.
Trois nouvelles feuilles : journal exact,32lignes d'aperçus pour quatre parcours,
bilan de validation. Les valeurs avant/après restent dans le classeur, pas dans ce dépôt.
Les aperçus sont textuels et protégés, non des HTML interactifs publiables.
Trace metadata : `../_local-trace/2026-09-14-content-finalization/journal.json`.
Ne pas utiliser le pipeline de génération pour exporter ce contenu privé avant validation
de publication ; aucune source/index/page courante n'a changé.

**Trace de reprise locale :** le dossier frère `../_local-trace/2026-09-14-8020/`
contient le journal du recentrage. L'archive immuable `../_local-trace/2026-09-14-r2/`
conserve décisions, commentaires, échecs et patches exacts antérieurs. Ces dossiers
restent hors de ce dépôt public et des contextes Docker, sans classeur ni secret.

## Reprise active — 80/20, décision du 14 septembre à 10:21

**Mise à jour à 10:59 : priorité aux fiches et parcours.** Le sélecteur retrouve
exactement ses consignes antérieures ; les ajouts expérimentaux de prompt et leurs
assertions sont retirés, faute de bénéfice comparatif démontré. Le correctif intrafiltre
reste seul dans le moteur. L'image privée `dd2s` contient encore les consignes retirées :
elle est historique, ne pas la déployer comme cette version minimale.

Le générateur de parcours conserve les apports d'adoption et allège maintenant son
introduction ; étape2 en langage courant et étape4 avec contrôles utile/fiable/utilisable.
Pas de modification de classeur ni de régénération des pages dans ce travail de gabarit.
Trace courante hors dépôt : `../_local-trace/2026-09-14-parcours-priority/journal.json`.

Le moteur conservé est `app.main` / `haystack_rag.py`, interface `HomeView.vue`.
L'expérimentation parallèle `/preview` est retirée du code et des recettes actives,
pas réparée ni promue. Ne pas recréer un vérificateur LLM ni un second moteur pour
résoudre les faux rejets qu'elle avait introduits. Les correctifs asynchrones retirés
restent récupérables dans l'archive, sans imposer leur protocole au bot existant.

Le correctif de sélection déjà présent dans `812aa94` reste : tous les candidats du
pool récupéré sont visibles avant le plafond de cinq résultats après rapprochement.
Le stable Azure `d02ffad` ne contient pas encore ce correctif. Le prompt existant
reste inchangé. Les exclusions, filtres et identités sont préservés ; jusqu'à cinq
pistes utiles sont acceptées, pas une liste imposée d'un seul ID. Les documents à réunir
se traitent dans le parcours, sans supposer leur disponibilité.

Le détail conserve le titre/texte source et le lien générique autoritaire, sans nouvel
appel de pertinence ni texte du besoin dans le lien ou le prompt copié. Le générateur
privé conserve les six étapes et les améliorations d'adoption ; il retire son champ
de contexte automatique et les overrides réservés au moteur d'essai.

Contrôles ciblés : `test_case_selection_prompt`, `test_infilter_retrieval`,
`test_chat_relevance`, `test_chat_regressions`, `test_relevance_evaluation` ;
suite opt-in `evaluate_chat_relevance --suite generic-intent`, au maximum seize
appels et aucun par défaut. Les fixtures ne prouvent pas une recette du catalogue réel.
Définir `PARCOURS_SOURCE_ROOT` vers le dépôt privé actif pour les contrôles croisés ;
ne pas lire le classeur utilisateur modifié ni régénérer les données pour ces essais.

Publication suivante : contexte neuf du bot existant, sans source privée dans le dépôt
public, aperçu exact puis confirmation. Aucun commit, push ou déploiement dans le
nettoyage local. La r1 distante n'est pas arrêtée par la suppression des fichiers ;
son retrait cloud devra être explicite, en conservant images et trafic stable.

## Archive r1/r2 — historique, commandes et cibles retirées

Les instructions de préversion ci-dessous sont conservées pour comprendre et
reconstituer les essais passés, jamais pour relancer le développement ou déployer
des modules désormais supprimés. Le cadrage actif ci-dessus et ROADMAP les remplacent.

### Correctif de fiabilité r2 — passe antérieure du 14 septembre

**État final de cette passe : bloqué, non déployé.** Le transport asynchrone et la reprise ont été exercés, mais le vérificateur expérimental ne passe pas la recette sémantique élargie : faux rejet du cas GenZ et réponse tronquée sur un contrôle spécialisé. La validité des références ne prouve pas la vérité du jugement. Le build privé `dd2r` a aussi échoué sur une assertion de langue du prompt, corrigée ensuite localement ; aucune image r2 validée n'a été produite. Ne pas pousser/promouvoir ce lot comme terminé.

La candidate r1 a été publiée (`812aa94`, gabarits privés `5c748ef`) ; le site habituel et son trafic principal restent sur les révisions `ux-20260913-d02ffad`. Une réorientation a dépassé la limite HTTP Azure de 240s ; le calcul continuait et retenait le verrou global. Un autre essai a produit une erreur de vérification 502. Ces échecs restent consignés, même si une relance a réussi.

Le prochain backend reçoit les actions via `POST /api/preview/v1/sessions/{sid}/operations`, avec l'enveloppe Action existante. Réponse `{protocol_version:1,state,operation}` : HTTP202 si l'opération est en attente/en cours, 200 pour une transition courte terminée. `operation` contient `id`, `request_id`, `status`, `error` et `draft`. Les états sont `queued`, `running`, `succeeded`, `failed`, `cancelled`. Le dernier résultat ou échec peut être retrouvé par `GET .../operations/current` ; `GET .../operations/{id}` suit une opération connue. `POST .../operations/{id}/cancel` accepte `{protocol_version:1}` et annule uniquement cette opération.

Les appels HTTP restent courts pendant le calcul. Une réponse perdue doit conduire à lire l'opération courante et rapprocher son `request_id`, jamais à resoumettre aveuglément avec un nouvel identifiant. L'état validé, le brouillon soumis et le statut d'échec restent distincts. Les anciens endpoints preview `/actions` et `/actions/stream` refusent explicitement les actions nécessitant une inférence en hébergement cloud (`async_required`, 409) ; le bot stable `/api/v1` n'est pas modifié.

`preview_operations.py` borne l'admission à deux travaux d'inférence, sans file d'attente, et à 64 opérations par session. Les actions de qualification sans inférence ne patientent pas derrière ces travaux. `preview_execution.py` fournit échéance monotone et annulation coopérative ; maximum 600s par opération, limites SDK bornées par le temps restant. Une annulation invalide immédiatement le droit de valider le résultat ; un appel distant déjà engagé peut encore terminer, mais ne peut ni appliquer un ancien résultat ni déclencher la suite du pipeline. Sa place reste occupée jusqu'à son retour, pour ne pas contourner la limite de capacité.

Les transitions utilisent un verrou court ; aucun appel modèle ni attente de quota ne le retient. Avant validation finale : mêmes session, révision, question et catalogue, même opération active. Annulation, expiration, redémarrage ou changement concurrent interdisent toute validation tardive. Les activités utilisateur renouvellent le délai d'inactivité d'une heure ; la tâche de nettoyage ne le renouvelle pas. Sessions et opérations restent en mémoire d'un seul processus/réplique, sans données utilisateur persistées.

Le vérificateur interne `avia_verification_v5` demande des références énumérées vers les segments du besoin original et de la source, avec schéma JSON strict. Le code retrouve les citations et calcule le verdict à partir de la couverture et des restrictions fonctionnelles ; pas de citation fabriquée ni d'acceptation en cas de contrat invalide. Le schéma interdit un jugement positif sans référence au besoin. La liste des restrictions doit rester vide quand il n'y en a pas ; les données à réunir, garde-fous de relecture, bénéfices et positionnement générique PME ne sont pas des activités supplémentaires à demander. Les véritables spécialisations de canal/population et les exclusions restent bloquantes.

La sélection conserve `medium`/2200 ; la vérification conserve finalement `medium`, avec un plafond de3000 par cas. L'essai `low`/1800 a été abandonné après des erreurs sémantiques et de références sur des contrôles élargis. Ces observations ne prouvent pas que l'effort de raisonnement était leur cause unique. Les verdicts sémantiques restent ceux d'un modèle et peuvent se tromper malgré des références valides ; ne pas confondre conformité structurelle et pertinence universelle. Erreurs, refus ou troncatures restent explicites : aucun faux résultat vide, aucune liste noire de cas ni limite artificielle à un seul résultat.

Le budget 10k TPM conserve les réservations en cours et les fenêtres de consommation observée. L'attente est annulable ; le verrou de budget ne couvre pas le réseau. Chaque recherche utilise son propre vecteur de requête ; le cache partagé ne doit jamais lui substituer celui d'une autre session. Aucune hausse de modèle, quota ou infrastructure de données.

Pour la recette HTTP réelle : `python -B -m scripts.smoke_preview_operations --origin <origine explicite de la candidate> --stage genz --live-consent`, puis `negative` et `orientation`. Ce script réutilise les scénarios existants, mesure les temps de soumission/polling, borne chaque requête HTTP à 20s et ne confond pas calcul long et HTTP bloquant. Il conserve les échecs ; les contrôles unitaires utilisent des attentes simulées, pas des appels Azure.

La cible r2 est `qual-20260914-r2` pour les deux images/révisions. Reprendre la recette de contexte public en liste blanche, le snapshot et les références de secrets existants ; inclure les nouveaux modules/tests. Le frontend Pages reçoit l'API r2 et un vrai fichier `preview/index.html`, pour que l'URL canonique `/A-Vous-l-IA/preview/` ne dépende plus du fallback404. Les libellés distinguent explicitement hébergement Azure et essais locaux. Aucun texte privé v462 n'entre dans cette livraison.

Déployer la candidate corrigée séparément, conserver le site stable à100%, puis éprouver recherche/réorientation, annulation pendant une recherche, deuxième session, rechargement, erreurs et parcours sur mobile. Conserver les anciennes images ; retirer l'ancienne candidate seulement après bascule du frontend de test. Les accords et reçus historiques ci-dessous ne prouvent pas que r2 est déjà livrée.

## État déployé — 13 septembre 2026

Le dev sert v461 avec les cinq correctifs UX via `avoulia-backend--ux-20260913-d02ffad`,100% trafic, mode Single ; image `sha256:058fe52822fea24c4e52e17b27242480f3ab96771b883243d8bad7efb2aaaafb`. Le frontend de référence reste https://nricl.github.io/A-Vous-l-IA/. Les étapes de préparation ci-dessous sont historiques, pas des tâches à recommencer.

Le mapping et le classeur sont sous `/app/private`, jamais sous la racine web. Les exports hérités sont conservés dans un sous-dossier privé et le serveur statique refuse leurs extensions. `INDEX_PATH` désigne le fichier explicite ; l'index utilise un répertoire/une collection propres à cette révision, sans effacement du précédent.

**Attention stockage :** une déclaration Azure Files existe, mais aucun montage n'était attaché au conteneur observé. L'index est donc local à la réplique et peut être reconstruit à son redémarrage. Ne pas annoncer une persistance Azure Files sans la mettre en œuvre et la vérifier dans un lot dédié.

**Rollback :** anciennes images et définitions de révision conservées ; les anciennes répliques sont inactives pour éviter des coûts et des endpoints hérités inutiles. Une restauration doit remettre ensemble code, catalogue, index et pages. Le retour à0045 remettrait aussi ses anciens comportements de confidentialité : préférer une correction conservant la protection du webroot lorsque possible. Ne jamais vider le nouvel index pour improviser un retour arrière.

**Sources / vitrine finalisées :** chatbot `d02ffad` et parcours inchangé `a500a22` publiés ; Pages et frontend Azure affichent 1 021 cas, 14 domaines métier et 71 intentions. Frontend Azure `avoulia-frontend--ux-20260913-d02ffad`, image `sha256:2ae5e263bb60ecf245c4ad59658de07323a902da858d60c42cb26c22d4cfee18`. Les mentions de préparation/non-publication plus bas sont historiques.

**Rollback du lot UX :** r3 backend, image `sha256:9c356b0643a3313709f434d73505b6c7e98b49fca735ad869983b0e835410c1b`, et frontend v461, image `sha256:dd4598880ea05482eddf5795f81f97e30bfe6b21ff544ecdcfb38e1dadad1930`, conservés. Réactiver/restaurer explicitement l'image souhaitée et son trafic, sans effacer d'index. La reconstruction d'index d'une nouvelle réplique peut demander quelques minutes.

## Candidate de test Azure — préparation demandée à 20:47

La candidate utilise `app.preview:create_app`, pas le backend historique `app.main`. Elle reste séparée de la révision stable : **trafic principal 100% sur `ux-20260913-d02ffad`, candidate accessible uniquement par son URL dédiée**. Ne pas promouvoir automatiquement. Les indications « local seulement / pas d'autorisation » dans l'historique ci-dessous décrivent des étapes antérieures.

Backend prévu : `https://avoulia-backend--qual-20260913-r1.purpleocean-980317d1.francecentral.azurecontainerapps.io`. Frontend Azure prévu : `https://avoulia-frontend--qual-20260913-r1.purpleocean-980317d1.francecentral.azurecontainerapps.io/preview`. Pages prévu : `https://nricl.github.io/A-Vous-l-IA/preview`. La racine garde son API stable et son identité ; seule la route preview reçoit le nouveau flux. Ces URLs sont des cibles, pas un reçu de déploiement.

Configuration backend : `AVIA_PREVIEW_HOSTING=azure_test`, `AVIA_PREVIEW_MODE=public_pages`, `AVIA_PREVIEW_AZURE_AUTH=environment-key`, origines exactes dans `AVIA_PREVIEW_ORIGIN` / `AVIA_PREVIEW_FRONTEND_ORIGIN`, et `AVIA_PREVIEW_APP_URL=https://nricl.github.io/A-Vous-l-IA/preview`. Configurer `AVIA_PREVIEW_TRUSTED_PROXY_CIDRS` d'après les pairs réellement observés, jamais un wildcard ; Uvicorn conserve le pair original avec `--no-proxy-headers`. Vérifier à nouveau les pairs et HTTPS sur la candidate. Les noms d'hôte et CORS sont des limites de transport, pas une authentification utilisateur.

Conserver les modèles existants `gpt-5-mini` et `text-embedding-3-small`, API `2024-08-01-preview`, et les références de secrets Azure existantes ; ne pas passer de clé dans le contexte Docker, les arguments de build, GitHub ou les journaux. Le mode cloud interdit CLI, fixtures et changement de source. En local, le mode `cli-token` exige maintenant `AVIA_PREVIEW_AZURE_SUBSCRIPTION` explicitement défini ; aucun abonnement personnel codé en dur dans le nouveau module.

Frontend : `VITE_AVIA_PREVIEW=true`, `VITE_AVIA_PREVIEW_CLOUD=true`, `VITE_AVIA_PREVIEW_ORIGIN=<origine HTTPS de la candidate backend>` et `VITE_AVIA_PREVIEW_HOSTS=<origine HTTPS exacte du frontend>`. Pages utilise `https://nricl.github.io` et la base `/A-Vous-l-IA/` ; Azure utilise son origine de révision et `/`. Les builds sans flags restent sans preview. `previewEnvironment.ts` partage les règles de route/base et coupe la télémétrie sur les alias et transitions entre site stable et preview.

Préparer un dossier de build neuf avec `scripts/prepare_preview_context.py` : code autorisé, gabarits rapprochés et quatre ressources de cache issues exclusivement des pages déjà publiques. Le Dockerfile `Dockerfile.dev-preview` réutilise les dépendances de l'image stable puis reconstruit une image `FROM scratch`, sans anciens `/app`, `/root`, classeurs, mapping ou index. `requirements-preview.txt` déclare Beautiful Soup ; les contrôles du build s'exécutent sous Python 3.11, puis le démarrage minimal est exercé dans l'image finale sous UID 65532.

**Exploitation limitée :** une seule réplique et un seul worker, sondes TCP sur 8000, sessions en mémoire expirantes. Un redémarrage perd les sessions et invalide leurs liens ; ne pas déployer plusieurs répliques. Les liens parcours sont des liens porteurs liés à session/révision. Leur ouverture document depuis Pages est admise sans `Origin`, sans ouvrir les appels API cross-site ; les liens périmés restent refusés. Le texte du besoin n'est pas dans l'URL.

**Ordre de livraison :** images privées et contrôles, aperçu exact/confirmation de publication, révisions isolées sans promotion, contrôle santé/CORS/ouverture Pages → parcours, puis essais réels et mobiles. Un échec ne déclenche ni fallback vers un faux résultat vide ni bascule sur le site stable. Pour retirer l'essai : remettre le build Pages sans flags et désactiver les deux révisions candidates ; conserver les images et le trafic stable. La candidate privée v462 et le correctif du cœur Chroma ne sont pas déployés dans cette recette preview.

## Historique de conception — qualification d'abord, cadrage du 13 septembre à 11:55

### Raccordement initial de la préversion — PUBLIC_PAGES / RAG local réel

Le mode par défaut de l'instance locale a été raccordé à un snapshot de **1 021fiches déjà publiées v4.6.1**, avec14domaines et4pages historiques exclues. Source distincte des classeurs General : ne jamais mélanger le corpus public et la candidate v462 privée. `mode_execution` et `declencheurs_typiques` ne sont pas disponibles dans les pages extraites ; rester explicite sur cette limite. Le classement local cosine/embeddings et les champs indexés ne sont pas identiques au moteur Chroma déployé.

Modules : `preview_publicsnapshot.py` (lecture des ressources publiques et contrôle de provenance), `preview_public_rag.py` (embeddings, pré-filtres, sélection et vérification), scripts `build_preview_publicsnapshot.py`, `embed_preview_publicsnapshot.py`, `smoke_preview_public_rag.py`. Les identités et versions sont rapprochées ; erreurs de lecture, budget, modèle, JSON ou preuve ne deviennent pas de faux résultats vides. Les besoins et vecteurs de requête restent en mémoire.

Configurer un chemin de cache public explicite dans `AVIA_PREVIEW_PUBLIC_CACHE`, `AVIA_PREVIEW_MODE=public_pages`, les origines loopback8767/4178 et `AVIA_PREVIEW_PARCOURS_ROOT` vers le dépôt parcours rapproché. Lancer le serveur séparé avec `python -B -m uvicorn app.preview:create_app --factory --host 127.0.0.1 --port 8767 --no-access-log`. L'interface `/preview` demande l'accord de transmission du besoin et des champs déjà publiés aux modèles Azure existants. Aucun fichier General n'est lu par ce chemin.

Le protocole code gouverne les domaines/secteurs/objectifs ; les modèles ne les changent pas. La recherche principale filtre avant similarité, examine un pool borné et limite l'affichage après sélection. L'orientation utilise un autre pool distinct, conserve le secteur et exige une confirmation avant nouvelle recherche principale. Le vérificateur reçoit le besoin original et le texte source sans classement/contexte métier ; ses jugements sont contrôlés (IDs, citations exactes, périmètre et contraintes) mais restent des jugements de modèle, non une preuve universelle.

**Correctif intrafiltre dans le cœur historique, local uniquement :** `_build_rag_prompt_from_docs` et `_docs_to_payload` ne coupent plus à5 avant sélection ; `_reconcile_generated_case_list` limite les résultats après rapprochement. Le besoin produit avait26candidats éligibles et son cas adapté figurait au rang lexical8–9. Tests `test_infilter_retrieval.py`, diagnostic opt-in `scripts/diagnose_infilter_retrieval.py`. Ne pas confondre preuve de cette troncature avec une capture exhaustive de l'ordre ANN ou de la réponse brute de production.

**Parcours réels locaux :** PUBLIC_PAGES est rendu par `preview_parcours.py`, sans redirection publique ; PUBLIC_API seul conserve la redirection vers sa page actuelle. Le mode non publié reste `None` ; `render_page` accepte des gabarits explicites de présentation communs pour5/6, sans modifier les champs source. Besoin conservé dans la zone locale, liens liés à la révision, ancienne URL refusée après changement de sélection. Lien public source secondaire sous provenance, un seul CTA principal.

**Limites ouvertes :** une proposition de page web peut encore être admise trop largement ; ne pas résoudre cela en cachant toutes les alternatives ou en ajoutant un mot-clé interdit. Les workflows réels ont pris70–305secondes ; le budget glissant respecte le quota10kTPM existant et un nouveau processus attend son refroidissement initial. Pas de hausse de quota autorisée ni promesse de rapidité. La télémétrie est exclue aussi sur les alias `/preview/` et `/PREVIEW`, et la configuration par défaut sans flag conserve l'ancien frontend.

La candidate de contenu est une copie privée labellisée séparée ; elle conserve IDs, taxonomie, formules et journaux. Aucun de ces changements n'est publié sur GitHub ou déployé. La préversion locale monoprocessus reste une surface d'essai, pas une recette d'hébergement multi-répliques.

### Préversion exécutable — lot demandé à13:37

**URL locale :** `http://127.0.0.1:4178/preview`, backend `http://127.0.0.1:8767`. Mode **SYNTHÉTIQUE / NON PRODUCTION**,16cas fictifs,14domaines ; règles de tâches sur fixtures, aucun modèle/embedding/accès v461. Interface opt-in et serveur séparé de `app.main` : les endpoints et le bot déjà déployés ne changent pas.

Backend : `app/preview.py`, `preview_protocol.py`, `preview_repository.py`, `preview_fixture.json`, `preview_parcours.py`, `preview_theme.py`. Frontend : `src/api/preview.ts`, `src/views/PreviewView.vue` et activation locale dans router/main/Vite. Contrat : phase/question/révision/source, choix canoniques, rejet de commandes périmées et double requête, copie transactionnelle de l'état en cas d'erreur. Les sessions sont en mémoire, limitées et expirent après une heure ; **ce stockage est destiné à cette préversion monoprocessus, pas une architecture validée pour les répliques Azure**.

Le bot qualifie brièvement, propose les cas, puis affiche une fiche courte et **un seul bouton parcours**, sans autre saisie ou coaching après sélection. La réorientation propose un autre classement sans changer l'état jusqu'à acceptation ; un refus conserve les choix. Les numéros et libellés sont résolus uniquement dans la question courante. Le bloc de diagnostic est séparé de l'usage normal.

La page parcours est rendue en mémoire par le générateur du dépôt associé. Le besoin est un complément local modifiable, séparé des champs source et ajouté au texte copié ; pas de données privées dans l'URL ni d'envoi externe. Les liens parcours/handoff portent la révision sélectionnée et refusent un ancien lien après changement de choix, au lieu de servir silencieusement un autre cas. La récupération d'une erreur sans transition préserve les brouillons saisis.

**Lancement backend**, depuis `backend`, avec dépendances existantes et de rendu disponibles : définir `AVIA_PREVIEW_MODE=synthetic`, `AVIA_PREVIEW_ORIGIN=http://127.0.0.1:8767`, `AVIA_PREVIEW_FRONTEND_ORIGIN=http://127.0.0.1:4178`, `AVIA_PREVIEW_PARCOURS_ROOT=<chemin absolu du dépôt parcours rapproché>` ; lancer `python -B -m uvicorn app.preview:create_app --factory --host 127.0.0.1 --port 8767`. L'absence du mode ou du générateur ne déclenche aucun repli vers la production.

**Lancement frontend**, depuis `frontend` : définir `VITE_AVIA_PREVIEW=true` et `VITE_AVIA_PREVIEW_ORIGIN=http://127.0.0.1:8767`, puis `npm run dev -- --host 127.0.0.1 --port 4178 --strictPort`. Garder la préversion sur loopback, jamais via tunnel ou hébergement public. Le port8766 était occupé par un processus système et n'a pas été utilisé.

**Contrôles ciblés finaux :**39tests `tests.test_preview_protocol` et `tests.test_preview_parcours` (racine parcours explicitement configurée),44tests Node `check-preview-state.mjs` et `check-chat-state.mjs`, types frontend. Les contrôles antérieurs ont également parcouru les gabarits aux deux tailles, stockage bloqué et copie manuelle ; la revue a révélé les liens de session mutables et la perte d'une saisie après choix invalide, tous deux corrigés avec reproductions persistantes. Essai navigateur final : choix invalide sans perte du besoin, réorientation confirmée, fiche terminale et six étapes avec contexte intact à390px. Ce résultat **ne prouve pas la pertinence sur les1 021cas**.

**Blocage du catalogue réel :** la lecture M365 disponible n'a pas permis un inventaire complet et des champs exacts liés à une version stable. Le lot de revue exhaustive n'a accepté aucune correction de cas. Il faut une copie de travail autorisée pour traitement local explicite (si les règles de protection le permettent), ou un lecteur protégé de plages exactes. Aucune suppression de protection, export forcé ou modification du classeur partagé.

**Mise à jour après autorisation locale à16:43 :** une copie binaire identique de la v461 a été autorisée et lue intégralement. L'étiquette d'origine a été identifiée via Excel et conservée. Les1 021IDs, champs obligatoires et caches ont été rapprochés ; quatre revues disjointes ont été consolidées dans un classeur labellisé, sans changer les18feuilles originales. Le blocage de lecture ci-dessus est donc levé, mais pas celui de l'exposition dans un artefact non labellisé.

Les propositions de champs doivent encore être arbitrées, particulièrement les modes d'exécution. Les données et jugements détaillés restent dans les classeurs labellisés ; les scripts privés ne contiennent que le traitement générique. Native Excel a préservé les métadonnées et caches ; ne pas passer ces fichiers par une conversion LibreOffice susceptible de perdre l'étiquette. Une revue documentaire assistée ne constitue ni validation réglementaire ni test utilisateur de chaque cas.

La nouvelle lecture invalide l'interprétation trop rapide selon laquelle l'échec de l'essai conjoint s'expliquait seulement par un autre classement. Un cas éligible existe dans le périmètre initial : rechercher la cause de ce faux négatif (récupération, classement, candidats et sélection), sans élargir silencieusement les filtres ni publier les textes de revue. Aucun correctif ou nouvel index réel n'a été appliqué.

Le protocole, les gabarits et le raccordement local sont prêts pour des essais de mécanique/ergonomie. Le connecteur de RAG réel, la revue complète et la migration du runtime restent à terminer avant approbation de livraison.

Depuis la poursuite demandée à12:01, le contrat et le banc mécanique QUAL-01 ont été préparés localement ; depuis12:16, Eneric souhaite des essais conjoints avant toute approbation de déploiement. QUAL-02 et ORI-01 ne sont pas implémentés. Source servie `d02ffad`, reçu publié `e895cab`, catalogue v461 et parcours `a500a22` restent inchangés. `ROADMAP.md` est la référence des travaux à venir ; UX-01 à UX-05 sont déjà livrés.

**Priorité non négociable :** qualification exacte et fidélité au catalogue avant fluidité. Maintenir domaine choisi explicitement, secteur selon les règles existantes, objectif, problème, pré-filtres, IDs, détail verbatim et URLs autoritaires. Le prochain lot exclut la classification automatique de ces choix par LLM. Un clic est une confirmation ; une réponse ambiguë ne l'est pas.

**Piège actuel à traiter avant de varier le texte :** `haystack_rag.py::_detect_expected_step_from_assistant` et `HomeView.vue::detectPhase` reconnaissent des formulations de questions. « Pour vos stocks, quelle est votre priorité ? » ne devient pas une étape objectif par simple reformulation. QUAL-02 doit introduire une représentation explicite de l'étape, de la question, du contexte et des choix canoniques dans `models.py`, les routes HTTP/SSE, `frontend/src/api/chat.ts` et `HomeView.vue`. Les champs de sélection existants sont à réutiliser autant que possible ; les nouveaux noms et le versionnement du contrat restent à concevoir.

Le serveur doit valider l'appartenance d'un choix à la liste offerte pour cette question, son contexte de qualification et la version concernée. Ne pas faire d'un numéro affiché un identifiant durable d'objectif. Prévoir choix périmés, réponses retardées/doubles, listes modifiées, interruptions, historique partiel et correction des parents ; ne pas rétablir silencieusement les champs invalidés. Les anciennes voies de lecture ne doivent rester que pour une compatibilité explicitement bornée, pas redevenir la source d'autorité du nouveau flux.

QUAL-01 établit les invariants et attentes avant comparaison. QUAL-03 améliore ensuite la présentation par des formulations maîtrisées, sans nouveau modèle ni appel LLM à chaque question. Le problème original, y compris ses négations/exclusions, reste disponible ; une reformulation ne le remplace pas. L'absence de cas donne une sortie explicite et une possibilité de correction, jamais une réponse générale hors catalogue.

CONT-01 porte sur **les 1 021 cas**, avec couverture et journal par ID. Travailler en lots internes n'autorise pas une clôture sur vingt cas. Améliorer les champs existants en distinguant cible, premier livrable et déploiement, ainsi que données accessibles/autorisées, calculs ou outils requis, limites et validation. Tout classement métier à corriger doit être tracé et arbitré ; pas de refonte de taxonomie implicite. La v461 est conservée ; une modification produit un nouveau classeur versionné, jamais un écrasement.

PAR-01 conserve les six étapes : réponses adaptées aux questions, adéquation non déclarée automatiquement, données fictives distinguées des données manquantes, résultat attendu et contrôle métier. Reprendre `pipeline/genere.py` et `templates/page.html.j2` du dépôt parcours associé, pas le générateur historique backend. Les changements préexistants des worktrees parcours restent à préserver. REC-01 distingue couverture structurelle exhaustive et pertinence sémantique évaluée sur demandes réalistes ; LIV-01 réunit source/index/mapping/pages cohérents et rollback après les accords de publication requis.

### Contrat de référence QUAL-01 — version 1, 13 septembre

**Périmètre :** règles à préserver ou à rendre explicites dans QUAL-02. Le code en service n'est pas modifié par cette spécification. La conformité mécanique, l'adéquation métier et le confort utilisateur sont trois dimensions différentes ; aucune ne prouve les deux autres.

| État logique | Entrée qui autorise la transition | Sortie attendue |
|---|---|---|
| Domaine à choisir | Choix explicite parmi les 14 domaines ; jamais un secteur ou un récit métier pris pour un domaine | Secteur si applicable, sinon objectif |
| Secteur à choisir | Choix reconnu dans la liste offerte pour le domaine ; « Autre » selon l'éligibilité existante | Objectifs applicables à cette combinaison |
| Objectif à choisir | Choix dans la liste offerte pour le domaine/secteur | Problème à demander, ou recherche si un besoin exploitable a déjà été exprimé |
| Problème à préciser | Description libre utile, conservant contexte, négations et exclusions | Recherche limitée par les choix validés ; jamais invention d'une qualification |
| Résultats | Liste réconciliée de cas effectivement issus du catalogue filtré | Sélection de l'un des IDs réellement affichés, puis fiche exacte |
| Fiche et parcours | Identité sélectionnée et mapping valide | Détail verbatim et URL autoritaire ; aucune URL devinée depuis le numéro |
| Clarification / aucun cas | Choix ambigu, contexte insuffisant ou recherche sans cas adéquat | Qualification conservée, correction possible, pas de remplissage hors périmètre |
| Requête interrompue / réponse périmée | Échec ou réponse ne correspondant plus à la question courante | Pas de nouvel état validé sur simple erreur ; reprise explicite |

**Invariants :**

1. Un domaine est un choix métier explicite, pas la profession ou le secteur déduits par le modèle.
2. Un numéro appartient à une question et à ses options : il n'est jamais réutilisé pour l'étape suivante, ni remappé après un changement de liste. Le prochain protocole doit porter cette identité ; le texte seul ne suffit pas.
3. Les valeurs retenues doivent être autorisées dans la combinaison courante. Un champ non vide ne prouve ni son appartenance au catalogue ni sa pertinence métier.
4. Changer le domaine invalide secteur, objectif et résultats ; changer le secteur invalide objectif et résultats ; changer l'objectif invalide les résultats. Répéter le même choix ne détruit pas les dépendances valides.
5. Le besoin donné avant qualification n'est pas perdu ni redemandé inutilement. Une nouvelle clarification utile prévaut ; les anciennes réponses Q3 liées à des choix abandonnés ne doivent pas ressurgir.
6. « Oui », un métier seul, un numéro inconnu, une négation ou une hésitation ne constituent pas par eux-mêmes une nouvelle qualification.
7. La recherche utilise les filtres validés ; l'absence de résultat ne les relâche pas. Les affirmations et bénéfices restent ancrés dans le contenu source.
8. Texte affiché, IDs sélectionnables, ordre, fiche et URL doivent correspondre. La réponse détail peut conserver toute la liste de candidats : son identité s'apprécie par le contenu du cas et l'URL autoritaire, pas par l'exigence d'une liste de longueur un.
9. Les domaines sans Q1.5 restent sans question secteur ; les secteurs ajoutés aux menus viennent des métadonnées, sans renuméroter silencieusement un ancien choix.
10. Une paraphrase de question, un double clic, un délai réseau ou une modification du catalogue ne doit pas changer la signification d'un choix déjà fait. Les limites actuelles à cette règle seront rapportées comme écarts, pas cachées par une moyenne de succès.

**Référence métier :** pour une demande vague ou multi-intention, la réponse attendue peut être une clarification ou plusieurs qualifications acceptables. Les scénarios techniques à objectifs fictifs mesurent le routage et la conservation de l'état, pas la pertinence des 1 021 cas. Toute référence de cas réels doit identifier sa version source et expliciter le statut des attentes (hypothèse, revue experte, validation utilisateur). Aucun taux de précision global ne doit être déduit du seul banc hors ligne.

**Essais ensemble avant déploiement, demande du 13 septembre à 12:16 :** le contrat/corpus de référence a été préparé, mais QUAL-02 n'est pas implémenté. Organiser d'abord une répétition explicitement simulée du dialogue à partir des choix canoniques, puis une préversion technique isolée avec les vraies transitions et filtres. Le diagnostic de test doit distinguer choix confirmé, problème original, filtre réellement appliqué, candidats récupérés et cas affichés ; ne pas envoyer de contenu privé dans un service tiers pour la démonstration. Un accord sur la conversation simulée ne vaut pas preuve de fonctionnement RAG ni autorisation de déployer : Eneric veut donner son accord après les essais.

### Exécuter et interpréter la référence QUAL-01 locale

Fichiers : `backend/tests/fixtures/qualification_reference.json`, `backend/scripts/evaluate_qualification.py`, `backend/tests/test_qualification_reference.py`. Depuis `backend`, `python -B scripts/evaluate_qualification.py --output "<dossier-prive-existant>\qual01-nouveau.json"` produit un rapport neuf, refuse l'écrasement et n'appelle ni réseau, ni modèle, ni catalogue réel. Codes retour :0 pour les vérifications mesurées conformes,1 pour écarts observés,2 pour erreur d'entrée/exécution ; les exigences non évaluées sont séparées.

Référence v1.0.0 :66scénarios,63conformes,3écarts au niveau des helpers (question reformulée non reconnue, numéro d'objectif réinterprété après changement d'ordre, collision avec le préfixe d'un libellé fictif).14domaines testés par numéro et libellé, objectifs volontairement fictifs. Le premier brouillon de fixture heurtait cette collision lexicale ; la provenance décrit l'isolation de la collision dans une sonde dédiée, dont l'échec reste visible. Les attentes n'exigent pas que les bugs persistent.

Commande ciblée exécutée avec `PYTHONPATH=tests` : `python -B -m unittest test_qualification_reference test_chat_regressions test_chat_relevance -q`,102tests réussis. Le succès de ces tests vérifie notamment le banc ; il n'annule pas le code1 de l'évaluation, ni les huit dimensions non mesurées. Empreintes de source et version Python dans le rapport ; un export sans Git l'indique explicitement et conserve les hashes.

Pour une future validation d'image avec cette suite, exporter aussi **la fixture JSON et `scripts/evaluate_qualification.py`** dans le contexte de tests. Les anciens scripts de staging ne copiant que `test_*.py` et le banc de pertinence ne suffisent pas. Le rapport de baseline reste privé ; il ne décrit pas une panne du site ni une mesure exhaustive de pertinence.

### ORI-01 et continuité d'adoption — enseignement de l'essai conjoint

Le filtre principal peut être correct et exclure un cas placé dans un autre domaine que celui choisi naturellement. La proposition ORI-01 ajoute une recherche secondaire d'orientation, sans altérer les sélections actives : `piste proposée → acceptation/refus → revalidation des choix → recherche principale`. Un refus ne change rien ; une acceptation ne permet pas d'inventer un secteur. Les métadonnées et le cas doivent être authentiques, la correspondance directe et les prérequis absents ne doivent pas être supposés.

La preuve conjointe concerne une demande inchangée d'adaptation de descriptions produit à une audience : aucun cas en Marketing, puis cas adapté retrouvé après réorientation commerciale confirmée. Cette réorientation a été préparée manuellement via lecture du catalogue, pas par le bot. La future capacité automatisée reste à construire/évaluer ; ne pas confondre ce résultat avec la réussite du nouveau protocole.

Ne pas abandonner CONT-01/PAR-01 au profit du seul routage : le transfert vers un parcours doit rendre le premier essai faisable et son résultat vérifiable. Le contexte propre à l'utilisateur, absent des pages statiques actuelles, doit rester un complément explicite au contenu source, sans URL contenant le problème libre ni envoi à un service tiers. Tous les1 021cas restent dans le périmètre ; relais humains et réutilisation sont conservés comme suites du parcours, pas comme assistant généraliste.

### Historique du lot livré UX-01 à UX-05

Les cinq frictions post-livraison ont été corrigées et livrées : sélection du cas unique, exemples Q3 trop denses avec pipes bruts, filtre d'exemples Cabinet & conseil, besoin initial du magasin redemandé et suggestion secondaire supposant une saisonnalité. Le classement et les formulations source restent inchangés ; le calibrage de pertinence général reste ouvert.

La documentation a été rapprochée avant l'implémentation. Voir la table active de `ROADMAP.md`. Ne pas relancer l'intégration v461, régénérer les pages, modifier le classeur ou préparer Simplon. Le composant actif est `frontend/src/views/HomeView.vue` ; ses boutons utilisent `suggestedCases` conservé dans chaque message. La réponse détail peut contenir plusieurs candidats : la présence de candidats seule ne suffit pas, le CTA autoritaire `parcours_url` et le marqueur de détail restent prioritaires. Le retour à la liste restaure ces candidats, pas ceux du dernier détail.

Les exemples Q3 utilisent l'éligibilité sectorielle de Q2, conservent le filtre intention et limitent à quatre situations après séparation/dédoublonnage. Une intention invalide ne doit pas revenir à tous les exemples du domaine. Le besoin initial reste réutilisable lors d'une correction ; un Q3 donné sous d'anciens choix est au contraire invalidé.

**Reproduire hors ligne depuis `backend` :** définir `PYTHONPATH=tests` puis lancer `python -B -m unittest test_haystack_rag test_chat_regressions test_chat_relevance test_case_selection_prompt test_relevance_evaluation test_catalogue_integration -q`. Définir `PARCOURS_SOURCE_ROOT` vers le checkout parcours rapproché pour inclure les contrôles associés. Depuis `frontend` : `npm run check:chat`, `npm run type-check`, `npm run build-only`.

**Évaluer UX-05 :** `python scripts\evaluate_chat_relevance.py --suite stock-assumptions --repeats 2 --max-completion-tokens 6000` prépare les huit requêtes sans réseau. Ajouter `--live --subscription "<abonnement-dev>" --resource-group rg-avoulia-fr-dev --container-app avoulia-backend --interval-seconds 90 --output "<dossier-prive-existant>\ux05.json"` uniquement pour un passage autorisé. Aucun classeur n'est lu ; les rapports contiennent les réponses brutes fictives et les paramètres, pas les identifiants d'authentification. Ne pas transformer les attentes techniques en taux de précision utilisateurs.

**Recette utilisée pour ce lot :** `Dockerfile.dev-catalogue-code-fix` avec l'image r3 épinglée ci-dessus et un contexte privé minimal. L'overlay doit comprendre **`app/haystack_rag.py` et `app/rag_constants.py`** ensemble ; inclure les tests et le banc à jour dans le paquet de validation. L'ancien `Dockerfile.dev-code-only` du 10 septembre ne copie pas `rag_constants.py` et ne suffit pas à ce lot. Hériter catalogue/pages/mapping, préserver les exports hors webroot, et valider dans l'image avant bascule. Pas de régénération ou d'effacement d'index ; un remplacement de réplique peut néanmoins reconstruire son index local au démarrage.

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
