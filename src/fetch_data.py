"""Récupère les données en ligne et vérifie le cache du dépôt.

Ce script est lancé par la GitHub Action avant build.py. Il :
  1. télécharge la page Wikipédia « 2026 Ballon d'Or » (API officielle de Wikipédia,
     usage autorisé avec un User-Agent qui identifie le projet) ;
  2. la met en cache dans data/cache/ ;
  3. vérifie que les 30 nommés de data/nommes_2026.csv y figurent bien.

Si Internet ne répond pas, on garde le cache existant : la page se construit quand même.
"""

import csv
import json
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_CACHE = RACINE / "data" / "cache"
FICHIER_PAGE = DOSSIER_CACHE / "wikipedia_ballon_dor_2026.json"
FICHIER_VERIF = DOSSIER_CACHE / "verification.json"

PAGE_WIKIPEDIA = "2026 Ballon d'Or"
URL_API = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
    "action": "parse", "page": PAGE_WIKIPEDIA, "prop": "wikitext",
    "format": "json", "formatversion": "2",
})
# Wikipédia demande un User-Agent qui permet de contacter l'auteur du script.
USER_AGENT = "ballon-dor-2026/1.0 (projet personnel ; https://github.com/badis-ar/ballon-dor-2026)"


def sans_accents(texte):
    """« Mbappé » -> « mbappe » : pour comparer des noms sans se soucier des accents."""
    decompose = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c)).lower()


def telecharger_wikipedia():
    """Télécharge le texte source de la page Wikipédia. Renvoie le texte (ou lève une erreur)."""
    requete = urllib.request.Request(URL_API, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(requete, timeout=30) as reponse:
        donnees = json.load(reponse)
    return donnees["parse"]["wikitext"]


def nom_present(nom, texte):
    """Un joueur est trouvé si un des mots de son nom (4 lettres ou plus) apparaît dans le texte."""
    mots = [m for m in sans_accents(nom).replace("-", " ").split() if len(m) >= 4]
    return any(m in texte for m in mots)


def main():
    DOSSIER_CACHE.mkdir(parents=True, exist_ok=True)
    maintenant = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # 1. Téléchargement (ou repli sur le cache)
    try:
        texte = telecharger_wikipedia()
        FICHIER_PAGE.write_text(json.dumps({"date": maintenant, "wikitext": texte}, ensure_ascii=False),
                                encoding="utf-8")
        origine = f"Wikipédia, téléchargé le {maintenant}"
        print(f"✔ Page Wikipédia téléchargée ({len(texte)} caractères)")
    except Exception as erreur:  # pas d'Internet, page renommée, etc.
        print(f"⚠ Téléchargement impossible : {erreur}")
        if FICHIER_PAGE.exists():
            cache = json.loads(FICHIER_PAGE.read_text(encoding="utf-8"))
            texte = cache["wikitext"]
            origine = f"cache Wikipédia du {cache['date']} (hors ligne)"
            print("→ On utilise le cache existant")
        else:
            FICHIER_VERIF.write_text(json.dumps({
                "statut": "non vérifié", "date": maintenant,
                "detail": "Wikipédia inaccessible et aucun cache disponible.",
            }, ensure_ascii=False, indent=2), encoding="utf-8")
            print("→ Aucun cache : vérification ignorée (la page sera construite quand même)")
            return

    # 2. Vérification des 30 nommés
    texte_normalise = sans_accents(texte)
    with open(RACINE / "data" / "nommes_2026.csv", encoding="utf-8") as f:
        noms = [ligne["joueur"] for ligne in csv.DictReader(f)]
    manquants = [n for n in noms if not nom_present(n, texte_normalise)]

    FICHIER_VERIF.write_text(json.dumps({
        "statut": "ok" if not manquants else "à vérifier",
        "date": maintenant,
        "origine": origine,
        "trouves": len(noms) - len(manquants),
        "total": len(noms),
        "manquants": manquants,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✔ {len(noms) - len(manquants)}/{len(noms)} nommés retrouvés sur Wikipédia")
    for n in manquants:
        print(f"  ⚠ introuvable : {n}")


if __name__ == "__main__":
    main()
