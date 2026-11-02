# Ciel - PWA météo sourcée Météo-France

Créée le 2026-11-02. Besoin de Simon : une appli météo **sans pub, jolie, rapide, et dont on ne
doute pas des infos** : heure par heure, 15 jours, risque de gel, lever / coucher du soleil.

## Ce que c'est

Une PWA **une seule page** (`index.html`, ~70 Ko, vanilla JS, zéro build) + `sw.js` +
`manifest.json` + `icons/`. Interface en français, thème clair / sombre (auto, ou forcé en pied de
page). Pensée téléphone d'abord, deux colonnes au-delà de 920 px.

Écran, de haut en bas :
- **En-tête** au dégradé de ciel (change selon le temps, la nuit, l'aube et le crépuscule) : lieu,
  favoris en puces, température actuelle (AROME au quart d'heure, interpolée à la minute),
  ressenti, mini / maxi du jour, une phrase de synthèse (pluie à venir, rafales, gel cette nuit,
  demain plus doux / plus frais), et **la pluie des 2 prochaines heures** au quart d'heure (cachée
  s'il ne pleut pas dans les 24 h).
- **Heure par heure** sur 48 h (SVG) : pictogramme, courbe de température colorée, pluie en mm,
  vent (flèche = sens où il va) et rafales, nuits grisées, séparateurs de jour.
- **15 jours** : mini / maxi en barre colorée, **bande grise = plage des 51 scénarios ECMWF**
  (p10 des mini à p90 des maxi), pluie en mm + **proba de pluie ≥ 1 mm** (part des scénarios),
  **indice de confiance sur 5** (points sous le jour). Un tap ouvre le détail du jour (graphique
  horaire, vent, scénarios, modèle et run). Au-delà de J+4 le détail passe au pas de 3 h puis 6 h,
  parce que l'ECMWF ne sort pas de données horaires à ces échéances (on n'affiche pas une fausse
  précision interpolée).
- **Gel** : 14 nuits, minimale sous abri, niveau (gel fort ≤ −5, gel ≤ 0, gelée blanche possible
  si ≤ 3° par nuit claire et calme, gel possible si ≥ 25 % des scénarios gèlent, risque faible) et
  % de scénarios ECMWF à ≤ 0°. Phrase de tête : prochaine nuit à risque, sinon la plus froide.
- **Soleil et lune** : arc du soleil avec position actuelle, lever / coucher, durée du jour et écart
  avec la veille, midi solaire, aube / crépuscule civils, heure dorée, compte à rebours du solstice,
  phase de lune dessinée, % éclairé, prochaines pleine et nouvelle lunes.
- **En ce moment** : vent, humidité + point de rosée, pression + tendance 3 h, écart avec hier à la
  même heure, UV, qualité de l'air (indice européen), pollens, pluie sur 24 h.
- **Sources et fiabilité** : chaque modèle, sa couverture réelle, l'heure de son run et de sa
  réception ; liens « Comparer sur meteofrance.com » (page de la commune) et « Vigilance <dépt> ».

## D'où viennent les données (le point qui compte)

Tout passe par **Open-Meteo** (gratuit, sans clé, CORS ouvert), qui redistribue les données
ouvertes de Météo-France (Licence Ouverte Etalab) et de l'ECMWF (CC BY 4.0).

| Horizon | Modèle | Id Open-Meteo |
|---|---|---|
| 0 à ~J+2 | AROME 1,5 km (Météo-France), + pluie et température **natives** au quart d'heure | `meteofrance_arome_france_hd` |
| idem, pictogramme et nébulosité | AROME 2,5 km (le HD ne fournit ni `weather_code` ni `cloud_cover`) | `meteofrance_arome_france0025` |
| ~J+2 à ~J+4,5 | ARPEGE Europe 11 km (Météo-France) | `meteofrance_arpege_europe` |
| J+4,5 à J+15 | ECMWF IFS 9 km (Météo-France l'utilise aussi au-delà de 4 jours) | `ecmwf_ifs` |
| confiance, probas | ECMWF ENS 51 membres, agrégats journaliers par membre | `ecmwf_ifs025` (ensemble-api) |
| UV, air, pollens | Copernicus CAMS | air-quality-api |

**Fusion** : pour chaque heure et chaque variable, la première valeur non nulle dans l'ordre
AROME HD > AROME 2,5 > ARPEGE > ECMWF. La source d'une heure = le modèle qui a fourni sa
température. Les heures de run viennent de `https://api.open-meteo.com/data/<modele>/static/meta.json`.

Requêtes par chargement : 1 forecast (4 modèles, ~110 Ko), 1 ensemble (~21 Ko), 1 qualité de
l'air, 4 meta.json. Recherche de commune : **API Adresse** (`api-adresse.data.gouv.fr`,
`type=municipality`) ; commune d'une position GPS : `geo.api.gouv.fr/communes?lat&lon`.
Soleil et lune calculés sur l'appareil (aucun appel).

Ce qui n'est **pas** dans l'app, et pourquoi :
- **Vigilance orange / rouge** : pas dans les données ouvertes sans clé (le portail
  `portail-api.meteofrance.fr` demande un compte + clé). D'où le lien vers la carte officielle du
  département. Piste v2 : un compte portail-api et un petit proxy (la clé ne peut pas vivre dans
  une page publique).
- **L'API privée de l'app Météo-France** (`webservice.meteofrance.com` avec le jeton embarqué dans
  leur app, celle qu'utilise la lib Python `meteofrance-api`) : écartée volontairement, ce n'est
  pas une API publique (et l'appel a été bloqué par le garde-fou de Claude Code).
- **Observations de stations** : idem, portail-api avec clé.
- La prévision officielle de meteofrance.com est retouchée par des prévisionnistes : petits écarts
  possibles avec l'app, c'est écrit dans la carte Sources.

## Lancer / tester

```bash
python -m http.server 8129 --directory PERSO/ciel
```
(entrée `ciel` dans `.claude/launch.json` à la racine du dépôt). Un lieu se partage par l'URL :
`#l=lat,lon&n=Nom&cp=31000&d=Haute-Garonne`. Stockage local : `ciel:place`, `ciel:favs`,
`ciel:theme`, `ciel:data:<lat,lon>` (les 6 derniers lieux, pour le hors ligne).

## Versioning / déploiement

`APP_VERSION` + `APP_BUILT` en tête du script d'`index.html`. Le service worker est enregistré en
`sw.js?v=APP_VERSION` et en dérive son nom de cache (`ciel-v<N>`) : bumper `APP_VERSION` à chaque
livraison. Page en réseau d'abord (les mises à jour arrivent tout de suite), icônes et manifeste en
cache d'abord ; le worker **ne supprime que les caches `ciel-`** (l'origine `kkjsf.github.io` est
partagée avec Harmonic Atlas et Chess Analyst, cf. le bug corrigé en v297 de Chess Analyst).

**v2 (2026-11-02, choix de Simon sur la maquette)** : au téléphone, **barre de navigation en bas**
(variante A : Aujourd'hui, 15 jours, Gel, Soleil, Fiabilité ; un écran par onglet, mini-barre du lieu
en haut des autres écrans, `show(k)` + règles CSS `[data-view]` sous 920 px) ; au bureau, deux colonnes
sans barre. Nouvelles cartes portées du prototype : **Meilleur créneau pour sortir**, **15 jours en
courbe** (bascule Liste / Courbe), **Les modèles sont-ils d'accord ?** **Balayage horizontal sur
l'en-tête** entre les lieux enregistrés (points cliquables sous l'en-tête). **Thème sombre par
défaut** (cycle sombre > clair > auto). **Alerte gel** : bouton dans la carte Gel ; `periodicSync`
(tag `gel`, intervalle mini 6 h, **Chrome Android + app installée seulement**) ; le worker lit le lieu
surveillé dans le cache `ciel-reglages` (pas de localStorage côté worker, et ce cache n'est jamais
purgé), récupère `meteofrance_seamless` sur 3 jours, regarde la nuit qui finit le matin de
(maintenant + 18 h), mêmes seuils que la carte Gel sans la proba ensemble, notifie une seule fois
par nuit et par lieu ; « Tester » envoie la notification quoi qu'il arrive. Logique vérifiée en
exécutant `sw.js` dans la page avec une fausse `showNotification` (Toulouse 3° : rien ; Chamonix 1°
nuit claire : « Gelée blanche possible », une seule fois). Pas testé sur un vrai Android.

**Statut : v1 en ligne depuis le 2026-11-02** sur **https://kkjsf.github.io/ciel/** (GitHub Pages,
branche `main`, racine), dépôt public `git@github.com:kkjsf/ciel.git`, premier commit `782239f`.
Vérifié en ligne : tous les fichiers en 200, worker `sw.js?v=1` actif, cache `ciel-v1` à côté de
ceux de Harmonic Atlas et Chess Analyst (non touchés). Pas encore vérifié en ligne avec des données
réelles : Open-Meteo répondait 503 au moment de la mise en ligne.

