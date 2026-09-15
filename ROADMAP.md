# Avoulia V2 — Roadmap produit

**Rôle du document :** feuille de route priorisée des évolutions d'Avoulia V2.
Décisions prises en tant que Product Owner (Eneric) ; ce fichier est versionné dans le
repo pour rester traçable côté Eneric **et** côté Simplon.

**Dernière mise à jour :** 2026-09-15

**12:17 — accès direct après choix livré :** titre du cas sélectionné puis lien
parcours, sans répéter le déplieur précédent. Identité vérifiée par l'URL serveur ;
fallback explicite si correspondance absente/ambiguë. Historique/API inchangés,
pas d'accélération du modèle revendiquée. Source `4fbbd24`, frontend
`v463-handoff-20260915-r1` sain à100%, rollback détails r1 ;51tests frontend,
recette réelle320/390/1280 et Pages/CI réussis. Détails dans `HANDOFF.md`.
Kit/gel restent en pause ; aucune modification backend, base, éditorial ou parcours.

**11:07 — libellé livré :** « Plus de détails » remplace uniquement « Premier essai »
sur les cartes proposées. Source `57f59c6`, frontend `v463-details-20260915-r1`
sain à100%, rollback compact r1 ;46tests frontend et recette réelle Azure/Pages
réussis. Backend/contenus/parcours inchangés, kit toujours en pause. Détails et reçu
dans `HANDOFF.md` ; les jalons ci-dessous restent historiques.

## Correctif compact — 15 septembre, demande10:28 livrée

La présentation blanche et le bandeau de contexte de la consolidation précédente
sont remplacés : cartes bleu nuit, titre et gain potentiel seuls au premier regard ;
les détails restent sous « Premier essai ». Valeurs confirmées sous Domaine/Secteur/
Objectif, sans changer leurs actions de retour. Texte éditorial, API, base, backend,
sélection et parcours inchangés.

Source `e2b3fe2`, frontend Azure `v463-compact-20260915-r1` sain à100%,
build `dd3b`, digest `d8eb2bb8deb2bdbabfac2bef5a40484d98b2a3192d810a179d1d4038d8be38b3`.
Rollback frontend : accessibilité r2 ; backend accessibilité r1 inchangé.
Pages `34948147883` et CI `34948147776` réussies ;46tests frontend, typage/build,
recette réelle candidate et Pages, cas unique simulé, clavier/contrastes et
320/390/1280px vérifiés. Détails dans `HANDOFF.md` et reçu local
`_local-trace/2026-09-15-compact-cards/deployment-receipt.json`.

**Le kit reste en pause depuis10:23.** Aucun packaging repris ni gel actualisé ;
un éventuel instantané précédent demeure historique face à cette UI plus récente.

## Consolidation finale — 15 septembre, livrée

Choix confirmé à06:31, pause à06:50, reprise à08:24 : les modifications en attente
ont été conservées. Avant toute écriture distante, la reprise a vérifié les révisions
et builds : le socle éditorial du14septembre était encore seul à100%.

**ACC-01 consolidé et publié :** backend `v463-accessibility-20260915-r1`,
frontend Azure `v463-accessibility-20260915-r2`, chacun sain à100%, et GitHub Pages
`34938049102` réussi. Source `1efdaa6`, gabarit privé `c67b422`.
Le frontend r1 n'a jamais reçu le trafic principal : la recette réelle a détecté
une collision CSS des vues légales qui annulait le contraste du pied de page ;
la r2 isole ce style, sans modifier ces vues ni le bot.

- Contrastes texte normal ≥4,5:1 : cartes/titres13,76, choix6,85, contexte12,01,
  avertissement7,86, liens de pied de page9,56. Clavier, focus et retour à la première
  ligne de réponse vérifiés ; erreur/attente hors du journal occupé, reprise exacte.
- Accordéons : focus visible non rogné ; copie du prompt annoncée, secours manuel
  préservé. Mise en page testée à320/390/1280px, réduction des animations respectée.
