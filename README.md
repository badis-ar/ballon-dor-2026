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
