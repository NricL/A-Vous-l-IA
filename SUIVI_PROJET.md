# Avoulia V2 — Suivi Projet & Décisions

### 15septembre — accès direct après choix demandé à12:17, livré

Titre source puis CTA parcours immédiatement dans la réponse confirmée ; pas de
nouvelle répétition des détails des cartes. URL et libellé CTA serveur préservés,
fallback ancien si identité non établie, historique brut/API inchangés.
Source `4fbbd24`, frontend `v463-handoff-20260915-r1` sain à100%, build `dd3d`,
digest `a16be7062be07fc084167dee7064fdbf0b8ff27a9a0922fb96ab01f9c799c204`.
Rollback détails r1 actif ; backend accessibilité r1 inchangé.
51tests frontend, typage/build, fixtures et recettes réelles candidate/Azure/Pages,
clic/numéro et320/390/1280px réussis. Pages `34958051205`, CI `34958051185`.
Reçu : `_local-trace/2026-09-15-direct-handoff/deployment-receipt.json`.
Priorité d'affichage uniquement, pas de gain de latence annoncé. Base/éditorial/
parcours inchangés, kit et gel en pause, classeur/prototypes exclus.

### 15septembre — libellé demandé à11:07, livré

« Plus de détails » remplace uniquement le résumé « Premier essai » des cartes.
Source `57f59c6`, frontend `v463-details-20260915-r1` sain à100%, build `dd3c`,
rollback compact r1 actif ; backend inchangé.46tests frontend, typage/build et
recette réelle clavier/rechargement Azure/Pages réussis. Pages `34951318376`,
CI `34951318397`. Reçu : `_local-trace/2026-09-15-details-label/deployment-receipt.json`.
Autres mentions de premier essai, contenu, parcours et kit en pause inchangés.

### 15septembre — correctif compact demandé à10:28, livré

Source `e2b3fe2` : seules les deux sources frontend changent. Cartes bleu nuit,
titre/gain potentiel au premier regard, détails conservés dans « Premier essai » ;
valeurs confirmées sous Domaine/Secteur/Objectif plutôt qu'un bandeau séparé.
Ce choix remplace les cartes blanches et le contexte séparé du lot précédent.

Frontend `v463-compact-20260915-r1`, sain à100%, build `dd3b`,
digest `d8eb2bb8deb2bdbabfac2bef5a40484d98b2a3192d810a179d1d4038d8be38b3`.
Rollback accessibilité frontend r2 actif ; backend accessibilité r1 inchangé à100%.
Pages `34948147883` / CI `34948147776` réussies.46tests frontend et typage/build ;
recette candidate réelle3cas puis Pages5cas, cas unique simulé, accordéon clavier,
contrastes≥4,5 et320/390/1280px sans débordement ni contexte tronqué.
Cache/rechargement ordinaire vérifiés, six HTML backend inchangés, chemins privés404.
Pas de modification éditoriale, base, runtime ou parcours, pas de lecteur d'écran
réel ni certification revendiqués. Classeur et prototypes préexistants exclus.
Reçu : `_local-trace/2026-09-15-compact-cards/deployment-receipt.json`.
**Kit en pause depuis10:23, non repris.** Aucun packaging ni gel actualisé ;
un gel antérieur reste un instantané historique, pas cette nouvelle révision UI.

### 15septembre — consolidation finale reprise et livrée

Choix06:31, pause06:50, reprise08:24 : modifications conservées et état distant
relu avant écriture. Backend `v463-accessibility-20260915-r1` / frontend
`v463-accessibility-20260915-r2` sains à100%, builds `dd38`/`dd3a`.
Source publique `1efdaa6`, gabarits privés `c67b422`.
Pages `34938049102` et CI `34938049142` réussis (239tests,5ignorés).

Contraste des cartes/choix et textes d'aide, focus de lecture/clavier, erreurs/
attente et copie annoncées, nom accessible conforme au libellé visible corrigés.
Un conflit CSS réellement détecté sur la candidate r1 a motivé la r2 du seul
frontend : pied de page isolé des vues légales, r1 jamais promue.
Ratios≥4,5 pour les textes normaux testés ; mobile320/390 et bureau1280 sans overflow.
164tests locaux backend/gabarits,152dans l'image,43frontend, typage/build.
Fixture d'erreurs/reprise distincte des essais réels API et navigateur ;
Pages→plusieurs cartes→bon parcours, copie réelle, bilan non conservé et cache
ancien rechargé normalement vérifiés. Détails/critères WCAG dans `HANDOFF.md`.

Overlay1 021pages : champs sources, prompts, six étapes et éditorial inchangés ;
quatre historiques intacts. Aucun classeur ouvert ni publié, modification privée
préexistante et prototypes conservés. Bot/base/taxonomie inchangés ; rollback
éditorial r2 conservé. Pas de certification ni de test avec lecteur d'écran réel.
Reçu durable : `_local-trace/2026-09-15-accessibility/deployment-receipt.json`.
**Lot clos** ; essais métier/taxonomie à Eneric, packaging Simplon non lancé.

### 14septembre — complément éditorial des1 021cas

