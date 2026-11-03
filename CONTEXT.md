# Ciel - PWA météo sourcée Météo-France

Créée le 2026-11-02. Besoin de Simon : une appli météo **sans pub, jolie, rapide, et dont on ne
doute pas des infos** : heure par heure, 15 jours, risque de gel, lever / coucher du soleil.

## Ce que c'est

Une PWA **une seule page** (`index.html`, ~120 Ko en v5, vanilla JS, zéro build) + `sw.js` +
`manifest.json` + `icons/` + `normales/` (données précalculées, v5). Interface en français, thème clair / sombre (auto, ou forcé en pied de
page). Pensée téléphone d'abord, deux colonnes au-delà de 920 px.

Écran, de haut en bas (chaque carte a une bulle **« ? »** à côté de son titre qui explique comment la lire, v7) :
- **En-tête** au dégradé de ciel (change selon le temps, la nuit, l'aube et le crépuscule) : lieu,
  favoris en puces, température actuelle (AROME au quart d'heure, interpolée à la minute),
  ressenti, mini / maxi du jour, une phrase de synthèse (pluie à venir, rafales, gel cette nuit,
  demain plus doux / plus frais), et **la pluie des 2 prochaines heures** au quart d'heure (cachée
  s'il ne pleut pas dans les 24 h).
- **Heure par heure** sur 48 h (SVG) : pictogramme, courbe de température colorée, pluie en mm,
  vent (flèche = sens où il va) et rafales, **ressenti, humidité, UV** (v5, pastille colorée le jour),
  nuits grisées, séparateurs de jour ; colonne de libellés fixe à gauche, le graphique défile.
- **15 jours** : mini / maxi en barre colorée, **bande grise = plage des 51 scénarios ECMWF**
  (p10 des mini à p90 des maxi), pluie en mm + **proba de pluie ≥ 1 mm** (part des scénarios),
  **indice de confiance sur 5** (points sous le jour), **écart aux normales** sous chaque mini et
  maxi (v5, coloré chaud / froid). Un tap ouvre le détail du jour (graphique
  horaire, vent, scénarios, modèle et run). Au-delà de J+4 le détail passe au pas de 3 h puis 6 h,
  parce que l'ECMWF ne sort pas de données horaires à ces échéances (on n'affiche pas une fausse
  précision interpolée).
- **Gel** : 14 nuits, minimale sous abri, niveau (gel fort ≤ −5, gel ≤ 0, gelée blanche possible
  si ≤ 3° par nuit claire et calme, gel possible si ≥ 25 % des scénarios gèlent, risque faible) et
  % de scénarios ECMWF à ≤ 0°. Phrase de tête : prochaine nuit à risque, sinon la plus froide.
- **Soleil et lune** : arc du soleil avec position actuelle, lever / coucher, durée du jour et écart
  avec la veille, midi solaire, aube / crépuscule civils, heure dorée, compte à rebours du solstice,
  phase de lune dessinée, % éclairé, prochaines pleine et nouvelle lunes.
- **En ce moment** (illustré en v5 : un picto coloré par tuile) : vent avec boussole, ressenti
  expliqué, humidité en jauge + point de rosée, UV en échelle 11 cases, qualité de l'air en échelle
  6 niveaux, pollens (3 premiers, 4 niveaux), pression + courbe des 24 h, écart avec hier, pluie sur
  24 h en barres, **normales du jour et records du mois** de la station Météo-France.
- **Montagne** (v8, écran Aujourd'hui, seulement pour un sommet / col / refuge choisi dans la recherche
  ou un lieu au-dessus de 800 m) : altitude de la prévision (modifiable), graphique 4 jours de
  l'isotherme 0 °C, de la limite pluie-neige et de l'altitude du lieu, pluie ou neige ici, orages
  possibles ; puis un résumé par jour (mini / maxi ici, iso 0, vent en altitude, neige dès X m, orages).
- **Bilan du mois** (v8, écran 15 jours) : mois en cours jusqu'à hier, ou mois dernier (bascule) :
  pluie et % de la normale, maxi et mini moyens et leur écart, cumul de pluie face à la normale,
  pluie par jour, une case par jour colorée selon l'écart de température, faits du mois.
- **Explorer un jour** (v5, 6e onglet) : un lieu et une date au choix de 1940 à J+14, graphique
  horaire, mini / maxi avec écart aux normales, pluie, rafales, ressenti, humidité, records, source.
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
| normales 1991-2020, records | fiches climatologiques Météo-France (station la plus proche) | `normales/` précalculé |
| Explorer : passé depuis l'automne 2022 | archives des prévisions AROME / ARPEGE / ECMWF | historical-forecast-api |
| Explorer : avant | réanalyse ERA5 (Copernicus / ECMWF), depuis 1940 | archive-api |
| Montagne (v8) : iso 0, vent en altitude, CAPE | niveaux de pression 1000 à 500 hPa d'AROME 2,5 km puis d'ARPEGE (AROME 1,5 km n'en a pas, ECMWF IFS non plus chez Open-Meteo) | forecast, `models=meteofrance_arome_france0025,meteofrance_arpege_europe` |
| Bilan du mois (v8) | archives des prévisions à courte échéance (`best_match`, Météo-France en France) ; repli : `past_days=62` de l'API de prévision | historical-forecast-api, daily |
| sommets, cols, refuges (v8) | index des lieux IGN (BD TOPO), altitude au point par l'altimétrie IGN | `data.geopf.fr/geocodage` (`index=poi`), `data.geopf.fr/altimetrie` |

**Fusion** : pour chaque heure et chaque variable, la première valeur non nulle dans l'ordre
AROME HD > AROME 2,5 > ARPEGE > ECMWF. La source d'une heure = le modèle qui a fourni sa
température. Les heures de run viennent de `https://api.open-meteo.com/data/<modele>/static/meta.json`.

Requêtes par chargement : 1 forecast (4 modèles, ~110 Ko), 1 ensemble (~21 Ko), 1 qualité de
l'air, 4 meta.json. Recherche de commune : **API Adresse** (`api-adresse.data.gouv.fr`,
`type=municipality`) ; commune d'une position GPS : `geo.api.gouv.fr/communes?lat&lon`.
Soleil et lune calculés sur l'appareil (aucun appel).

**Normales (v5)** : Météo-France publie ses **fiches climatologiques** en données ouvertes
(meteo.data.gouv.fr, jeu « Fiches climatologiques », un `.data` texte par station : normales
1991-2020 de Tx / Tn / pluie par mois, records avec leur date). Leur S3 n'envoie **pas de CORS** :
`tools/build_normales.py <dossier de téléchargement> .` les télécharge (1 574 stations, ~9 Mo) et
écrit `normales/index.json` (indicatif, lat, lon, altitude, période complète ou non) et
`normales/<2 premiers chiffres>.json` (96 fichiers, 1,3 Mo en tout). Relancer de temps en temps pour
les records (fiche éditée le 15/10/2026 au premier passage). Dans l'app : station = minimum de
(distance + 1 km par 15 m d'écart d'altitude + 10 km si la normale ne couvre pas 1991-2020),
60 km maximum ; altitude du lieu = `elevation` renvoyée par Open-Meteo ; au-delà de 100 m d'écart,
correction de 0,65° par 100 m (écrite dans la carte Sources). Normale d'un jour : série de Fourier à
3 harmoniques ajustée aux 12 moyennes mensuelles, chaque harmonique corrigée de l'effet de moyenne
mensuelle (Toulouse le 2/11 : 8,2° / 16,2°). Résultat gardé par lieu (`ciel:norm:<lat,lon>`).
Écart affiché = valeur prévue - normale, arrondi ; pastille de l'en-tête = moyenne des écarts mini
et maxi du jour.

**Explorer (v5)** : aujourd'hui et après, `api.open-meteo.com` avec `start_date` (mêmes modèles et
même fusion que l'app) ; avant, `historical-forecast-api` avec les mêmes modèles si la date est après
le 2022-10-01 et qu'elle renvoie au moins 30 h de température (AROME HD et ARPEGE y sont depuis
octobre / novembre 2022, AROME 2,5 depuis 2024), sinon `archive-api` (ERA5, sans
`precipitation_probability`, qui ferait échouer la requête). On demande J et J+1 pour la pluie de
23h-0h. Défaut : le même jour il y a un an, au lieu affiché (qui suit le lieu principal tant qu'on
n'en choisit pas un autre).

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
(entrée `ciel` dans `.claude/launch.json` à la racine du dépôt, ou `ciel-b` sur le port 8131 si une
autre session tient déjà le 8129). Un lieu se partage par l'URL :
`#l=lat,lon&n=Nom&cp=31000&d=Haute-Garonne`. Stockage local : `ciel:place`, `ciel:favs`,
`ciel:theme`, `ciel:data:<lat,lon>` (les 6 derniers lieux, pour le hors ligne), `ciel:norm:<lat,lon>`
(station et normales retenues pour un lieu, v5).

## Versioning / déploiement

`APP_VERSION` + `APP_BUILT` en tête du script d'`index.html`. Le service worker est enregistré en
`sw.js?v=APP_VERSION` et en dérive son nom de cache (`ciel-v<N>`) : bumper `APP_VERSION` à chaque
livraison. Page en réseau d'abord (les mises à jour arrivent tout de suite), icônes et manifeste en
cache d'abord ; le worker **ne supprime que les caches `ciel-`** (l'origine `kkjsf.github.io` est
partagée avec Harmonic Atlas et Chess Analyst, cf. le bug corrigé en v297 de Chess Analyst).

