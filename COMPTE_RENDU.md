# Compte rendu complet : Pronostic Ballon d'or 2026

Rédigé le 26/10/2026. Le modèle a été relancé et les fichiers du dépôt relus juste avant l'écriture : les chiffres ci-dessous sont ceux du code actuel. Le résultat réel de la cérémonie du 26 octobre n'a pas été consulté.

## 1. Liens et état

| Élément | Lien | État |
|---|---|---|
| Dépôt (public) | https://github.com/badis-ar/ballon-dor-2026 | Créé par l'utilisateur. Je n'ai pas pu le créer (les routes GitHub de création m'étaient interdites). |
| Pull request | https://github.com/badis-ar/ballon-dor-2026/pull/1 | **Fusionnée** le 22/10/2026 à 10:08 UTC. |
| Page | https://badis-ar.github.io/ballon-dor-2026/ | Déploiement GitHub Pages **réussi** (statut `success` du 22/10 à 10:08 UTC). |

- **Actions :**
  - L'Action de la pull request (branche `donnees-et-modele`) est réussie.
  - Celle du push sur `main` est réussie, étapes « construire » et « publier » comprises.
  - Trois exécutions planifiées (23, 24 et 25/10) sont réussies.
- **Ce que je n'ai pas pu vérifier :**
  - Le proxy m'interdit d'ouvrir `badis-ar.github.io`. Je n'ai donc jamais vu la page en ligne ; j'ai seulement vu un rendu du même code en local (captures sur ordinateur et téléphone, modes clair et sombre).
  - Je n'ai pas pu lire les journaux de l'Action. J'ignore donc si la vérification Wikipédia a réussi (voir §6).
- **Branches :** `main` contient le commit des données (`41ed14b`), puis la fusion du commit code (`a7e06a3`). Aucun fichier `NOTES.md` n'existe ; seul `README.md` existe.
- **Actions manuelles de l'utilisateur :** créer le dépôt, installer l'application Claude sur le dépôt (sans quoi mes envois étaient refusés en 403), activer Pages (source « GitHub Actions ») et fusionner la pull request. Je n'ai pas pu activer Pages moi-même (403 du proxy).

## 2. Données : sources, trouvé, manquant, estimé

### Méthode réelle de collecte
- **Demandé :** FBref, Transfermarkt, Kaggle, historique des votes.
- **Obtenu :** **aucune de ces sources n'a été utilisée.** FBref, Transfermarkt, Kaggle, Wikipédia et WebFetch étaient bloqués depuis mon environnement.
- **Seul outil disponible :** la recherche web, qui renvoie des extraits d'articles et de pages de stats (FotMob, The Analyst/Opta, UEFA, ESPN, NBC, Sofascore, Bundesliga.com, AP, Fox, Oddschecker…). Aucun site n'a été aspiré.
- **Risque :** ces extraits contiennent des chiffres souvent contradictoires ou pris à des dates différentes (« photos » de milieu de saison).

### Historique 2003-2025 (`data/historique_top5.csv`, 110 lignes, 22 éditions ; pas d'édition en 2020)

- **Vérifié par recherche web :** les 4e et 5e places de 2010, 2011, 2012, 2013 et 2016. Les vainqueurs de chaque année ne viennent pas d'une recherche : je les connaissais, et c'est le seul fait que le fichier historique doit à ma mémoire plutôt qu'à une vérification.
- **Rédigé de mémoire, non vérifié :** tout le reste, soit :
  - les 4e et 5e places hors des années ci-dessus (y compris 2025 : Salah 4e et Raphinha 5e, ordre non vérifié) ;
  - les buts et passes de championnat, les minutes, les titres, les coupes nationales et les prix de saison ;
  - les parcours en Ligue des champions et en tournoi international.
- **Fiabilité :** les buts et passes sont approximatifs (écarts de quelques unités possibles, voire erreurs). Les minutes sont **estimées**, à environ ± 300 près. Je n'ai rien téléchargé ligne par ligne. Le fichier `SOURCES.md` écrit « compilé à partir de statistiques publiques connues », ce qui est vague : en pratique, c'est de mémoire.
- **Biais :** j'ai saisi ces stats en connaissant les vainqueurs. Le test d'historique peut donc être flatté par cette connaissance a posteriori.
- **Choix de périmètre :** saison se terminant l'année du vote. La Copa América n'est comptée que quand elle a lieu la même année qu'un Euro (2004, 2016, 2021, 2024). La CDM 2022 est comptée pour 2023.
- **Podiums 1996-2002** (`podiums_avant_2003.csv`, 21 lignes) : de mémoire, non vérifiés. Ils ne servent que pour le critère « prestige ».