`editorial-value-2` :5 105champs qualitatifs rédigés depuis les seuls HTML déjà publics,
avec citations et empreinte des champs source.75formulations corrigées lors du contrôle
complémentaire ; aucune validation métier humaine ou mesure de ROI revendiquée.
Gain, premier livrable et condition d'observation apparaissent tôt dans les cartes,
la fiche et le parcours ; préparation/relecture restent à mettre en balance.
Backend/frontend Azure `v463-editorial-20260914-r2` à100%, builds `dd37`/`dd36`,
source fonctionnelle `f21a869`, correctif de publication `8529418`.
161tests ciblés locaux,149dans l'image,38frontend,
18chemins HTTP/SSE et recette réelle avec plusieurs propositions puis lien du bon cas.
Base, sélection, prompts, six étapes et quatre pages historiques conservés.
Le socle précédent reste disponible pour retour arrière ; reçus dans la trace locale
`2026-09-14-value-editorial`. **Gain mesuré et durée avant valeur : non établis pour les1 021cas.**
Pages `34888127182` et CI `34889281059` réussis (236tests,5ignorés).
La r2 corrige les dates de fichiers de l'image : ancien cache réellement testé,
contenus inchangés, navigation canonique et rechargement ordinaire vérifiés.

### 14 septembre à19:56 — valeur source et expérience livrées

Backend `v463-value-20260914-r1` et frontend Azure `v463-value-20260914-r2`,
sains à100% ; retour arrière Q3/backend et UX/frontend conservé et vérifié.
Sources `332a9b7` / `0132017`, Pages `34877371015` et CI `34877370929` réussis.
137tests dans l'image,38tests frontend,18chemins de qualification comparés,
recette réelle finale Pages→plusieurs cartes→fiche→parcours.1 021présentations
sourcées et quatre historiques conservées ; zéro enrichissement éditorial riche
généralisé. Base/prompts/filtres et comportement de sélection inchangés.
Le bilan n'est pas stocké et la copie du lien exclut le contexte personnel.
Les essais d'adoption, réserves métier et le packaging Simplon restent distincts.

### 14 septembre à19:09 — réalisation/tests/déploiement autorisés, expérience uniquement

Implémentation locale : contrat valeur source seul commun au bot et aux1 021parcours,
cartes identifiées, domaine initial explicite, contexte lisible, attente/reprise
honnêtes, passage vers l'assistant choisi, bilan facultatif et lien réutilisable.
Sources, prompts, filtres, classement, IDs, six étapes, modèles et base inchangés ;
aucun classeur lu ou modifié. Les quatre pages historiques restent intactes.
Pas de généralisation fictive des quatre brouillons : couverture éditoriale riche0,
couverture de présentation sourcée1 021. Tests locaux et contrôles navigateur
passés, candidates Azure en cours de préparation ; publication à confirmer par reçu.
Rôles d'Eneric et périmètre Simplon inchangés. Détails dans `HANDOFF.md`.

### 14 septembre à18:43 — aperçu VAL-01 par scénario validé

Demande de retirer la galerie : besoin fictif → cas illustratif → fiche → entrée
du parcours, un seul scénario visible. Changement de scénario réinitialisant l'étape,
navigation avant/arrière sans mélange des cas. Même artefact local et URL4191.
14 tests synthétiques et navigation clair/sombre à390/1280px. Ancienne galerie
archivée dans la trace VAL-01. Aucun raccordement API, édition de base ou déploiement ;
validation limitée au déroulé de l'aperçu, pas aux1021cas.

### 14 septembre à18:23 — VAL-01 lancé, quatre aperçus locaux

Inventaire du contrat servi : pas de champ gain/ROI/horizon dédié, sans conclure
sur des colonnes Excel non inspectées. Prototype séparant hypothèses éditoriales
et sources exactes, avec identité/hash/citations et refus des données manquantes.
Atelier liste/fiche/entrée du parcours pour quatre cas publics contrastés ; aucune
généralisation aux1021cas, modification de classeur, API, frontend ou parcours actif.
Aperçu `http://127.0.0.1:4191/`, artefact `avia-valeur-apercu-2.html` dans Microsoft Scout.
12 tests et navigation mobile/desktop clair/sombre. Format à valider avant raccordement.
Détails de provenance, limites et reprise dans `HANDOFF.md`.
Aucun commit, push ou déploiement ; les travaux précédents de roadmap restent locaux.

### 14 septembre à18:15 — roadmap valeur et expérience de choix

Cadrage consigné dans `ROADMAP.md`, section « Programme actif — valeur visible et
expérience de choix ». Ordre : bénéfice/horizon de valeur et continuité dans le
parcours, comparaison des cas, démarrage/contexte, attente/reprise et passage vers
l'outil ; retour ultérieur, confiance et accessibilité également cadrés.
Premier lot VAL-01 : inventorier les champs et définir leur provenance avant
aperçus communs liste/fiche/parcours. ROI potentiel qualitatif et conditionnel,
aucun gain chiffré ni conformité garantie inventés. Catalogue source inchangé.

Eneric garde les essais d'usage, leurs corrections et les cinq réserves métier.
Packaging Simplon différé. Mise à jour documentaire locale uniquement ; aucun
changement applicatif, classeur, commit, push ou déploiement dans ce jalon.
La révision Q3 `v463-q3-20260914-r2` reste celle en ligne.