- Critères ciblés : WCAG2.2 1.4.3,1.4.10,2.4.3,2.4.7,2.5.3,4.1.3.
  Pas de certification globale ni d'essai avec un lecteur d'écran réel.
- Preuves :164tests locaux backend/gabarits,152dans l'image,43frontend,
  typage/build ; CI `34938049142` réussie,239tests dont5ignorés.
  Recette réelle Pages→plusieurs cartes→fiche→bon parcours, presse-papiers réel,
  anciens validateurs HTTP et rechargement ordinaire sans cache-buster vérifiés.

Les1 021pages conservent exactement leurs sources/prompts/contenus éditoriaux ;
quatre historiques inchangées. Base, sélection, taxonomie, modèles et quotas inchangés.
Les deux révisions `v463-editorial-20260914-r2` restent le rollback.
Reçu : `_local-trace/2026-09-15-accessibility/deployment-receipt.json`.
**Consolidation terminée** ; adoption métier/taxonomie restent à Eneric,
packaging Simplon non lancé. Les5 105hypothèses ne sont toujours pas des gains mesurés.

## Programme actif — valeur visible et expérience de choix, accord à18:15

**Complément du14septembre : couche éditoriale des1 021cas livrée sur Azure, publication frontend coordonnée avec Pages.**
Le périmètre reste affichage/enrichissement d'expérience, sans modifier le bot,
la base ni la taxonomie. Les1 021cas ont été lus et rédigés individuellement à partir
des descriptions, premières actions et précautions déjà publiques :5 105champs qualitatifs.
Ce sont des hypothèses éditoriales relues contre les sources par IA, pas des validations
humaines ou des résultats d'usage. **Aucun gain mesuré ni délai chiffré avant valeur établi.**
Ce programme complète le cap80/20, sans relancer un moteur parallèle. Objectif :
comprendre tôt l'intérêt d'un cas, choisir une piste et commencer un essai utile.
Backend et frontend Azure `v463-editorial-20260914-r2` reçoivent100% du trafic.
Le socle précédent `v463-value-20260914-r1` / `v463-value-20260914-r2` est conservé pour retour arrière.

**Répartition confirmée à18:10 :** Eneric prend en charge les essais d'usage complets,
les corrections qui en découlent et les cinq réserves de classement métier. Ces
trois chantiers ne sont pas relancés par ce programme. Les tests techniques propres
aux nouveaux lots restent nécessaires. Le packaging et la production Simplon
restent différés ; le présent cadrage n'autorise pas leur lancement.

### Ordre de réalisation et critères de réussite

