# Sources

Règle : chaque valeur a une source avec son adresse. Sans source, la valeur reste vide ; rien n'est estimé.

## Sources retenues

| Donnée | Source | Conditions | Récupération |
|---|---|---|---|
| Liste des 30 nommés, nation, poste, club | [Wikipédia, 2026 Ballon d'Or](https://en.wikipedia.org/wiki/2026_Ballon_d%27Or) | CC BY-SA 4.0 | automatique |
| Classements 1996-2025 (top 5, points) | Wikipédia, une page par édition | CC BY-SA 4.0 | automatique |
| Coupe du monde 2026 : parcours, buteurs | [openfootball/worldcup.json](https://github.com/openfootball/worldcup.json) | domaine public | automatique |
| Coupe du monde 2026 : prix individuels | [Wikipédia, 2026 FIFA World Cup](https://en.wikipedia.org/wiki/2026_FIFA_World_Cup) | CC BY-SA 4.0 | automatique |
| Ligue des champions 2025-26 : parcours des clubs | [openfootball/champions-league](https://github.com/openfootball/champions-league) | domaine public | automatique |
| Champions et vainqueurs de coupe nationale | Wikipédia, pages de saison (infobox « winners ») | CC BY-SA 4.0 | automatique |
| Cotes | [Polymarket](https://polymarket.com/event/ballon-dor-winner-2026), [Kalshi](https://kalshi.com/markets/kxballondor) | API publiques | automatique |
| Buts, passes décisives, minutes (championnat, LDC, Coupe du monde) | [FBref](https://fbref.com) | usage personnel, citer FBref | **manuelle** |
| Notes de match | aucune source réutilisable | | non utilisé |

Sites testés et écartés : Transfermarkt, Sofascore, FotMob, WhoScored, Oddschecker (accès bloqué ou réutilisation interdite),
Understat (refuse les robots), Kaggle (jeux de données d'origine inconnue).

## Déposer les fichiers FBref

FBref bloque les téléchargements automatiques. Il faut copier cinq tableaux à la main, depuis le navigateur.

1. Ouvrir le lien FBref du tableau (liste ci-dessous). Si une page « Just a moment… » s'affiche, attendre quelques secondes.
2. Descendre jusqu'au tableau **Player Standard Stats**.
3. Au-dessus du tableau, survoler **Share & Export**, puis cliquer sur **Get table as CSV (for Excel)**.
4. Sélectionner tout le texte affiché et le copier (Ctrl + C).
5. Sur GitHub, dans le dépôt, cliquer sur **Add file**, puis **Create new file**.
6. Nom du fichier : le chemin indiqué ci-dessous, par exemple `data/fbref/fbref_ligues_2025-26.csv`.
7. Coller le texte (Ctrl + V), puis **Commit changes…** et **Commit changes**.

| Tableau | Lien | Fichier |
|---|---|---|
| 5 grands championnats 2025-26 | https://fbref.com/en/comps/Big5/2025-2026/stats/players/2025-2026-Big-5-European-Leagues-Stats | `data/fbref/fbref_ligues_2025-26.csv` |
| Ligue des champions 2025-26 | https://fbref.com/en/comps/8/2025-2026/stats/2025-2026-Champions-League-Stats | `data/fbref/fbref_ldc_2025-26.csv` |
| Coupe du monde 2026 | https://fbref.com/en/comps/1/stats/World-Cup-Stats | `data/fbref/fbref_cdm_2026.csv` |
| MLS 2025 (Messi) | https://fbref.com/en/comps/22/2025/stats/2025-Major-League-Soccer-Stats | `data/fbref/fbref_mls_2025.csv` |
| Saudi Pro League 2025-26 (Mané, Quiñones) | https://fbref.com/en/comps/70/2025-2026/stats/2025-2026-Saudi-Pro-League-Stats | `data/fbref/fbref_saudi_2025-26.csv` |

Après chaque dépôt, la page se reconstruit. Les joueurs introuvables dans un fichier sont listés dans
`donnees/controles.json` sur la page publiée ; leurs cases restent vides.