### 14 septembre à13:56 — préparation explicite et étapes complémentaires

**Publié après confirmation à14:48.** Révision `v463-preparation-20260914-r1` à100%,
image `a8a6cf7cde6cb48f59ffe4e15e1943229f962fcbbb084d434bc2447426917ff8`.
Le bot, la base métier v463, les URLs et les quatre pages historiques restent inchangés.
La révision v463 précédente et son image sont conservées.

Clôture de publication : sources `3f7bf8b1499989f99c7fedbd434793fad217fb7f`
et `8989942a53690b4901e2a6216059f06ca1692671`, CI `34849464018` réussie.
Le frontend n'a pas changé ; aucun nouveau build Pages/Azure frontend requis.
La page publique du retour utilisateur expose bien les prompts révisés, les six
étapes et le passage à la production, sans débordement mobile. Aperçu local arrêté.
Reçu détaillé : `../_local-trace/2026-09-14-preparation-prompts/deployment-receipt.json`.

Le retour utilisateur valide le déroulé du bot mais demande de revoir tous les prompts
de préparation. Inventaire des seuls champs v463 déjà publiés :1 021cas,3 774prérequis,
3 677libellés distincts. Quatre relectures sémantiques disjointes couvrent tout le lot ;
les empreintes et IDs sont rapprochés, sans accès aux onglets privés d'audit.

Le gabarit local cible une seule entrée, un format concret et un état prêt/partiel/bloqué.
Les références existantes restent sourcées, les données absentes ne sont pas fabriquées,
les entrées facultatives ne deviennent pas obligatoires. Les cas de données à garder
localement, d'essai fictif imposé, de période/régime/outil à confirmer et de pièce couvrant
plusieurs entrées sont traités par le contrat partagé, sans retag ni exception codée par ID.
L'étape4 réutilise cette préparation et demande seulement les manques bloquants ;5teste,
6capitalise. Le bot et la base métier ne changent pas.

Après un premier essai IA trop répétitif, une seule révision supplémentaire a imposé
un format et une fiche uniques. Les réponses IA restent susceptibles d'être longues
ou de contenir des hypothèses/conseils à vérifier ; aucun score automatique de justesse
n'est revendiqué. Les deux séries de trois appels fictifs et les sources sont conservées.

Candidate finale régénérée :1 021+4pages,3 774blocs identiques au générateur,32contrôles
locaux et quatre pages mobiles. Premier snapshot conservé mais remplacé après détection
de changement de source. Gabarits et documentation locaux uniquement ; pas encore de
commit, ACR ou publication à ce stade historique de préparation.

La construction a ensuite été reprise après un échec réseau de la CLI sans création
de run. L'archive native vérifiée (1 064fichiers identiques) a été transmise par HTTPS
et soumise via les APIs ARM documentées : run `dd2v` réussi,239contrôles backend,
20parcours et payload1 021+4. Les secrets/URLs signées ne sont pas conservés dans les reçus.
Candidate contrôlée puis bascule ; neuf pages/chemins privés et quatre parcours mobiles
confirmés. Les résultats d'IA fictifs antérieurs restent des observations limitées,
pas une garantie de justesse des réponses d'un assistant externe.

### 14 septembre — livraison v463 clôturée

Sources publiées : `830d2b0976d99a1622fc373437c873d1d90c7e1c` (chatbot/HTML)
et `e61e4873a6d714aae24eb67003123d73a74def26` (parcours privé).
Pages `34835285869` et CI `34835285888` réussis ; les avertissements de lint
informatif préexistants ne sont pas modifiés dans ce lot.
Les anciennes révisions expérimentales backend/frontend sont confirmées inactives.
Le backend principal est v463 à100%, le frontend Azure stable garde son image et son
trafic ; son proxy et le vrai parcours ouvert depuis Pages utilisent la nouvelle base.
La seule modification utilisateur du classeur historique privé v453 reste non stagée.

Trace privée complète : `../_local-trace/2026-09-14-v463-publication/deployment-receipt.json`.
Les nouvelles pages sont byte-identiques à l'image ; l'indentation des lignes vides
générées est conservée, plutôt que réécrire les sorties pour une règle de whitespace.
Le contrôle de diff des sources manuscrites reste appliqué.

La candidate `avoulia-backend--v463-20260914-r1` a été créée depuis le template
du stable, avec références de secrets et index distinct. Image privée `dd2u`,
digest `5de8ca8cc8f46828b8a62ddf83b7a47f0c9afb767b2d75720f6558a6e0c95182`.
Elle a été exercée avec le stable à100%, puis le trafic principal est passé à100%v463.
L'ancien stable et son image restent conservés. Aucun nouveau modèle ou quota.

1 021pages générées depuis le contenu explicitement autorisé et quatre historiques
préservées ; mêmes associations ID/hash. Les HTML publiables sont synchronisés dans
les sources, le CSV de mapping est retiré du HEAD public (historique non réécrit).
Le classeur complet, sa protection et les audits restent hors du dépôt/public webroot.