**v2 (2026-11-02, choix de Simon sur la maquette)** : au téléphone, **barre de navigation en bas**
(variante A : Aujourd'hui, 15 jours, Gel, Soleil, Fiabilité ; un écran par onglet, mini-barre du lieu
en haut des autres écrans, `show(k)` + règles CSS `[data-view]` sous 920 px) ; au bureau, deux colonnes
sans barre. Nouvelles cartes portées du prototype : **Meilleur créneau pour sortir** (retiré en v7), **15 jours en
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

**v3 (2026-11-02, `276e724`)** : corrige l'écran noir de la v2 au téléphone (cf. Pièges).

**v4 (2026-11-02, `9fe81c8`, en ligne)** : `"id": "/ciel/app"` explicite dans le manifeste (avant :
pas d'`id`, donc id = `start_url` = `https://kkjsf.github.io/ciel/`), pour tenter de débloquer la
réinstallation sur Android. **Sans effet** : le blocage vient d'un bug de Chrome 154 à 156 qu'aucun
manifeste ne contourne (cf. Pièges). **Ne plus changer cet id** : pour
Chrome c'est l'identité de l'app, un autre id ferait une autre app (doublon, alerte gel à refaire).

**v5 (2026-11-02, `ff37d5f`, en ligne)** : demande de Simon après la v4. Écart aux
normales Météo-France (liste 15 jours, courbe en pointillés, pastille de l'en-tête, détail du jour,
tuile), ressenti / humidité / UV heure par heure et dans le détail du jour, carte « En ce moment »
illustrée, onglet **Explorer** (6 onglets : libellés en 10,5 px, pastille d'icône plus étroite), carte
Sources avec la station et un lien vers sa fiche PDF. Testée en local (téléphone sombre, bureau
clair 1280 px), aucune erreur console.

**Icône (v5)** : quatre idées présentées dans `icon-proposals.html` (non commité) ; **choix de Simon :
A « 51 scénarios »**, un soleil dont les 51 rayons ont des longueurs différentes, comme le désaccord
des scénarios ECMWF (l'indice de confiance en symbole). Écartées : B « Horizon », C « ciel » écrit,
D « Jour et nuit ».

**v6 (2026-11-02, `70ec25d`, en ligne)** : retour de Simon, au téléphone les libellés « pluie / vent / ressenti /
humidité » de l'heure par heure débordaient sur le graphique et rendaient mal. La colonne fixe de
gauche affiche désormais les **pictos des tuiles** (parapluie, vent, thermomètre, goutte, soleil, en
couleur) au lieu de mots, et les trois lignes du bas sont plus espacées (ressenti, humidité, UV).
Vérifié en 375 px, y compris avec le texte du graphique agrandi de 30 %.

**v7 (2026-11-03, `f18bf62`, en ligne, vérifiée avec données réelles)** : demande de Simon, alléger l'interface. Le module **« Meilleur créneau
pour sortir » est retiré** (jugé pas utile : carte, CSS `.acts` / `.slot-*` / `.tl-*`, `ACTIVITIES`,
`hourScore`, `renderSlot`). Les **notes et légendes sous les cartes** (« lignes du bas, de haut en bas »,
lecture des 15 jours, légende et note du gel, note des modèles, première note des sources) passent dans
une **bulle « ? »** placée à côté du titre de chaque carte, y compris En ce moment, Soleil et Explorer
qui n'en avaient pas. Une seule bulle partagée (`#helpPop`), textes dans l'objet `HELP`, bouton injecté
dans le `.h2-t` de chaque `section[data-help]` ; positionnée en absolu à sa place naturelle sous le titre
(par-dessus la carte, sans décaler la page), fermée par un clic ailleurs, Échap ou un changement
d'onglet (`show()` appelle `closeHelp()`, d'où ce code placé avant `show('today')`). La mention des
licences reste visible sous les sources (attribution CC BY). La place gagnée sert à **grossir les
chiffres** : heure par heure température 13,5 -> 16 px, pluie, vent, ressenti 11-11,5 -> 13-13,5 px,
humidité 12,5, UV 11,5 (lignes redescendues : courbe 92-122, pluie au pied 170, vent 213 / 236 / 251,
ressenti 278, humidité 301, UV 310-326, `dy` 50 sans pluie) ; 15 jours mini / maxi en 17 px (colonnes
38 px, pluie 50 px, cumul arrondi au mm dès 10 mm pour tenir sur une ligne) ; nuits de gel 18 px ;
tuiles 23 px ; en-tête 72 px ; textes des courbes 10 -> 11,5 px. Vérifié en 375 px sombre et
1280 px clair, aucune erreur console, **aucun chevauchement** de texte mesuré par `getBBox` sur les
16 graphiques horaires (48 h + les 15 détails de jour).

**v8 (2026-11-03)** : demande de Simon après la v7 (« la 2 et la 4 » de la liste d'idées, plus un
manuel). Trois ajouts :
- **Mode montagne.** La recherche de lieu interroge aussi l'**index des lieux de l'IGN** (CORS ouvert,
  sans clé) : catégorie « élément topographique ou forestier » (sommets, pics, cols, crêtes...) et
  catégorie « refuge » ; altitude de chaque résultat par l'**altimétrie IGN** en un seul appel
  (plusieurs points séparés par `|`). Un lieu porte alors `alt` (et `kind`, `town` une fois la commune
  trouvée par `geo.api.gouv.fr`, en tâche de fond après le chargement) ; `alt` entre dans `placeId`
  (`lat,lon@alt`) et dans l'URL (`a=`, `k=`, `t=`). Les requêtes forecast et ensemble ajoutent
  `&elevation=<alt>` : Open-Meteo recalcule la température à cette altitude, donc toute l'app (en-tête,
  heure par heure, gel, normales avec la station choisie à altitude proche) passe au sommet. Carte
  **Montagne** si `alt` est fixée ou si l'altitude du modèle de terrain dépasse 800 m
  (`MOUNTAIN_FROM`), avec une requête de plus : 12 niveaux de pression (température, géopotentiel,
  vent) + CAPE, ~40 Ko. **Iso 0** = interpolation au-dessus du dernier niveau encore positif ;
  **limite pluie-neige** = iso 0 - 300 m (règle des prévisionnistes, `SNOW_GAP`) ; **vent en
  altitude** = niveau dont le géopotentiel est le plus proche de l'altitude ; **orage** = code météo
  95-99, ou CAPE >= 1000 J/kg avec au moins 0,2 mm, ou CAPE >= 2000. Altitude modifiable dans la carte
  (`altUser`).
- **Bilan du mois** : requête quotidienne séparée, faite après l'affichage et gardée dans le cache du
  lieu pour la journée (`data.month.day`) ; carte cachée tant qu'elle n'a pas répondu. Normale de pluie
  = normale mensuelle de la station au prorata des jours écoulés ; normales de température jour par
  jour (série de Fourier). En montagne la station est souvent plus basse : la carte le dit (« comparaison
  indicative »).
- **Guide d'utilisation** : boîte de dialogue plein écran (bouton livre en haut à droite de l'en-tête,
  bouton « Guide » en pied de page, lien « Tout le guide » au bas de chaque bulle « ? »). Il est
  **construit à partir des textes `HELP` des bulles** (objet `GUIDE` : 11 sections, intro + parties qui
  reprennent `HELP[clé]`), donc une bulle mise à jour met le guide à jour. Sommaire en puces,
  saut direct à la section de la bulle d'où l'on vient.

