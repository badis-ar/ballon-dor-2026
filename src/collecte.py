"""Télécharge les données brutes dans data/ et note leur provenance.

Lancé par l'Action « Collecter les données » (onglet Actions, bouton « Run workflow »).
Chaque fichier téléchargé est enregistré tel quel, et une ligne est ajoutée dans
data/provenance.csv : fichier, URL, date de téléchargement, empreinte SHA-256.

Les fichiers FBref ne sont pas téléchargés ici (le site bloque les robots) :
ils sont déposés à la main dans data/fbref/ (voir docs/sources.md).
"""

import csv
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER = RACINE / "data"
PROVENANCE = DOSSIER / "provenance.csv"
USER_AGENT = "ballon-dor-2026/2.0 (projet personnel ; https://github.com/badis-ar/ballon-dor-2026)"

OPENFOOTBALL = "https://raw.githubusercontent.com/openfootball"

# Pages Wikipédia (anglais) : nom du fichier local -> titre de la page.
PAGES_WIKIPEDIA = {
    "ballon_dor_2026": "2026 Ballon d'Or",
    "cdm_2026": "2026 FIFA World Cup",
    # Championnats et coupes nationales des clubs des nommés
    "angleterre_2025-26": "2025–26 Premier League",
    "espagne_2025-26": "2025–26 La Liga",
    "allemagne_2025-26": "2025–26 Bundesliga",
    "italie_2025-26": "2025–26 Serie A",
    "france_2025-26": "2025–26 Ligue 1",
    "arabie_2025-26": "2025–26 Saudi Pro League",
    "mls_2025": "2025 Major League Soccer season",
    "coupe_angleterre_2025-26": "2025–26 FA Cup",
    "coupe_espagne_2025-26": "2025–26 Copa del Rey",
    "coupe_allemagne_2025-26": "2025–26 DFB-Pokal",
    "coupe_italie_2025-26": "2025–26 Coppa Italia",
    "coupe_france_2025-26": "2025–26 Coupe de France",
    "coupe_arabie_2025-26": "2025–26 King's Cup (Saudi Arabia)",
    "coupe_usa_2025": "2025 U.S. Open Cup",
}
# Une page par édition passée du Ballon d'or (pas d'édition en 2020).
for annee in range(1996, 2026):
    if annee != 2020:
        PAGES_WIKIPEDIA[f"ballon_dor_{annee}"] = f"{annee} Ballon d'Or"

# Saisons des clubs des nommés (buteurs et passeurs par compétition, coupes et supercoupes comprises).
SAISONS_CLUBS = {
    "saison_real_madrid_2025-26": "2025–26 Real Madrid CF season",
    "saison_barcelone_2025-26": "2025–26 FC Barcelona season",
    "saison_chelsea_2025-26": "2025–26 Chelsea F.C. season",
    "saison_psg_2025-26": "2025–26 Paris Saint-Germain FC season",
    "saison_bayern_2025-26": "2025–26 FC Bayern Munich season",
    "saison_manchester_united_2025-26": "2025–26 Manchester United F.C. season",
    "saison_arsenal_2025-26": "2025–26 Arsenal F.C. season",
    "saison_manchester_city_2025-26": "2025–26 Manchester City F.C. season",
    "saison_inter_2025-26": "2025–26 Inter Milan season",
    "saison_al_nassr_2025-26": "2025–26 Al-Nassr FC season",
    "saison_al_qadsiah_2025-26": "2025–26 Al-Qadsiah FC season",
    "saison_inter_miami_2025": "2025 Inter Miami CF season",
}

# Autres fichiers : nom local -> URL.
FICHIERS = {
    "openfootball/cdm_2026.json": f"{OPENFOOTBALL}/worldcup.json/master/2026/worldcup.json",
    "openfootball/ldc_2025-26.txt": f"{OPENFOOTBALL}/champions-league/master/2025-26/cl.txt",
    "cotes/polymarket.json": "https://gamma-api.polymarket.com/events?slug=ballon-dor-winner-2026",
    "cotes/kalshi.json": "https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXBALLONDOR&limit=200",
}


def url_wikipedia(titre):
    return "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "parse", "page": titre, "prop": "wikitext", "redirects": 1,
        "format": "json", "formatversion": "2",
    })


def telecharger(url):
    requete = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(requete, timeout=60) as reponse:
        return reponse.read()


def main():
    """Sans argument : tout. Avec « saisons » : seulement les pages de saison des clubs."""
    DOSSIER.mkdir(parents=True, exist_ok=True)
    taches = [(f"wikipedia/{nom}.json", url_wikipedia(titre)) for nom, titre in SAISONS_CLUBS.items()]
    if sys.argv[1:] != ["saisons"]:
        taches += [(f"wikipedia/{nom}.json", url_wikipedia(titre)) for nom, titre in PAGES_WIKIPEDIA.items()]
        taches += list(FICHIERS.items())

    lignes, echecs = [], []
    for nom, url in taches:
        chemin = DOSSIER / nom
        chemin.parent.mkdir(parents=True, exist_ok=True)
        date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            contenu = telecharger(url)
            if nom.startswith("wikipedia/") and "error" in json.loads(contenu):
                raise ValueError(json.loads(contenu)["error"].get("info", "page introuvable"))
        except Exception as e:
            echecs.append(nom)
            print(f"échec  {nom} : {e}")
            continue
        chemin.write_bytes(contenu)
        lignes.append({"fichier": nom, "url": url, "telecharge_le": date,
                       "sha256": hashlib.sha256(contenu).hexdigest()})
        print(f"ok     {nom} ({len(contenu)} octets)")
        if nom.startswith("wikipedia/"):
            time.sleep(0.5)  # Wikipédia demande de ne pas enchaîner les requêtes trop vite

    # On garde les lignes des fichiers non retéléchargés (échec ou dépôt manuel).
    anciennes = []
    if PROVENANCE.exists():
        with open(PROVENANCE, encoding="utf-8") as f:
            nouveaux = {l["fichier"] for l in lignes}
            anciennes = [l for l in csv.DictReader(f) if l["fichier"] not in nouveaux]
    with open(PROVENANCE, "w", newline="", encoding="utf-8") as f:
        ecrivain = csv.DictWriter(f, fieldnames=["fichier", "url", "telecharge_le", "sha256"])
        ecrivain.writeheader()
        ecrivain.writerows(sorted(anciennes + lignes, key=lambda l: l["fichier"]))

    print(f"{len(lignes)} fichiers téléchargés, {len(echecs)} échecs")
    if len(echecs) == len(taches):
        sys.exit("Aucun fichier n'a pu être téléchargé.")


if __name__ == "__main__":
    main()