La recette réelle retrouve le cas produit, accepte plusieurs propositions utiles et
ouvre le bon parcours via HTTP/SSE et Pages. Sur quatre parcours, six étapes,
navigation au prompt et progression fonctionnent à390px sans débordement. Le besoin
initial est réutilisé et n'est pas injecté dans le prompt générique de la page.

Incidents tracés : premier build `dd2t` arrêté sur un ancien titre attendu, corrigé
sans affaiblir le contrôle ; réponse PATCH Azure asynchrone sans objet applicatif,
puis état relu sans renvoyer la création ; copie PowerShell lente reprise par copie
native idempotente avec vérification des1 025empreintes. Aucun échec masqué par une
nouvelle règle de sélection ou un faux résultat vide.

### 14 septembre à12:13 — publication v463 autorisée

Après relecture positive des quatre exemples, Eneric confirme la publication du
périmètre exact :1 021fiches `Sheet1`, parcours génériques, bot existant avec seul
correctif de coupure et suppression du moteur expérimental. Classeur complet,
audits/commentaires/arbitrages et mapping restent privés.

La copie canonique a été réenregistrée, mais une comparaison de toutes les cellules,
formules et caches confirme l'identité de contenu avec la version relue. Un nouveau
staging est préparé :1021pages actuelles, quatre historiques et mapping conservés,
image privée issue du stable, candidate sans trafic avant recette et bascule.
Une erreur de connexion Azure CLI en lecture est contournée par des appels ARM bornés ;
aucun changement de compte, de modèle ou de quota.

### 14 septembre après 11:29 — candidate de contenu v463 préparée

La v462 et sa revue complète ont été rapprochées :370cellules métier corrigées dans
la passe précédente,547propositions arbitrées et couverture1 021cas. La dernière
passe applique seulement quatre ajustements de premières actions/prérequis, puis
ajoute quatre aperçus protégés dans une nouvelle version v463. Aucun contenu privé
ne figure dans ce journal public.

Enregistrement/recalcul par Excel natif, étiquette conservée ; le convertisseur
LibreOffice n'est pas utilisé pour éviter de perdre la protection. Un défaut du
vérificateur sur cellule vide a été corrigé avant la relecture finale, sans réappliquer
les changements. Contrôle final : source inchangée,24feuilles conservées,6 158formules,
zéro erreur de cache, quatre modifications exactes et32lignes d'aperçus.
Les cinq réserves de classement existantes restent inchangées.

Les aperçus reprennent réellement les six étapes et prompts générés en mémoire,
mais sous forme de texte dans Excel ; aucun HTML non protégé créé. La publication
reste en attente de validation explicite du contenu, sans nouveau build/déploiement.
Trace hors dépôt : `../_local-trace/2026-09-14-content-finalization/journal.json`.

### 14 septembre à 10:59 — passer aux améliorations de valeur d'usage

Eneric estime les recommandations suivantes plus importantes que poursuivre la sélection.
Le prompt du bot est revenu à l'identique de la source existante ; seul le correctif
intrafiltre reste. L'évaluation à ID unique était trop stricte pour la découverte
de cinq pistes. Le lot public interrompu conserve aussi une vraie limite observée sur
la recette de gâteau (propositions de contenus marketing) ; ni ce défaut ni la présence
du bon cas dans les trois demandes produit ne mesurent le stable avant/après.
Pas de nouveau modèle, filtre, vérificateur ou essai de formulation.

Les gabarits de parcours sont maintenant le chantier actif : accueil raccourci en une
carte, prérequis en langage courant et trois contrôles concrets à l'étape4.
24contrôles ciblés bot/parcours et9contrôles synthétiques du générateur passent.
Cela porte sur les sources du générateur, pas les1 021pages publiques ou le classeur.
Nouvelle trace : `../_local-trace/2026-09-14-parcours-priority/journal.json`.

La construction privée dd2s avait réussi, mais son prompt a été retiré depuis :
aucune activation de cette image. La livraison du bot est différée ; stabilité et
contenu réellement servi restent inchangés.

### 14 septembre à 10:21 — efficacité et pertinence, recentrage 80/20

Eneric confirme : intention = action/objet/livrable ; cas et parcours génériques,
adaptation par l'usager. Le bot existant est conservé. Nettoyage effectif des37fichiers
du moteur parallèle et de ses interfaces/tests/recettes spécifiques ; sept fichiers
d'intégration frontend/CI/Pages remis au fonctionnement stable. Les27fichiers R2 ont
été rapprochés par SHA256 de l'archive immuable avant toute suppression.

Le correctif de pool intrafiltre est conservé ; le prompt de sélection existant distingue
contexte facultatif et activité réellement différente, sans ajouter de modèle ni de
personnalisation. Le générateur privé garde les six étapes, prérequis, contrôles et
réutilisation, mais retire le contexte ajouté au presse-papiers et les overrides de test.
Le classeur utilisateur modifié n'est ni lu, ni écrit, ni indexé.

La roadmap actualisée remplace les instructions R2 : priorité au correctif du bot,
puis aux1 021fiches et parcours génériques. Réorientation, relais humains et bilan
volontaire sont différés. Pas de refonte graphique, taxonomie, nouveau modèle ou quota.
Sources locales seulement, aucune livraison distante ; la r1 distante reste inchangée.
Trace détaillée hors dépôt : `../_local-trace/2026-09-14-8020/journal.json`.

