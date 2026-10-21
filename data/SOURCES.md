# Sources des données (collecte du 21 octobre 2026)

Toutes les données sont **en cache dans ce dossier** (fichiers CSV). Le modèle ne lit que ces fichiers.

## Comment les données ont été collectées

FBref, Transfermarkt et Kaggle n'étaient pas accessibles depuis l'environnement de collecte
(et Transfermarkt interdit l'aspiration automatique de son site). Les données viennent donc de
**recherches web**, en croisant des articles de presse et des pages de statistiques publiques
(FotMob, The Analyst/Opta, UEFA, Bundesliga.com, ESPN, NBC Sports, Sofascore, AP…).
Aucun site n'a été aspiré : seules quelques valeurs ont été recopiées, en citant la source.

## Fichiers

| Fichier | Contenu | Fiabilité |
|---|---|---|
| `nommes_2026.csv` | Les 30 nommés, stats de championnat 2025-26, Ligue des champions, CDM 2026 | Colonne `fiabilite` sur chaque ligne |
| `historique_top5.csv` | Top 5 de chaque Ballon d'or 2003-2025 (pas d'édition en 2020) | Voir plus bas |
| `podiums_avant_2003.csv` | Podiums 1996-2002 (utilisés seulement pour le critère « prestige ») | Bonne |
| `cotes_2026.csv` | Cotes des bookmakers (Oddschecker) et du marché Kalshi | Bonne (photos prises à des dates précises) |

## Niveaux de fiabilité (`nommes_2026.csv`)

- **confirmé** : au moins deux sources concordantes, ou une source officielle (ex. Bundesliga.com pour Kane).
- **partiel** : une seule source, ou une « photo » des stats prise un peu avant la fin de la saison.
- **estimation** : valeur introuvable, estimée à la main (surtout pour les défenseurs). Le détail est dans la colonne `commentaire`.

## Faits 2025-26 vérifiés par plusieurs sources

- Liste des 30 nommés : annoncée le 8 septembre 2026 (beIN Sports, ESPN, SI, Mykhel, Notjustok).
- Cérémonie : 26 octobre 2026, au London Palladium (Londres).
- CDM 2026 : l'Espagne bat l'Argentine 1-0 a.p. en finale (but de Ferran Torres). Angleterre 3e, France 4e.
  Ballon d'or de la CDM : Rodri ; Ballon d'argent : Messi ; Soulier d'or : Mbappé (10 buts) ; meilleur jeune : Cubarsí.
- Ligue des champions : le PSG bat Arsenal en finale (1-1, 4-3 aux tirs au but). Bayern et Atlético en demi-finales.
  Kvaratskhelia élu joueur de la saison de la LDC.
- Championnats : Arsenal (Angleterre), FC Barcelone (Espagne), Bayern (Allemagne, + Coupe), Inter (Italie),
  PSG (France), Al Nassr (Arabie saoudite). Manchester City : FA Cup + League Cup.
- Soulier d'or européen 2026 : Harry Kane.

## Hypothèses (à connaître)

1. **Saison de club = championnat national seulement** (buts, passes, minutes). Les sources donnaient surtout ce périmètre de façon cohérente.
2. **Messi** : sa saison de club est la saison MLS 2025 (terminée en décembre 2025, dans la période de vote).
3. **Tournoi international** : seule la CDM compte en 2026. La CAN 2025 (Mané, Hakimi) n'est pas prise en compte.
4. **Historique** : on prend la saison qui se termine l'année du vote (ex. 2011-12 pour 2012), même pour les éditions
   « année civile » d'avant 2022. Les tournois comptés : Coupe du monde, Euro et Copa América *quand elle a lieu la même année*
   qu'un Euro (2004, 2016, 2021, 2024). La CDM de décembre 2022 compte pour le Ballon d'or 2023.
5. **Notes de match** : pas de source gratuite et fiable (WhoScored, Sofascore et FotMob interdisent la réutilisation) →
   critère désactivé, son poids est redistribué.

## Ce qui est approximatif

- **Historique 2003-2025** : les classements, les résultats d'équipes (LDC, CDM/Euro) et les grands prix individuels
  sont fiables. Les **buts/passes de championnat sont approximatifs** (à ± quelques unités) et les **minutes sont
  des estimations** (environ ± 300 minutes). Ces valeurs ont été compilées à partir de statistiques publiques connues,
  pas téléchargées ligne par ligne.
- **2026** : 7 joueurs ont des stats largement estimées (Cucurella, Gabriel, Hakimi, Marquinhos, Nuno Mendes, Pacho,
  Upamecano). Pour Olise, les sources se contredisent sur le nombre de passes à la CDM (5 ou 7).

## Ce que je n'ai pas trouvé

- Les minutes exactes de plusieurs joueurs (Kane, Dembélé, Haaland, Hakimi…).
- Les buts/passes en LDC de la plupart des joueurs hors meilleurs buteurs/passeurs.
- Une cote récente pour les joueurs au-delà du top 8 des bookmakers.
- Les notes de match moyennes (voir hypothèse 5).