Vérifié en local : Pic du Midi d'Ossau (2 847 m), refuge des Sarradets (2 577 m), Font-Romeu (1 842 m,
puis altitude changée à 2 500 m), Toulouse (pas de carte Montagne, octobre : 37,7 mm, 69 % de la
normale), téléphone sombre et bureau clair, aucun chevauchement de texte dans les deux nouveaux
graphiques (`getBBox`).

**Statut : v8 en ligne** (v1 publiée le 2026-11-02) sur **https://kkjsf.github.io/ciel/** (GitHub Pages,
branche `main`, racine), dépôt public `git@github.com:kkjsf/ciel.git`, premier commit `782239f`.
Vérifié en ligne : tous les fichiers en 200, worker `sw.js?v=1` actif, cache `ciel-v1` à côté de
ceux de Harmonic Atlas et Chess Analyst (non touchés). Pas encore vérifié en ligne avec des données
réelles : Open-Meteo répondait 503 au moment de la mise en ligne.

Le dépôt est **public** : ne pas y écrire de lieu personnel (l'exemple de slug a été changé pour
L'Isle-Jourdain avant le premier commit). Pas de CLI `gh` sur la machine : le dépôt a été créé et
Pages activé par l'interface web (Chrome connecté au compte kkjsf) ; le push passe par SSH.

Icônes : `python tools/build_icons.py` (depuis `ciel/`) calcule les 51 rayons, écrit `icons/icon.svg`
(source et favicon) et rend les PNG 192, 512 et maskable 512 (fond bord à bord, dessin réduit à
80 % pour la zone sure d'Android) avec Chrome headless en 1024 px, réduits par PIL (lancer `python`
sans `-I` : PIL est dans le site-packages de l'utilisateur).

## Pièges rencontrés

- **Recherche IGN stricte sur les mots** : « refuge brèche » ne trouve rien alors que « brèche de
  roland » trouve le refuge. Comme la catégorie `refuge` est déjà filtrée, le mot « refuge » est retiré
  de la requête de cette catégorie. Le « Canigou » seul ne remonte le pic qu'avec le filtre de
  catégorie (sans filtre, 40 lotissements et résidences passent devant).
- **Altitude IGN au point du nom, pas au sommet** : Pic du Midi d'Ossau 2 847 m au lieu de 2 884 m,
  Canigou 2 761 m au lieu de 2 784 m (le point du toponyme est à côté du sommet ; chercher le maximum
  autour ne change rien). La BD TOPO n'a pas de Z sur ses détails orographiques. D'où l'altitude
  modifiable dans la carte.
- **`historical-forecast-api` en 503** pendant les tests du 2026-11-03 (et `meteofrance_seamless` qui
  y dépasse le délai) : le bilan du mois se replie sur `past_days=62` de l'API de prévision.
- **Encore `display` contre `hidden`** : `.mt-form { display: flex }` affichait le formulaire caché ;
  il faut `.mt-form[hidden] { display: none }`, et `.card[hidden] { display: none !important }` pour
  les cartes, que les règles `[data-view]` du téléphone remettent en `block`.
- **Python dans un heredoc du Bash de Claude Code** : `\b` y est arrivé en octet 0x08 dans une regex
  JS (le piège déjà noté dans Chess Analyst). Vérifier `grep -c $'\x08' index.html` après un patch.
- **Vérifier les chevauchements par le calcul** : après un changement de taille de police dans un
  SVG, comparer deux à deux les `getBBox()` des `<text>` de chaque graphique (les détails de jour
  ouverts compris). En v7 ça a trouvé 1 à 2 px de recouvrement vent / rafales et pluie / proba,
  invisibles sur une capture.
- **Pas de texte dans une colonne SVG de largeur fixe** : au téléphone, les mots débordent ou se
  chevauchent dès que la police est plus large ou agrandie (v5 -> v6). Des pictos de taille fixe ne
  bougent pas.

- **Fiches climatologiques Météo-France sans CORS** (`meteofrance.s3.sbg.io.cloud.ovh.net`, 403 au
  preflight) : impossible de les lire depuis la page, d'où le précalcul dans `normales/`. Certaines
  stations n'ont des normales que sur une partie de la période (ex. 1991-2010) : le bloc le dit sur
  sa propre ligne « Statistiques établies sur la période ... », le script la lit bloc par bloc.
- **Port 8129 déjà pris par une autre session** : la prévisualisation de Claude Code ne peut pas
  partager un serveur d'une autre conversation. Entrée `ciel-b` (port 8131, `autoPort: false`) dans
  `.claude/launch.json` ; l'entrée `ciel` code le port 8129 en dur dans ses arguments, donc un port
  réattribué automatiquement ne répond pas.

- **Android : réinstallation refusée (2026-11-02). Cause très probable : bug de Chrome 154 à 156,
  corrigé en 157.** Après désinstallation, Chrome Android répond « Déjà installé » puis « Application
  introuvable » ; l'app n'est plus ni dans la liste des applis ni dans `chrome://webapks` (aucune
  WebAPK fantôme). Redémarrage et nouvel `id` de manifeste (v4) sans effet.
  Cause : régression de Chrome Android 154 (commit `bee74a32d432`, bug Chromium 568841400) : la
  feuille d'installation regarde si **une web app quelconque de la même origine** est installée,
  sans tenir compte de l'`id` ni de la portée. Or `kkjsf.github.io` porte aussi Harmonic Atlas et
  Chess Analyst : si l'une des deux est installée sur le téléphone, Ciel est déclarée « déjà
  installée » et « Ouvrir » ne trouve rien. Mêmes messages chez un autre développeur avec trois apps
  sur `joeuk89.github.io` (github.com/joeuk89/london-lions/issues/19, source de ces détails ; le bug
  Chromium n'est pas lisible sans compte). Corrigé dans **Chrome 157** (`157.0.8103.13`, stable
  annoncé pour le 2026-11-03), pas reporté en 155 ni 156. **Rien dans le manifeste ne contourne ce
  bug** : l'id de la v4 était inutile (inoffensif), changer de dossier (`/ciel-meteo/`) aussi.
  Contournements :
  1. Mettre Chrome à jour en **157** (Play Store ; version dans Paramètres > À propos de Chrome).
  2. Ou installer depuis **Chrome Beta**, déjà au-delà de la 157 (l'app s'ouvre alors dans Beta).
  3. Ou désinstaller un moment les autres apps de `kkjsf.github.io`, installer Ciel, puis attendre
     la 157 pour les réinstaller (elles seraient bloquées à leur tour).
  4. À long terme, une origine par app (sous-domaine perso par dépôt) éviterait ce piège et le
     partage du stockage entre les trois apps.
  **Ne pas effacer les données du site `kkjsf.github.io`** pour ce bug : ça n'y change rien et ça
  efface aussi Harmonic Atlas et Chess Analyst (qui n'a aucun export).
  Constaté le 2026-11-02 : téléphone en Chrome 156, la 157 pas encore proposée par le Play Store
  (déploiement progressif sur plusieurs jours). À confirmer : quelle app de `kkjsf.github.io` y est
  installée.
  Non expliqué : la première installation de Ciel, le même jour, a réussi.

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

- Réinstaller sur le téléphone une fois Chrome en 157 (cf. Pièges), puis tester l'alerte gel sur un
  vrai Android.
- Le 2/11 à 15h, le dernier run AROME HD servi par Open-Meteo était encore celui de 7h00 (06 UTC,
  reçu à 12h03) alors qu'AROME tourne toutes les 3 h ; cf. leur issue #2274 sur les retards
  d'AROME HD. La carte Sources le montre ; à surveiller.
- Vigilance officielle via portail-api + proxy (Cloudflare Worker) si Simon crée un compte.
- Carte radar de pluie (tuiles RainViewer ou Météo-France), pluie dans l'heure plus fine.
- Repli si Open-Meteo est en panne longtemps (api.met.no, mais ce n'est plus du Météo-France).