Le dépôt est **public** : ne pas y écrire de lieu personnel (l'exemple de slug a été changé pour
L'Isle-Jourdain avant le premier commit). Pas de CLI `gh` sur la machine : le dépôt a été créé et
Pages activé par l'interface web (Chrome connecté au compte kkjsf) ; le push passe par SSH.

Icônes : `icons/icon.svg` est la source ; les PNG (192, 512, maskable 512 avec contenu réduit à
80 %) sont rendus par Chrome headless puis redimensionnés avec PIL.

## Pièges rencontrés

- **v2 = écran noir au téléphone, corrigé en v3 (`276e724`)** : la règle `[data-view] { display: none }`
  visait aussi `<body>`, qui porte l'onglet courant dans `data-view` : toute la page était masquée sous
  920 px. Il faut `body [data-view]`. Le test de la v2 lisait le `display` calculé de chaque section
  (qui reste `block` sous un parent masqué) : vérifier plutôt `elementFromPoint` ou le `display` du body.
  GitHub Pages garde la page 10 min en cache (`max-age=600`) : une correction peut mettre ce temps à arriver.

- **Open-Meteo peut répondre 503 « The service is overloaded »** sur toute l'API principale
  pendant de longues minutes (vu le 2026-11-02 de ~15h10 à au moins 15h45, `api` et `archive` en
  503 ; l'ensemble et la qualité de l'air répondaient ; aucun incident signalé sur leur GitHub,
  donc impossible de dire si c'était général ou propre à notre adresse IP). L'app retente 3 fois (1,5 s puis 3 s), garde l'affichage du cache du lieu
  avec un bandeau « prévisions de 15h09 affichées », et retente toute seule 2 min plus tard.
- **Jamais les données d'un autre lieu** : un lieu sans cache vide l'écran (`clearView`) au lieu
  de laisser les prévisions du lieu précédent sous le nouveau nom (bug trouvé en test, corrigé).
- **Pluie horaire = cumul de l'heure ÉCOULÉE** chez Open-Meteo (valeur à 15h = 14h-15h). L'app
  affiche des créneaux : la colonne « 14h » montre la pluie 14h-15h (`precipitation[i + 1]`), et
  le pictogramme du même créneau. Même logique au quart d'heure.
- **Les formules SunCalc dérivent de ~2 min** sur le coucher (17h46 au lieu de 17h44 à Toulouse le
  2/11). Remplacées par le calculateur NOAA, identique à la seconde à une référence Python et à
  Open-Meteo. Lune : longitude de Meeus avec les principaux termes de perturbation (nouvelle lune
  du 9/11/2026 trouvée à 11 min près).
- **`geo.api.gouv.fr` en recherche par nom bute sur les apostrophes** (une commune en « d'... » ne
  remonte pas si on tape « d » sans apostrophe) : la recherche passe par l'API Adresse, qui accepte aussi « st »
  et les codes postaux. En revanche son `reverse` en `type=municipality` renvoie vide : on garde
  `geo.api.gouv.fr` pour la géolocalisation.
- URL meteofrance.com d'une commune : `/previsions-meteo-france/<slug>/<code postal>`, slug sans
  accents, apostrophe remplacée par un tiret (`l-isle-jourdain/32600`). Même slug pour
  `vigilance.meteofrance.fr/fr/<departement>`.
- L'ECMWF est horaire jusqu'à 90 h, tri-horaire jusqu'à 144 h, puis 6-horaire : Open-Meteo
  interpole, l'app ré-échantillonne le détail du jour en conséquence (`stepFor`).

## Maquette v2 (2026-11-02, NON commitée, non publiée)

Demande de Simon : « une maquette plus sympa des modifs possibles, notamment des accès plus rapides
aux sections avec des menus en bas ». Trois fichiers, hors dépôt :
- `mockup.html` : la page de présentation (s'ouvre via le serveur local, `http://localhost:8129/mockup.html`) :
  les deux variantes côte à côte dans des cadres de téléphone, pour / contre, les trois nouveautés,
  quatre autres idées illustrées (glisser entre les lieux, alerte gel Android, radar, bilan d'eau du
  jardin) et une recommandation.
- `mockup-app.html` : **un vrai prototype**, généré depuis `index.html` par
  `tools/build_mockup_app.py` (remplacements vérifiés, à relancer si l'app change). `?nav=onglets`
  (variante A : un écran par bouton + mini-barre du lieu) ou `?nav=ancres` (variante B : une page,
  la barre saute aux sections et suit la lecture). Nouveautés : **Meilleur créneau pour sortir**
  (course / vélo / balade, chaque heure de jour notée sur pluie, température idéale, vent, rafales,
  meilleure fenêtre notée surtout par sa pire heure, frise de 40 h), **15 jours en courbe** (maxi /
  mini + plages p10-p90 des 51 scénarios + proba de pluie, zone « tendance » après J+10),
  **Les modèles sont-ils d'accord ?** (AROME / ARPEGE / ECMWF superposés sur ~4 jours, écart moyen
  et maximal, pluie par jour et par modèle, désaccords surlignés).
- `mockup-snapshot.json` : les prévisions de Toulouse figées le 2/11/2026 à 15h09 (le prototype
  ne fait aucun appel réseau ; récupérées du cache du navigateur pendant la panne d'Open-Meteo).

Recommandation faite à Simon : variante A au téléphone, deux colonnes sans barre au bureau ; v2 =
barre + créneau + courbe + modèles ; v3 = glisser entre les lieux + alerte gel Android ; radar
seulement si une source d'images gratuite se confirme. **Choix de Simon : A + alerte gel + balayage
entre les lieux, livrés en v2.** `tools/build_mockup_app.py` cible l'`index.html` v1 : relancé sur la
v2, ses remplacements échouent (c'est voulu, la maquette est figée).

Piège de test : avec le panneau navigateur de l'app masqué, `requestAnimationFrame` ne tourne plus,
donc le défilement doux, l'`IntersectionObserver` (suivi de section de la variante B) et parfois les
captures restent figés. Vérifier par le DOM, ou avec le panneau visible.

## Idées pour la suite

- Vérifier en ligne avec des données réelles, puis installer sur le téléphone (Chrome : menu >
  Installer l'application ; iPhone : Partager > Sur l'écran d'accueil).
- Le 2/11 à 15h, le dernier run AROME HD servi par Open-Meteo était encore celui de 7h00 (06 UTC,
  reçu à 12h03) alors qu'AROME tourne toutes les 3 h ; cf. leur issue #2274 sur les retards
  d'AROME HD. La carte Sources le montre ; à surveiller.
- Vigilance officielle via portail-api + proxy (Cloudflare Worker) si Simon crée un compte.
- Carte radar de pluie (tuiles RainViewer ou Météo-France), pluie dans l'heure plus fine.
- Repli si Open-Meteo est en panne longtemps (api.met.no, mais ce n'est plus du Météo-France).