| Ordre / ID | Lot | Livrable attendu | Critère de réussite / limite | État |
|---|---|---|---|---|
| 1 — VAL-01 | Bénéfice visible dès la découverte | Gain recherché, premier résultat, horizon de première valeur et conditions d'intérêt ; présentation courte dans les propositions, la fiche et l'entrée du parcours | Un utilisateur comprend pourquoi essayer, ce qu'il obtiendra et l'effort à mettre en balance ; aucun chiffre ou délai de rentabilité inventé | Livré :1 021hypothèses par cas, premier livrable et condition d'observation visibles tôt ; gains réels à éprouver |
| 1 — VAL-02 | Promesse suivie dans le parcours | Relier le bénéfice visé aux entrées nécessaires, au résultat de l'étape4, au bilan simple de l'étape5 et à la réutilisation en6 | Distinguer temps gagné/perdu, qualité perçue et intérêt à recommencer ; « non évalué » possible ; pas de score d'adoption déduit des cases cochées | Livré : bilan facultatif non stocké et continuité2/4/5/6 |
| 2 — CHOIX-01 | Comparer les pistes | Cartes compactes avec titre source, gain recherché, résultat et effort disponible ; bouton explicite par cas au lieu des seuls « Cas1/2 » | Jusqu'à cinq pistes restent possibles ; identité cas/détail/lien inchangée ; pas de classement par ROI supposé ni de nouveau tour de dialogue | Livré : gains éditoriaux sourcés séparés des champs catalogue ; choix serveur conservé |
| 3 — ENTREE-01 | Démarrage évident | Afficher immédiatement la première question et les domaines, sans devoir deviner un premier message ; conserver la possibilité de saisir un besoin initial | Domaine toujours confirmé explicitement, aucune classification silencieuse ; démarrage utilisable au clic et au clavier, sans tour vide | Livré :14choix canoniques immédiats |
| 3 — CONTEXTE-01 | Contexte lisible | Résumé des valeurs domaine/secteur/objectif et accès aux corrections déjà disponibles | Comprendre le périmètre choisi et l'effet d'un retour arrière ; aucune incohérence entre libellés, état serveur et choix dépendants | Livré, corrections existantes conservées |
| 4 — REPRISE-01 | Attente et récupération | État d'attente compréhensible, message d'erreur unique, reprise explicite sans ressaisie ni double soumission | Ne pas simuler des étapes de calcul, un pourcentage ou une annulation serveur inexistants ; conserver besoin et choix | Livré, interruption et reprise exacte testées |
| 4 — PASSAGE-01 | Passage vers l'outil d'exécution | Expliquer où utiliser le prompt et la différence entre orientation AVIA et exécution dans l'assistant autorisé choisi | Parcours générique conservé, aucun transfert automatique du besoin ni connexion imposée à un outil | Livré dans les1 021parcours |
| 5 — RETOUR-01 | Refaire un cas | Conservation volontaire du lien et accès court aux éléments utiles lors d'une utilisation suivante | Sans compte obligatoire, stockage de conversation ou partage automatique ; ne pas présenter les cases locales comme une sauvegarde complète | Livré : copie volontaire du lien sans contexte |
| Transversal — CONFIANCE-01 | Promesse cohérente | Revoir « personnalisé », « cas vérifiés », « RGPD », efforts et délais affichés | Distinguer contenu relu, bénéfice potentiel, résultat observé et obligations de l'opérateur ; pas de certification implicite | Vitrine et nouvelles surfaces corrigées ; texte du bot conservé |
| Transversal — ACC-01 | Accessibilité pratique | Clavier, focus, annonces des réponses/erreurs, lisibilité des listes et confort mobile | Contrôles ciblés sur chaque nouvelle surface, sans revendiquer une conformité globale non auditée | Consolidé et déployé le15septembre : contrastes, focus, annonces, mobile ; limites d'audit ci-dessus |

### VAL-01 — cadre de valeur et de « ROI potentiel »

Le bénéfice existe actuellement dans la description et « Ce que ça vous apporte »,
mais sa lisibilité est secondaire face aux étapes/prérequis/précautions. Ne pas
ajouter une promesse marketing identique à tous les cas : exprimer la valeur propre
à la tâche, en langage PME, comme une hypothèse compréhensible et non une mesure.

- **Gain recherché :** temps, qualité/cohérence, réduction des oublis, traçabilité,
  aide à la décision ou autre bénéfice réellement soutenu par le cas.
- **Premier résultat :** livrable tangible obtenu à l'essai, distinct d'un processus
  automatisé ou déployé.
- **Horizon :** distinguer temps de préparation, délai avant un résultat utilisable
  et répétitions nécessaires pour amortir la mise en place. Employer des repères
  conditionnels lorsqu'ils sont justifiables ; ne pas convertir le repère actuel
  uniforme de2h12 en délai de ROI.
- **Conditions et contreparties :** fréquence/volume, données disponibles, outil
  autorisé, effort initial, relecture et corrections. Un usage ponctuel peut rester
  intéressant pour la qualité sans faire gagner de temps.

La conformité n'est jamais acquise par le seul usage d'IA : privilégier réduction
des oublis, cohérence ou traçabilité selon la source. Aucun pourcentage, montant
économisé, durée précise d'amortissement ou garantie non étayés. Un éventuel calcul
ultérieur resterait un scénario fondé sur les hypothèses déclarées par l'usager,
pas un ROI validé ; aucun calculateur financier n'est requis pour ce premier lot.