Clôture locale :132contrôles du bot existant,39contrôles croisés parcours/publication,
31contrôles frontend avec types/build,11contrôles synthétiques du générateur.
Le banc existant a réalisé huit appels modèle sur fixtures : huit résultats conformes,
dont les trois formulations produit, cible sans vidéo imposée, données à préparer,
vidéo explicitement demandée, traduction seule et absence de correspondance.
Zéro erreur de transport/troncature sur ce lot borné ; ce n'est pas une recette de
récupération sur le catalogue réel ni une preuve de performance utilisateur.
La revue indépendante des deux diffs n'a trouvé aucun problème significatif.
Les anciens serveurs locaux de préversion ont été arrêtés ; aucune action cloud.

### Historique — publication r1 puis correction de fiabilité abandonnée

**Fin de passe : r2 non livrée.** Les opérations courtes, sessions concurrentes, reprise/annulation et récupération réseau sont implémentées et exercées. La validation sémantique ne passe pas : le dernier vérificateur rejette encore un cas GenZ adapté et a épuisé son budget sur un contrôle spécialisé. Le code reste local ; aucun nouveau push ou endpoint Azure. Le build privé `dd2r` n'a pas produit d'image finale. Les serveurs r2 temporaires ont été arrêtés ; le stable et r1 restent inchangés.

Le lot exact approuvé à07:20 a été publié : chatbot `812aa94`, gabarits privés `5c748ef`, Pages `34809713720` et CI `34809713718` réussis. Révisions backend/frontend `qual-20260913-r1` saines à0% du trafic principal, révisions stables à100%. Source PUBLIC_PAGES v4.6.1 uniquement.

Le chemin nominal GenZ a retrouvé UC-0706 sans réorientation ; le parcours réel s'est ouvert depuis Pages avec besoin conservé et six étapes, sans débordement à390px. Mais une réorientation a expiré après242s ; une recherche bloquait aussi la création d'une autre session. Un essai navigateur a renvoyé502 du vérificateur, avant succès d'une seule relance. Les bandeaux « NON DÉPLOYÉ » étaient obsolètes et Pages utilisait un fallback404. Aucun de ces constats n'est effacé du bilan.

À08:03, Eneric demande de corriger puis déployer. Trois scopes séparés : serveur asynchrone/atomicité, vérification référencée/quotas, interface polling/annulation/reprise. Le parent intègre gabarits, packaging, documentation et recette. R2 utilise un protocole d'opération additif, un budget partagé borné et des références déterministes vers les preuves fournies ; modèles, filtres, source et six étapes inchangés. Les contrôles sémantiques ciblés ne valent pas validation exhaustive de tous les besoins.

### 13 septembre à 20:47 — livraison de test GitHub/Azure demandée

Changement de séquence demandé : héberger une candidate isolée puis poursuivre les essais, plutôt que terminer les essais en local. La version stable garde son trafic principal ; pas de promotion automatique. La candidate reste PUBLIC_PAGES v4.6.1, sans la v462 privée, avec identité AVIA et fiche terminale courte suivie du parcours.

Adaptations cloud préparées : authentification par références de secrets existants, origines HTTPS explicites, pairs proxy bornés, une réplique/worker, build context en liste blanche, image finale sans ancien payload privé. La revue a corrigé l'import `Request` requis par Python 3.11 et l'ouverture du lien parcours depuis Pages sans affaiblir les contrôles API/session. Le premier build a révélé la dépendance Beautiful Soup manquante ; elle est désormais déclarée. Images privées construites séparément ; activation publique non encore effectuée à ce point.

Les limites de latence et de périmètre restent ouvertes. Les détails et l'ordre de livraison/rollback sont consignés dans HANDOFF et `.azure/plan.md`. Le dernier reçu stable reste celui du matin ; les comptes rendus suivants sont historiques.

### Suite du travail demandé à17:45 — RAG réel local et candidate privée

Le faux négatif intrafiltre a été expliqué : le cas adapté était dans le pool de26candidats, mais une limite de5 appliquée avant le modèle l'excluait. Correctif dans les sources locales du cœur RAG et régressions associées ; aucun changement du backend déployé.

La préversion `http://127.0.0.1:4178/preview` utilise maintenant les1 021fiches publiques v4.6.1, leurs embeddings et les modèles Azure existants ; la qualification reste pilotée par le code. Consentement préalable, recherche principale filtrée, orientation séparée confirmable, fiche terminale puis nouveau parcours local. Aucun contenu des classeurs General ni de la candidate v462 n'a été exporté dans ce corpus.

Le besoin GenZ initial retrouve son cas marketing sans réorientation. Vérification indépendante ajoutée pour les conditions non exprimées ; tests réels négatifs et positifs réalisés, sans masquer leurs échecs intermédiaires. Limites encore ouvertes : portée trop large d'une suggestion secondaire web et latence70–305secondes selon le flux. La préversion n'est pas déclarée prête pour production.

Les1 021champs de parcours publics ont été rendus en mémoire avec les nouveaux gabarits, contexte séparé et aucune valeur de mode inventée. Quatre pages historiques sont exclues ; source brute privée et index de production distincts. Une revue a aussi identifié et fait corriger l'activation de télémétrie sur certains alias de route locale.