### Les 30 nommés 2026 (`data/nommes_2026.csv`)

- **Liste :** confirmée par plusieurs sources (beIN Sports, ESPN, SI, Mykhel, Notjustok), annoncée le 8 septembre 2026. Cérémonie le 26 octobre 2026 au London Palladium.
- **Faits d'équipe retrouvés :**
  - Coupe du monde 2026 : l'Espagne bat l'Argentine 1-0 après prolongation, but de Ferran Torres. L'Angleterre est 3e. La France est 4e : l'ordre 3e/4e vient d'une seule source et le score du match pour la 3e place est contradictoire entre sources.
  - Prix de la CDM : Ballon d'or Rodri, Ballon d'argent Messi, Soulier d'or Mbappé (10 buts), meilleur jeune Cubarsí, Gant d'or Unai Simón.
  - Ligue des champions : le PSG bat Arsenal en finale (1-1, 4-3 aux tirs au but). Demi-finales : Bayern, Atlético. Kvaratskhelia est élu joueur de la saison.
- **Titres nationaux :** Arsenal (Premier League), Bayern (Bundesliga, plus Coupe d'Allemagne confirmée), PSG, Inter, Al Nassr. Les titres du FC Barcelone et du Bayern reposent sur **une seule source** (Voz). Man City : FA Cup et League Cup.

**Fiabilité par joueur** (colonne `fiabilite`) : 3 « confirmé » (Kane, Mbappé, Cubarsí), 20 « partiel », 7 « estimation ». Les 7 « estimation » sont Cucurella, Gabriel, Hakimi, Marquinhos, Nuno Mendes, Pacho et Upamecano. Pour eux, une grande partie des buts, passes et minutes **sont des valeurs que j'ai estimées moi-même** (aucune stat trouvée pour Pacho et Upamecano).

**Valeurs que j'ai estimées ou complétées sans source**, même chez les joueurs « partiels » :
- les minutes de plusieurs joueurs (Kane, Dembélé, Haaland, Hakimi, Marquinhos…) ;
- les passes de Haaland ;
- la plupart des buts et passes en LDC hors meilleurs buteurs et passeurs ;
- plusieurs totaux de buts et passes à la CDM (Bellingham, Bruno Fernandes, Díaz, Mané, Neves, Rice, Rodri, Vitinha…).

Le détail se trouve dans la colonne `commentaire` du CSV.

**Valeurs en conflit ou douteuses :**
- **Kane :** « confirmé » (36 buts et 5 passes en Bundesliga, 14 buts et 2 passes en LDC, Bundesliga.com), mais ses minutes sont estimées.
- **Mbappé :** « confirmé » alors que ses stats Liga et LDC viennent d'un seul article (Sofascore), ce qui est incohérent avec ma propre règle « deux sources ».
- **Cucurella :** j'ai écrit le club « Chelsea » (de mémoire). Une recherche (beIN) le disait au Real Madrid, et je n'ai **pas tranché** ce conflit. Son parcours LDC dans le CSV est cohérent avec Chelsea, pas avec le Real Madrid.
- **Olise :** passes à la CDM, 7 (Fox) contre 5 (instantané plus ancien).
- **Dembélé :** les stats de Ligue 1 varient de 5 à 10 buts selon la source.
- **Haaland :** le total de 27 buts en championnat vient de NBC, dont les sous-totaux ne se réconcilient pas avec le total.
- **Lautaro :** « meilleur buteur de Serie A » vient d'une page qui ne le dit pas explicitement ; la Coppa Italia 2026 est inconnue (j'ai mis 0).
- **Barcelone en LDC :** l'élimination en quart de finale est **déduite** (Atlético était demi-finaliste), pas lue.
- **Messi :** sa « saison de club » est la MLS 2025 (29 buts et 19 passes, titre MLS), une hypothèse de ma part. Ses stats de CDM sont 8 buts et 4 passes ; un autre extrait évoquait 12 passes en carrière.
- **Hakimi :** 1 but à la CDM (une source).
- **CAN 2025 :** non comptée, par hypothèse.