### Historique — premier prototype à18:23

**Avancement du lot lancé à18:23 :** inventaire des champs servis réalisé dans le code,
sans lecture de classeur. Description, première action, effort, prérequis, guardrails
et mode existent dans le contrat courant ; aucun champ dédié gain/ROI/horizon n'est
transmis. Cela ne prouve pas l'absence de colonnes supplémentaires dans les classeurs.
Choix de prototype : propositions éditoriales séparées des champs source, pas de
déduction au runtime ni de génération de promesses par domaine.

`backend/scripts/value_preview.py` valide un contrat versionné de brouillon avec
identité du cas, hash de page publique et citations exactes ; il rend un atelier
HTML autonome pour liste, fiche et entrée du parcours. Quatre cas publiés couvrent
temps, qualité, traçabilité et aide à la décision. Les extraits et hashes sont
rapprochés des pages publiques ; titres/descriptions/actions restent intacts.
Les hypothèses de valeur ne sont pas des mesures et leur ancrage textuel n'est
pas une validation sémantique. Aucun de ces textes n'est adopté dans la base.

**Ajustement validé à18:43 :** remplacer la galerie par un scénario à la fois :
besoin fictif → cas illustratif associé → fiche → entrée du parcours individuel.
Changer de scénario revient au besoin ; aucune liste mélangeant les quatre cas.
Le prototype ne rejoue pas la qualification ni une recherche RAG et ne limite pas
le vrai bot à une seule proposition. Validation du déroulé local seulement,
pas adoption des textes pour tout le catalogue ou autorisation de publication.

Aperçu local : `http://127.0.0.1:4191/`, fichier `avia-valeur-apercu-2.html` dans
le dossier Microsoft Scout, actualisé au même emplacement. Navigation séquentielle, provenance
consultable et liens vers les parcours actuels. Habillage d'atelier, pas nouvelle
identité AVIA ; aucun appel IA, formulaire de bilan, stockage ou exécution simulée.
14 tests synthétiques et navigation sur4scénarios/4étapes à390/1280px, clair/sombre.
Le raccordement API/frontend/générateur et les1 021cas sont désormais livrés dans
la couche séparée `editorial-value-2` décrite ci-dessus ; cet aperçu initial reste un prototype.

Commencer par l'inventaire des champs déjà disponibles et la définition d'un contrat
de présentation commun à la liste, la fiche et le parcours. Définir la provenance
de chaque information : texte métier source inchangé, information éditoriale dérivée
explicitement distincte, ou hypothèse laissée à l'utilisateur. Une valeur absente
n'autorise pas une invention au runtime ni une déduction du bénéfice depuis le seul
domaine. Réutiliser les champs existants si leur contenu suffit.

Préparer quelques aperçus contrastés (temps, qualité, traçabilité, aide à la décision)
pour arrêter le format, sans confondre ces aperçus avec une couverture des1021cas.
Le contrat vise l'ensemble du catalogue ; si des données nouvelles sont nécessaires,
définir leur schéma, leur validation et leur versionnement avant toute extension.
Ne pas modifier en masse les classeurs ni leur classement au titre d'un changement UI.

### Invariants et sortie vers Simplon

Conserver qualification explicite, filtres métier avant retrieval, sources verbatim,
identités/liens autoritaires, cas et parcours génériques, six étapes dans le même
ordre et arrêt du dialogue après la fiche/bouton. Pas de coach bavard, nouveau
modèle, moteur de sélection parallèle ou refonte visuelle gratuite.

Chaque lot a un aperçu, des contrôles ciblés et un état local/déployé explicite ;
l'accord sur cette roadmap n'est pas un accord de publication. Avant packaging :
surfaces retenues stabilisées, confiance/accessibilité examinées, documentation
et reprise cohérentes, puis décision distincte d'engager la livraison Simplon.
Les critères ci-dessus sont des objectifs de conception, pas des résultats acquis.

### Réalisation après accord de19:09