Le travail de contenu a abouti à une candidate privée labellisée, avec arbitrages et journal, sans écraser la v461. Détails conservés dans le classeur, pas dans ce dépôt. Aucun push ni déploiement ; accord après essais conjoints toujours requis.

### 13 septembre — lecture locale autorisée et revue documentaire complète

Après accord explicite à16:43, la v461 a été inspectée, rapprochée de l'empreinte déployée et copiée sans changement d'octet ou d'étiquette. Lecture en mémoire des1 021cas, contrôle de l'inventaire et revue en quatre groupes disjoints, puis consolidation en classeur labellisé. Couverture complète et valeurs avant des propositions rapprochées de la source ; détails réservés aux classeurs de revue, hors dépôt public.

Les propositions ne sont pas appliquées à la base ; aucune nouvelle version source, indexation réelle, connexion de la vraie base au navigateur, publication ou déploiement. Les modes d'exécution et points incertains nécessitent un arbitrage cohérent. La préversion locale reste sur fixtures.

Correction de diagnostic : la lecture directe a trouvé un cas éligible dans le périmètre initial d'un essai resté sans réponse. La réorientation manuelle réussie ne prouvait donc pas que le classement était l'unique cause. Ce faux négatif doit être étudié avant d'automatiser la récupération entre domaines.

### 13 septembre — préversion locale, suite au lancement demandé à13:37

Trois chantiers exécutés séparément (bot, parcours, accès/revue du catalogue), puis intégration et revue de code. Préversion accessible sur `http://127.0.0.1:4178/preview`, serveur indépendant8767, explicitement **16cas fictifs / aucun RAG v461**. Qualification serveur par question/révision et identités, choix boutons/numéros/libellés, réorientation avec acceptation/refus et fiche terminale avec un seul lien vers les six étapes locales.

Gabarits du dépôt parcours modifiés en source seulement : décision d'adéquation, prérequis sans données inventées, contexte local copié séparément, livrable et vérification, comparaison puis réutilisation. Six étapes et champs source préservés ; aucune régénération des1 021pages, aucun classeur modifié.

Revue intégrée : deux défauts corrigés, lien de transfert pouvant changer de cas avec la session et brouillon effacé après choix invalide. Liens désormais liés à une révision ; récupération sans transition conservant la saisie.39tests Python du protocole/rendu et44tests Node preview/legacy réussis, types frontend ; navigation finale sur le serveur réel local jusqu'au parcours avec besoin conservé.

CONT-01 bloqué avant couverture exhaustive :48IDs seulement énumérés dans un essai M365, total/version/champs exacts non certifiés,0revue complète acceptée dans ce lot. Les recommandations portent toujours sur tout le catalogue ; la fixture ne le remplace pas. Pas de push ou déploiement ; code servi `d02ffad` et v461 inchangés. Détails de lancement, limites monoprocessus et condition d'accès aux données dans HANDOFF.

### 13 septembre à 12:36 — référence QUAL-01 et premier essai conjoint

QUAL-01 dispose localement d'un contrat, d'un corpus JSON versionné et d'un évaluateur hors ligne, sans modification du runtime.66scénarios :63conformes et3écarts cibles documentés ;14domaines par numéro/libellé, objectifs fictifs.102tests liés réussis. Les trois écarts sont au niveau des helpers, pas des incidents live établis. Source, limites, provenance des fixtures et commandes dans HANDOFF ; aucune couverture des1 021cas revendiquée par ce banc.

L'essai conjoint a mis en évidence une limite métier distincte : un cas adapté peut se trouver hors du domaine initial pourtant naturel pour l'utilisateur. Une réorientation confirmée a permis au RAG réel de le retrouver. Elle a été préparée manuellement, pas proposée automatiquement par le bot ; pas de modification des filtres à l'insu de l'utilisateur.

ORI-01 est ajouté comme proposition à éprouver : recherche secondaire d'orientation dans la base après une impasse, cas et autre classement expliqués, acceptation avant modification, refus conservant l'état. Les autres recommandations Bpifrance/DGE/France Num restent actives : trouvabilité et contenu des1 021cas, faisabilité du premier essai, contrôle métier, réutilisation et relais humains. La continuité du besoin particulier entre chat et page statique doit également être examinée, sans réécriture du contenu source.

À ce stade : documents et trois fichiers du banc local uniquement ; aucun changement du bot, de la base ou du déploiement. Les essais conjoints se poursuivent sur le parcours ; accord explicite requis avant toute livraison.

### 13 septembre 2026 à 11:55 — prochaines étapes révisées, documentation uniquement

Eneric demande de consigner les recommandations après avoir précisé deux contraintes : améliorer **tout le catalogue et ses 1 021 parcours**, pas un pilote de vingt cas ; conserver la qualification explicite par domaines, qui structure le RAG et distingue AVIA d'un assistant généraliste. La qualité de qualification prime sur le naturel conversationnel. La proposition antérieure de découverte libre ou de classification implicite par le modèle n'est pas retenue.