### Notes de match
**Introuvables** : aucune source gratuite et réutilisable (WhoScored, Sofascore et FotMob l'interdisent). Le critère est donc **désactivé** et son poids redistribué, comme le prévoyait la consigne. Les « notes » du modèle valent 0 pour tous.

### Cotes
`data/cotes_2026.csv` contient 15 lignes, tirées d'extraits de recherche (Oddschecker le 29/09 et le 05/10, Kalshi le 19/10). Seuls les 8 premiers noms ont une cote. Aucune cote récente n'a été trouvée pour Haaland, Bellingham, Vitinha ni les autres.

## 3. Poids : `config/poids.yaml` (copie exacte, jamais modifié par moi depuis le début)

```yaml
# Poids des critères du modèle (en %). Une ligne = un critère.
# Modifiez un chiffre directement sur GitHub (icône crayon), validez :
# la page se régénère toute seule en 1 à 2 minutes.
#
# Règles :
# - Les poids n'ont pas besoin de faire exactement 100 : ils sont remis à l'échelle.
# - Mettre 0 désactive un critère.
# - « notes_match » est ignoré tant qu'il n'existe pas de source gratuite et fiable :
#   son poids est redistribué entre les autres critères.

coupe_du_monde: 35     # Parcours de l'équipe à la CDM 2026, buts + passes, prix individuels
saison_club: 30        # Buts + passes par 90 min, minutes jouées, titres nationaux
ligue_des_champions: 20  # Parcours du club en LDC, buts + passes en LDC
notes_match: 10        # Notes moyennes des matchs (désactivé : pas de source gratuite fiable)
prestige: 5            # Podiums passés au Ballon d'or + grands prix individuels de la saison
```

- **Poids effectifs utilisés par le modèle :** les 10 points des notes de match sont répartis au prorata, ce qui donne CDM 38,9 %, club 33,3 %, LDC 22,2 % et prestige 5,6 %. La CDM reste le critère le plus lourd.
- **Autres poids testés :** une exploration par pas de 5 %, avec la règle « CDM jamais sous son poids de config et toujours le critère le plus lourd », trouve CDM 40 %, club 5 %, LDC 15 %, prestige 40 %. Cette combinaison retrouve 12/15 vainqueurs en rang 1 et 15/15 dans le top 3. **Elle n'est pas appliquée** : elle est affichée sur la page à titre indicatif.
- **Prudence sur cette combinaison :**
  - Un prestige à 40 % reflète probablement le fait que Messi et Ronaldo gagnent plusieurs années de suite : c'est du surapprentissage possible sur 15 années.
  - Cette recherche a été corrigée en cours de route. Sans la règle « CDM la plus lourde », elle sortait club 0 % et prestige 45 %.

## 4. Validation 2010-2025 (poids effectifs ci-dessus, température T = 9,0)

Le modèle reclasse les 5 premiers du vote réel de chaque édition.

| Année | Vrai vainqueur | 1er selon le modèle (proba) | Rang du vainqueur |
|---|---|---|---|
| 2010 | Messi | Sneijder (70 %) | 2 |
| 2011 | Messi | Messi (65 %) | **1** |
| 2012 | Messi | Cristiano Ronaldo (58 %) | 4 |
| 2013 | C. Ronaldo | Ribéry (39 %) | 3 |
| 2014 | C. Ronaldo | Müller (59 %) | 4 |
| 2015 | Messi | Messi (55 %) | **1** |
| 2016 | C. Ronaldo | C. Ronaldo (51 %) | **1** |
| 2017 | C. Ronaldo | C. Ronaldo (59 %) | **1** |
| 2018 | Modrić | Mbappé (35 %) | 3 |
| 2019 | Messi | Messi (62 %) | **1** |
| 2021 | Messi | Messi (86 %) | **1** |
| 2022 | Benzema | Benzema (56 %) | **1** |
| 2023 | Messi | Messi (66 %) | **1** |
| 2024 | Rodri | Bellingham (31 %) | 3 |
| 2025 | Dembélé | Dembélé (48 %) | **1** |

**Résultat :** 9/15 vainqueurs en rang 1, 13/15 dans le top 3. Au hasard parmi 5 candidats, on aurait 3/15 et 9/15.

**Limites de ce test :**
1. T = 9,0 est calibré sur ces mêmes 15 années (test « dans l'échantillon », sans validation séparée).
2. Il n'y a que 5 candidats par année, au lieu de 30 en 2026 : c'est bien plus facile.
3. Les stats historiques ont été saisies de mémoire, avec connaissance des résultats (voir §2).
4. Les barèmes (vainqueur = 1, finaliste = 0,8…) ont été choisis par jugement. Je ne les ai pas ajustés après avoir vu les résultats, seule T est calibrée.

## 5. Prédiction 2026 (les 30 nommés)

| # | Joueur | Proba | Note /100 | Fiabilité des données |
|---|---|---|---|---|
| 1 | Harry Kane | 26,0 % | 70,9 | confirmé |
| 2 | Michael Olise | 14,5 % | 65,6 | partiel |
| 3 | Ousmane Dembélé | 14,1 % | 65,4 | partiel |
| 4 | Lionel Messi | 11,4 % | 63,4 | partiel |
| 5 | Kylian Mbappé | 4,8 % | 55,6 | confirmé |
| 6 | Lamine Yamal | 4,3 % | 54,6 | partiel |
| 7 | Fabián Ruiz | 3,2 % | 52,1 | partiel |
| 8 | Ferran Torres | 2,8 % | 50,7 | partiel |
| 9 | Luis Díaz | 2,1 % | 48,0 | partiel |
| 10 | Erling Haaland | 1,9 % | 47,3 | partiel |
| 11 | Lautaro Martínez | 1,6 % | 45,7 | partiel |
| 12 | Declan Rice | 1,4 % | 44,8 | partiel |
| 13 | Achraf Hakimi | 1,3 % | 44,1 | estimation |
| 14 | Pau Cubarsí | 1,3 % | 43,6 | confirmé |
| 15 | Rodri | 1,0 % | 41,4 | partiel |
| 16 | Vitinha | 0,9 % | 41,1 | partiel |
| 17 | Khvicha Kvaratskhelia | 0,9 % | 40,9 | partiel |
| 18 | Dayot Upamecano | 0,9 % | 40,1 | estimation |
| 19 | William Saliba | 0,8 % | 39,6 | partiel |
| 20 | Jude Bellingham | 0,8 % | 39,4 | partiel |
| 21 | Nuno Mendes | 0,7 % | 37,7 | estimation |
| 22 | João Neves | 0,6 % | 37,2 | partiel |
| 23 | Vinícius Júnior | 0,5 % | 35,3 | partiel |
| 24 | Gabriel Magalhães | 0,5 % | 34,4 | estimation |
| 25 | Marc Cucurella | 0,4 % | 33,9 | estimation |
| 26 | Willian Pacho | 0,4 % | 33,7 | estimation |
| 27 | Marquinhos | 0,4 % | 33,5 | estimation |
| 28 | Julián Quiñones | 0,2 % | 25,5 | partiel |
| 29 | Sadio Mané | 0,2 % | 24,6 | partiel |
| 30 | Bruno Fernandes | 0,1 % | 21,7 | partiel |

Ces probabilités sont arrondies à 0,1 % près, donc leur somme affichée peut s'écarter légèrement de 100 %.

### Comparaison avec les bookmakers
Probabilité implicite = 1 / (1 + cote), **non corrigée de la marge** (les chiffres d'un bookmaker totalisent plus de 100 %).

| Joueur | Modèle | Oddschecker 29/09 | Oddschecker 05/10 | Kalshi 19/10 |
|---|---|---|---|---|
| Kane | 26,0 % | 5/4 → 44,4 % | 6/5 → 45,5 % | 66 % |
| Yamal | 4,3 % | 2/1 → 33,3 % | 10/11 → 52,4 % | 28 % |
| Mbappé | 4,8 % | 14/1 → 6,7 % | 22/1 → 4,3 % | – |
| Messi | 11,4 % | 18/1 → 5,3 % | 25/1 → 3,8 % | – |
| Rodri | 1,0 % | 20/1 → 4,8 % | 40/1 → 2,4 % | – |
| Kvaratskhelia | 0,9 % | 33/1 → 2,9 % | – | – |
| Olise | 14,5 % | 66/1 → 1,5 % | – | – |
| Dembélé | 14,1 % | 125/1 → 0,8 % | – | – |

- **Accord :** Kane favori, même si le modèle lui donne bien moins que le marché.
- **Gros écarts :**
  - Yamal est très sous-estimé par le modèle (4,3 %, contre 28 à 52 % au marché). Il a gagné la CDM mais n'y a marqué qu'un but, et le modèle compte surtout les buts et passes.
  - Olise et Dembélé sont surestimés par rapport aux cotes (14 % contre environ 1 %).
  - Messi est surestimé (11,4 % contre 4 à 5 %).
  - Rodri (15e, 1,0 %) est peu valorisé malgré son Ballon d'or de la CDM, à cause d'une saison de club avec peu de minutes.
- **Faiblesses de la comparaison :** elle repose sur des cotes vieilles de 1 à 4 semaines, issues d'extraits de recherche, et seulement sur 8 joueurs.

## 6. Problèmes, bugs connus, limites, reste à faire

**Problèmes rencontrés pendant le travail :**
- Sites de données bloqués (§2). Je n'ai pas pu créer le dépôt ni activer Pages ; mes premiers envois ont été refusés avant l'installation de l'application Claude.
- Une manipulation de l'historique git a été bloquée par le système de permissions. J'ai pris une voie plus simple ; il n'y a eu aucun dégât.
- Les journaux de l'Action GitHub sont inaccessibles depuis mon environnement.

**Points à vérifier ou bugs probables :**
1. **Vérification Wikipédia :** `fetch_data.py` interroge l'API Wikipédia. Je n'ai jamais vu son résultat (testé hors ligne seulement : il retombe sur « non vérifié »). Le contrôle est très faible : un nom est « retrouvé » si **un seul mot de 4 lettres ou plus** apparaît dans le texte. La section « Données et vérification » de la page en ligne indique le résultat réel.
2. **Date trompeuse :** `build.py` fixe la « date de collecte » à « 21 octobre 2026 ». Comme l'Action tourne chaque matin, la date de mise à jour de la page change tous les jours alors que les données ne sont pas rafraîchies (seule la vérification Wikipédia l'est).
3. **Club de Cucurella** : conflit non résolu (§2). À corriger dans le CSV si besoin.
4. **Surapprentissage possible** de la combinaison de poids « meilleure » (prestige 40 %), affichée sur la page mais non appliquée.
5. Mon test sur l'historique mesure un peu mal : T est calibrée sur ces mêmes données, et il y a 5 candidats par année.

**Limites du modèle (affichées aussi sur la page) :**
- Données imparfaites, avec de nombreuses « photos » de fin de saison.
- Le vote humain n'est pas modélisé (récit, réputation, moments marquants).
- Les défenseurs et milieux défensifs sont désavantagés, car on mesure surtout buts et passes.
- Pas de notes de match.
- CAN 2025 ignorée.
- Peu d'historique pour régler le modèle (15 éditions).
- Barèmes choisis par jugement.
- Les buts et passes en LDC et à la CDM mélangent des chiffres vérifiés et estimés.

**Reste à faire (suggestions) :**
- Comparer le pronostic au résultat réel de la cérémonie (ce soir, 26/10).
- Remplacer les valeurs « estimation » et « partiel » par de vraies stats (FBref ou autre, si accessible hors de ce bac à sable). Vérifier surtout les 4e et 5e places historiques non vérifiées.
- Rafraîchir les cotes.
- Rendre la « date de collecte » dynamique, ou l'afficher plus honnêtement.
- Renforcer la vérification Wikipédia, par exemple en exigeant le nom complet.
- Valider le modèle hors échantillon (par exemple calibrer sur 2010-2018 et tester sur 2019-2025).

## 7. README (copie exacte). NOTES.md n'existe pas.

```markdown
# Pronostic Ballon d'or 2026

Un modèle simple qui calcule les chances de victoire des 30 nommés au Ballon d'or 2026
(cérémonie le 26 octobre 2026).

**Page web : https://badis-ar.github.io/ballon-dor-2026/**

## Changer les poids des critères

1. Ouvrez [`config/poids.yaml`](config/poids.yaml) sur GitHub.
2. Cliquez sur l'icône crayon ✏️ (« Edit this file »).
3. Changez un chiffre, par exemple `coupe_du_monde: 40`.
4. Cliquez sur **Commit changes…** puis **Commit changes**.
5. Attendez que l'Action se termine (onglet **Actions**, pastille verte, 1 à 2 minutes),
   puis rechargez la page web.

Si un chiffre est mal écrit, l'Action devient rouge : cliquez dessus pour lire le message d'erreur en français.

## Comment ça marche

- `data/` : les données en cache (30 nommés, historique 2003-2025, cotes). Sources et estimations : [`data/SOURCES.md`](data/SOURCES.md).
- `src/fetch_data.py` : télécharge la page Wikipédia du Ballon d'or 2026 et vérifie la liste des nommés.
- `src/modele.py` : le calcul (notes par critère → moyenne pondérée → softmax).
- `src/build.py` : lance le modèle et fabrique la page (`site/index.html`).
- `.github/workflows/page.yml` : l'Action qui enchaîne tout et publie sur GitHub Pages.

Vous pouvez aussi corriger une donnée directement dans `data/nommes_2026.csv` (même méthode : crayon, commit, attendre l'Action).
```

**Fichiers du dépôt à connaître :**
- `data/SOURCES.md` : sources, hypothèses et estimations en détail.
- `data/nommes_2026.csv`, `data/historique_top5.csv`, `data/podiums_avant_2003.csv`, `data/cotes_2026.csv`.
- `src/modele.py` (barèmes et calculs), `src/build.py`, `src/page.py`, `src/fetch_data.py`.
- `.github/workflows/page.yml` (se déclenche sur les push vers `main`, les pull requests, chaque jour à 06:17 UTC et à la demande).
- `requirements.txt` (`pyyaml==6.0.2`).