VAL-02 : première action visible à l'entrée, renvoi aux étapes2/4/5, bilan facultatif
temps total/qualité/suite, sans score ni sauvegarde des réponses. CHOIX-01 : cartes
liées aux identités serveur, titre/description/effort source, sélection dans la même
liste. ENTREE-01 : question et14domaines canoniques fournis par l'accueil, aucun
classement implicite. CONTEXTE-01 : résumé des choix et corrections existantes.
REPRISE-01 : attente honnête, erreur unique, requête conservée et reprise explicite ;
fin de flux sans confirmation traitée comme erreur. PASSAGE-01 : guide AVIA distinct
de l'assistant d'exécution. RETOUR-01 : copie volontaire du lien sans paramètres,
sans conservation de conversation. CONFIANCE-01 : retrait des absolus de vitrine ;
inconnus et contreparties visibles. ACC-01 : contrôles ciblés clavier, focus,
statuts et affichage390/1280px, pas de revendication de conformité globale.

Les1021pages sont enrichies uniquement depuis le HTML déjà public, avec quatre pages
historiques intactes ; prompts et champs métier conservés. Aucun classeur lu,
modifié, versionné ou envoyé. Tests et recette dans `HANDOFF.md`.

## Cap actif — efficacité et pertinence, règle 80/20

**Correctif Q3 livré après accord à17:10 :** règle commune aux14domaines,
diversité des cas et du vocabulaire, report des quasi-doublons observés.
18parcours réels comparés HTTP/SSE avant/après, choix de qualification inchangés ;
123 tests locaux et109 dans l'image. Révision `v463-q3-20260914-r2` à100%.
Base/parcours et sélection finale conservés ; ancienne préparation disponible
pour retour arrière. Les formulations source restent un sujet éditorial distinct,
pas une garantie sémantique du classement lexical. Détail dans `HANDOFF.md`.

**Jalon local précédent après accord à16:50 :** retirer le biais alphabétique dominant
des quatre exemples de problèmes. Diversité de cas et vocabulaire du titre/objectif,
sans nouvelle fréquence supposée, modèle ou taxonomie. Sources verbatim et filtres
inchangés ; les recommandations finales ne sont pas reclassées par ce correctif.
Implémentation locale et régressions dans `HANDOFF.md` ; pas de publication ni de
déploiement à ce jalon. La révision Q3 ci-dessus l'a depuis remplacée en ligne.

**Lot demandé à13:56, confirmé à14:48 et publié : préparation et complémentarité des étapes.**
Revue complète des1 021cas /3 774entrées terminée. Gabarit local : une entrée préparée
avec contenu utilisable, manques et sources/statut ; données existantes non inventées,
choix déclarés séparés, aucune réalisation prématurée du cas.
L'étape4 consomme cette préparation ; les étapes5/6 testent puis réutilisent sans repartir
de zéro. Les3 774blocs sont régénérés et contrôlés ; quatre parcours représentatifs ont
été ouverts localement sur mobile. Le bot et les cellules de la base v463 sont inchangés.
La révision `v463-preparation-20260914-r1` reçoit100% du trafic après contrôle de
la candidate. V463 précédente conservée pour retour arrière ; mêmes données et liens.
Sources `3f7bf8b` / `8989942` publiées, CI `34849464018` réussie. Pas de nouvelle
version Excel pour un changement de gabarit ; le serveur d'aperçu local est arrêté.

**Livraison v463 initiale, désormais référence de retour arrière** :
1 021fiches/parcours actuels et quatre pages historiques conservées. Autorisation
explicite à12:13, candidate exercée avant bascule, retour arrière conservé.
Les notes de préparation privée ci-dessous sont historiques. La publication porte
sur les fiches/parcours, jamais sur le classeur complet, ses audits ou le mapping.

Clôture : sources `830d2b0` / `e61e487`, Pages `34835285869` et CI `34835285888`
réussis ; anciennes préversions backend/frontend désactivées. Le frontend Azure
stable reste inchangé et utilise le backend v463 par son proxy habituel.