Programme prévu dans `ROADMAP.md` : QUAL-01 contrat/invariants et référence métier ; QUAL-02 état explicite backend/frontend ; CONT-01 revue de tous les cas, pouvant avancer en parallèle après fixation des critères ; QUAL-03 présentation naturelle maîtrisée ; PAR-01 six étapes plus opérationnelles sur tout le catalogue ; REC-01 robustesse et non-régression métier ; LIV-01 livraison cohérente après autorisation. Aucun de ces lots n'est commencé par cette mise à jour.

Point technique justifiant l'ordre : une partie du code déduit encore l'étape des mots de la question. Le contrôle en lecture seule a confirmé que la formulation actuelle « objectif principal » est reconnue, contrairement à « Pour vos stocks, quelle est votre priorité ? ». Changer seulement les textes ou ajouter des paraphrases LLM ne fiabiliserait pas la qualification. Les choix et leur contexte doivent devenir explicites dans le protocole avant une variation importante de l'interface.

La revue de contenu doit distinguer ambition du cas, premier essai réellement exécuté et déploiement technique, puis prérequis/droits/outils, effort, contrôles et suites. Elle couvre chaque ID, y compris les cas laissés inchangés avec justification. Pas de génération générique présentée comme revue métier exhaustive ; incertitudes explicites et conservation des versions Excel.

Les surfaces documentaires mises à jour sont README, ROADMAP, SUIVI_PROJET, CHANGELOG, HANDOFF, IMPLEMENTATION_SUMMARY et le plan Azure. Les reçus des livraisons restent conservés ; code `d02ffad`, documentation publiée `e895cab`, v461 et parcours inchangés. Pas de modification de code, classeur, mapping, index ou page ; aucun commit, push, appel modèle réel ou déploiement dans ce lot documentaire.

### 13 septembre 2026 — lot UX publié et déployé, état faisant foi

Publication approuvée à09:57 et effectuée par `d02ffad38720757f53d15b81519d4f282e1b07a5`. Pages `34746510034` et CI `34746509999` réussies. Backend et frontend Azure `--ux-20260913-d02ffad` Healthy, 100 % du trafic. Les cinq correctifs UX-01 à UX-05 sont en ligne ; les paragraphes « locaux » ci-dessous sont historiques.

Backend ACR `dd2k`, digest `058fe52822fea24c4e52e17b27242480f3ab96771b883243d8bad7efb2aaaafb` ; frontend `dd2m`, digest `2ae5e263bb60ecf245c4ad59658de07323a902da858d60c42cb26c22d4cfee18`. Sources exportées depuis le commit exact ; deux modules applicatifs superposés à r3. Aucun nouveau classeur, mapping, page ou secret dans le contexte de build.

Validation de l'image Python3.11 :212 tests backend avec un test Node ignoré,8 de rapprochement et payload privé inchangé. Recette réelle candidate puis URL normale : qualification Cabinet & conseil HTTP/SSE, quatre exemples sans pipes, besoin magasin non redemandé, détail source et URL corrects, hors sujet refusé puis reprise. Pages390px : sélection unique cliquable et retour au troisième cas d'une liste ; Azure desktop1280px : même Q3, sans débordement. Neuf empreintes de pages et quatre refus404 de fichiers privés confirmés.

Une première commande ACR utilisait un mauvais répertoire courant, sans build lancé ; relance depuis les contextes dédiés. La CLI Azure a perdu une réponse réseau après le changement de mode et a échoué sur l'affichage Unicode d'un log : l'état réel a été relu via ARM avant toute action suivante. Premier contrôle santé trop tôt, pendant la reconstruction d'index ; aucune promotion avant Healthy. Le smoke test avait supposé à tort que le détail ne pouvait renvoyer que l'ID sélectionné, alors que son contrat conserve parfois la liste : assertion corrigée sur le titre/description et l'URL autoritaire, sans modification du produit.

Mode Single restauré, seule la nouvelle révision backend reste active ; r3 et ses images sont conservées, inactives. La v461 et ses parcours sont inchangés ; l'index de la nouvelle réplique a été reconstruit sans effacer celui de la précédente. Package Simplon différé. Pertinence universelle non garantie ; les exemples restent tributaires du classement et du vocabulaire de la base.

### 13 septembre 2026 — finalisation publiée et reprise UX

La finalisation est terminée : chatbot `24e145b` et parcours `a500a22` publiés sur leurs branches `main`. Pages `34743193980` et CI `34743193992` terminées ; frontend Azure `avoulia-frontend--v461-20260913`, backend r3 inchangé. Les deux frontends affichent 1 021 cas, 14 domaines métier et 71 intentions. Aucun classeur, audit ou mapping ajouté à cette publication.

Les simulations post-livraison ont révélé cinq points restant ouverts : bouton absent pour un cas unique ; exemples Q3 en groupes à pipes, trop nombreux ; exemples incohérents dans Cabinet & conseil / relation client ; besoin initial redemandé dans le scénario magasin même sans retour arrière ; piste secondaire dépendant d'une saisonnalité non mentionnée.

Eneric autorise le 13 septembre la mise à jour des documents puis les corrections en autonomie. Lots UX-01 à UX-05 dans `ROADMAP.md`, maintenant implémentés localement ; aucun nouveau déploiement. Base et parcours inchangés ; package Simplon différé. Les états datés « reste à publier » ci-dessous sont historiques.

