# Ballon d'or 2026, pronostic

Probabilité de victoire des 30 nommés au Ballon d'or 2026, calculée à partir de données publiques.
Chaque valeur utilisée a une source ; une donnée introuvable reste vide.

Page : https://badis-ar.github.io/ballon-dor-2026/

## Organisation

| Dossier | Contenu |
|---|---|
| `data/` | Fichiers téléchargés tels quels (Wikipédia, openfootball, Polymarket, Kalshi) et `provenance.csv` (adresse, date, empreinte de chaque fichier). Les exports FBref vont dans `data/fbref/`. |
| `config/poids.yaml` | Poids des critères et température du modèle. |
| `src/collecte.py` | Téléchargement des fichiers de `data/`. |
| `src/preparation.py` | Lecture des fichiers et production des tableaux sourcés (une ligne par valeur, avec son URL). |
| `src/modele.py` | Calcul des notes et des probabilités. |
| `src/construire.py`, `src/page.py` | Construction de la page. |
| `docs/sources.md` | Sources retenues, conditions d'utilisation, dépôt des fichiers FBref. |

## Mettre à jour

- **Changer un poids** : ouvrir `config/poids.yaml` sur GitHub, cliquer sur le crayon, modifier, puis « Commit changes ». La page se reconstruit en une ou deux minutes (onglet Actions).
- **Ajouter les statistiques FBref** : voir [`docs/sources.md`](docs/sources.md#déposer-les-fichiers-fbref).
- **Retélécharger les données** : onglet Actions, « Collecter les données », « Run workflow ». À éviter après la cérémonie, car les pages et les cotes intègrent alors le résultat.

## Méthode

Quatre critères : Coupe du monde 2026, saison de club 2025-26, Ligue des champions 2025-26 et palmarès au Ballon d'or.
Chacun regroupe plusieurs éléments (parcours, buts, titres...). Un élément qui manque pour un seul joueur est écarté pour tous.
Les notes sont converties en probabilités par une fonction softmax. Le détail est affiché sur la page.

## Licences des données

Wikipédia : CC BY-SA 4.0. openfootball : domaine public. Polymarket et Kalshi : API publiques.
FBref : usage personnel, avec citation de la source.