**Avancement après accord du 14 septembre à 11:29 : candidate privée v463 prête à relire.**
La revue complète v462 et ses370corrections de contenu sont réutilisées ; quatre
ajustements ciblés supplémentaires clarifient les entrées et les premières actions.
Les1 021IDs, le schéma, la taxonomie, les modes et les6 158formules sont conservés.
Les cinq réserves de classement nécessitant un avis métier restent consignées, sans
reclassement automatique ni blocage artificiel du reste du catalogue.

Quatre aperçus textuels des parcours (fiches produit, chantier, stocks, recrutement)
contiennent les six étapes et le prompt générique courant. Ils sont conservés uniquement
dans le classeur labellisé, pas exportés en HTML/JSON. Ce sont des supports de relecture,
pas une recette interactive des pages déployées. L'accord de publication du contenu
a depuis été donné à12:13 ; la bascule contrôlée vers v463 est réalisée.

**Priorité révisée à 10:59 : fiches et parcours avant optimisation du bot.**
Les consignes du sélecteur existant sont restaurées à l'identique ; seule la coupure
prématurée du pool de candidats reste corrigée. Aucun gain des nouvelles consignes
n'a été démontré par une comparaison avant/après. Arrêt des essais de formulation
et des builds supplémentaires pour ce chantier.

Travail actif : rendre le premier essai clair, les prérequis compréhensibles et le
résultat vérifiable. Le gabarit commun présente désormais une seule introduction courte,
des choix de préparation en langage courant et trois contrôles avant usage :
utile, fiable, utilisable. Les six étapes, leurs textes source et les prompts
génériques sont conservés. Ces gabarits sont appliqués aux1 021pages v463 servies.

**Décision d'Eneric du 14 septembre à 10:21 : conserver le bot existant comme socle.**
Le programme r2 est arrêté, pas livré ni déclaré réparé. Le moteur parallèle `/preview`,
son vérificateur exhaustif, sa réorientation et son transfert de contexte personnalisé
sont retirés du développement actif. Les sources et résultats antérieurs restent
récupérables dans Git et dans la trace locale hors dépôt ; ne pas relancer leurs anciens
commandes, builds ou plans de livraison.

AVIA aide à découvrir une possibilité d'usage puis à faire un premier essai utile.
Il reconnaît **l'action, son objet et le livrable**, sans exiger qu'une cible ou une
motivation figure dans la fiche. « Réécrire mes fiches produit pour la GenZ »,
« pour de nouveaux clients » et « améliorer mes descriptions produit » peuvent mener
au même cas générique. L'usager adapte lui-même le parcours. Cela n'autorise ni
à inventer un canal comme TikTok, ni à ignorer une exclusion explicite.

La qualification reste domaine choisi → secteur applicable → objectif → besoin.
Les filtres, IDs et sources restent autoritaires. Après sélection : fiche courte,
un bouton parcours, fin du dialogue. Même identité visuelle, pas de coach bavard.

**Précision du 14 septembre à 10:56 : jusqu'à cinq cas utiles sont souhaitables.**
La découverte peut offrir plusieurs pistes ; trouver le cas attendu ne doit pas
forcer une réponse unique. Évaluer séparément sa présence, les exclusions réellement
exprimées et l'utilité des autres pistes, plutôt qu'exiger une liste d'IDs exactement
égale à un seul cas. Ni remplissage obligatoire à cinq, ni rejet automatique des alternatives.

Les3 774aides de préparation ont une mission et un livrable nommés. Le premier résultat
du cas est produit à l'étape4, testé en5 puis réutilisé en6. Les champs métier et le bot
ne sont pas modifiés pour ces améliorations de gabarit.

### Livraisons par valeur, sans dépendance à une nouvelle architecture