**Résultat local :** bouton du cas unique piloté par les métadonnées ; au plus quatre exemples individuels Q3, filtrés par secteur/objectif ; besoin initial français réutilisé, sans transformer une simple présentation en problème ; sélection instruite de rejeter les hypothèses métier non exprimées. Restauration de la liste/ordre au retour depuis une fiche également corrigée. Détail des causes et fichiers dans le changelog.

**Portée des contrôles :** 171 tests backend ciblés, 31 frontend, build/types/composants ; navigateur à 390/1280 px sur frontend construit avec SSE fictif. Test de qualification Cabinet & conseil et réutilisation du besoin magasin dans les deux routes HTTP/SSE avec catalogue synthétique. La suite `stock-assumptions` a produit huit réponses réelles complètes conformes aux quatre scénarios fictifs répétés, sur le modèle Azure existant ; aucun cas saisonnier ajouté sans besoin explicite, garde-fou conditionnel conservé, refus approprié sans correspondance. Pas de précision universelle revendiquée. Le runtime Python local 3.14 avertit de la compatibilité Pydantic-v1 ; aucun nouveau résultat dans l'image Python 3.11 n'est revendiqué pour ce lot.

**Clôture locale :** cinq correctifs et documents persistés, sans publication ni déploiement ; les textes des fiches, Excel, index et mapping sont inchangés. La livraison distante reste à autoriser à partir du diff exact, puis à valider dans l'image et sur l'URL de référence.

### 13 septembre 2026 — catalogue et parcours v461 déployés sur DEV

**État courant :** `avoulia-backend--v461-20260913-r3`, Healthy,100% du trafic, mode Single. Le chatbot accessible depuis https://nricl.github.io/A-Vous-l-IA/ utilise désormais le catalogue v461 et ses parcours régénérés. Le classeur, les audits et le mapping restent privés ; leurs fichiers ne sont pas servis par la racine web.

**Autorisation :** après présentation de la cible et du caractère public des textes, Eneric a confirmé à06:42 « Tout, avec les textes v461 ». Il s'agit du dev existant en France Central, pas de la production Simplon.

**Livraison :** image `sha256:9c356b0643a3313709f434d73505b6c7e98b49fca735ad869983b0e835410c1b`, build ACR `dd2h`. Source parcours rapprochée dans le merge local `a500a22` : intégration sûre et évolutions distantes conservées. Les hashes publiés restent stables ; les pages historiques hors catalogue sont conservées.

**Corrections issues des essais réels :** questions guidées produites par le backend, sans revalidation par le modèle ; prompt de sélection séparé et centré sur le problème concret. Le candidat r2 a été retiré du trafic après une réponse hors sujet intermittente ; r3 a ensuite passé les scénarios répétés avant et après bascule. Aucun seuil de pertinence lexical arbitraire ajouté.

**Confidentialité :** le mapping CSV était téléchargeable dans l'ancienne version. Les exports hérités sont maintenant conservés hors du dossier web et les types de fichiers sources/export sont refusés par le serveur statique. Les contrôles publics retournent404.

**Preuves :** 198 tests backend locaux,8 tests de rapprochement, puis mêmes suites dans l'image Python3.11 (un test nécessitant Node explicitement ignoré dans cette image). Essais HTTP/SSE, cas hôtelier, refus répétés hors sujet, pages et mobile390px réussis. Ces essais ne constituent pas une certification de pertinence sur toutes les formulations possibles.

**Publication clôturée :** correctifs et documentation publiés par `24e145b`, ainsi que la retouche `1 025` → `1 021` et `Secteurs couverts` → `Domaines métier` sur Pages et frontend Azure. Voir la finalisation en tête.

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

### Correctif Q3 déployé — 14 septembre, accord à17:10

`v463-q3-20260914-r2`, Healthy,100% du trafic ; image `407403ae…`, build `dd30`.
123 tests locaux,109 dans l'image,18parcours de qualification sur14domaines
comparés puis rejoués sur le principal. Choix Q1/Q1.5/Q2, sources, base v463,
recommandations finales et parcours inchangés. Le tri évite le biais alphabétique
dominant et reporte les formulations très proches lorsqu'il existe des alternatives.
Le parcours achats fonctionne via le lien GitHub Pages habituel à390px.
Révision de préparation et image conservées pour rollback ; candidate Q3 r1 arrêtée.
Trace hors dépôt et limites dans `HANDOFF.md`. Les jalons ci-dessous sont historiques.

## Historique du correctif local Q3 — 14 septembre, accord à16:50

Les quatre exemples ne sont plus choisis principalement par alphabet : priorité
sectorielle conservée, alternance entre cas et vocabulaire lié aux titres/objectifs.
Texte source intact, doublons de chunks sans poids, aucun cas ajouté hors périmètre.
Introduction et instructions Q3 harmonisées, sans affirmation de fréquence.
106 régressions ciblées réussies ; détails et limites dans `HANDOFF.md`.
Base v463, parcours et recommandations finales inchangés. Aucun commit, push,
build cloud ou déploiement ; la révision en ligne reste celle décrite ci-dessous.

## Objectif V2
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