| Priorité | Livrable | Périmètre et limite |
|---|---|---|
| P1 — bot existant, lot technique limité | Corriger la coupure prématurée, sans changer la sélection | Livré avec v463 : pool complet avant sélection, cinq après rapprochement. Prompt inchangé ; aucun second juge, mot-clé spécial ou personnalisation de fiche. |
| P0 — nettoyage | Retirer l'expérimentation parallèle | Livré : code/flags/routes/recettes retirés, anciennes révisions Azure désactivées. Cinq correctifs UX, banc existant et archives conservés ; aucune migration asynchrone imposée. |
| P0 — contenu complet | Améliorer les 1 021 cas dans les colonnes existantes | V463 adoptée sur le backend après autorisation : première action claire, entrées réalistes, validation humaine. Sources v461/v462 conservées, audits privés, cinq réserves de classement documentées sans reclassement automatique. |
| P0 — parcours génériques | Rendre les six étapes praticables, sans changer leur ordre | Garder données/prérequis, premier livrable, contrôles métier, comparaison et réutilisation. Retirer le contexte injecté depuis le chat. Les prompts restent génériques et complétés par l'usager. |
| P0 — premier essai honnête | Séparer brouillon, analyse et automatisation déployée | Indiquer données, droits et outil nécessaires. Données fictives annoncées comme telles ; ne pas inventer d'historique, de résultat ou de gain. Informations à préparer dans le parcours, pas questionnaire d'admission au cas. |
| P1 — usage fiable | Corriger les frictions observées sur le socle conservé | Choix/boutons cohérents après retour arrière, besoin conservé, erreurs explicites, absence de dialogue après la fiche. Mesurer d'abord la latence de l'appel existant ; ne pas transférer les défauts du moteur expérimental au diagnostic du stable. |
| P2 — suites utiles | Réutilisation volontaire, responsable, formation/accompagnement | Dans les parcours, sans compte imposé ni transmission automatique. Une copie de prompt ou une case cochée ne prouve pas l'adoption. |
| P2 — éventuelle orientation | Aider seulement si la recherche principale reste une impasse | À reconsidérer après le correctif intrafiltre. Piste réelle séparée, autre classement expliqué, accord obligatoire. Aucun développement actif de recherche secondaire dans ce lot. |

Le générique concerne le contexte de l'usager, pas la précision de l'action : une
traduction n'est pas une réécriture, un script vidéo n'est pas une fiche produit.
Une spécialisation réellement indispensable au cas ne devient pas générique par
effacement de son sens. Les documents à réunir et la relecture ne sont pas supposés acquis.

### État et publication

Les cinq correctifs UX restent en ligne, avec le catalogue et les parcours v463.
L'ancien stable `d02ffad` reste la référence de retour arrière. Le code preview est
retiré des sources ; les anciennes révisions expérimentales sont désactivées.
Aucune ancienne image ni aucun mapping privé n'est détruit.
Le périmètre de cette livraison a reçu son aperçu et sa confirmation à12:13.
Il utilise un contexte neuf du bot existant et conserve les images/index/mappings de retour arrière.

La recette compare notamment les trois formulations produit ci-dessus, une exclusion
explicite, un autre livrable demandé, l'absence de cas, le cas au-delà du cinquième candidat
et le détail terminal lié au bon parcours. Les résultats locaux ne sont pas un reçu Azure
ni une garantie de pertinence sur toutes les formulations.

Les repères Bpifrance/France Num/DGE motivent le premier essai faisable, le contrôle du
résultat et la réutilisation ; ils ne prescrivent pas une refonte de moteur ni ne prouvent
la performance d'AVIA. Pas de nouveau modèle, connecteur, télémétrie ou package Simplon.

Les suites restent ciblées : avis métier sur les cinq réserves de classement, retours
sur des usages réels, puis relais humains facultatifs. Les libellés historiques du
chat et de la vitrine peuvent encore employer « personnalisé » au sens de découverte ;
les pages et prompts ne reprennent ni n'adaptent automatiquement le besoin du chat.

## Archive de la roadmap antérieure — ne pas exécuter

Les sections suivantes conservent la chronologie, y compris des hypothèses corrigées.
Le cap 80/20 ci-dessus remplace leurs consignes de développement et de préversion.

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
