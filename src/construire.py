"""Construit la page : python src/construire.py

Lit les tableaux préparés (site/donnees/, voir preparation.py) et config/poids.yaml,
applique le modèle, écrit site/index.html et site/donnees/resultats.csv.
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

import yaml

import modele
import page

RACINE = Path(__file__).resolve().parent.parent
DONNEES = RACINE / "site" / "donnees"
SITE = RACINE / "site"
NUMERIQUES = {"cdm_buts", "cdm_passes", "cdm_minutes", "ldc_buts", "ldc_passes", "ldc_minutes",
              "champ_buts", "champ_passes", "champ_minutes", "champ_titre", "coupe_nat", "podiums_points"}


def erreur(message):
    sys.exit(f"Erreur : {message}")


def lire_csv(nom):
    with open(DONNEES / nom, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def lire_config():
    try:
        config = yaml.safe_load((RACINE / "config" / "poids.yaml").read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        erreur(f"config/poids.yaml est mal écrit : {e}")
    temperature = config.pop("temperature", None)
    if not isinstance(temperature, (int, float)) or temperature <= 0:
        erreur("config/poids.yaml : « temperature » doit être un nombre positif.")
    for critere, valeur in config.items():
        if critere not in modele.CRITERES:
            erreur(f"config/poids.yaml : critère inconnu « {critere} » (possibles : {', '.join(modele.CRITERES)}).")
        if not isinstance(valeur, (int, float)) or valeur < 0:
            erreur(f"config/poids.yaml : le poids de « {critere} » doit être un nombre positif.")
    return config, temperature


def main():
    poids_config, temperature = lire_config()
    nommes = lire_csv("nommes_2026.csv")

    # Valeurs sourcées : {joueur: {donnée: valeur}} et {joueur: {donnée: ligne source}}
    valeurs, sources = defaultdict(dict), defaultdict(dict)
    for ligne in lire_csv("valeurs_2026.csv"):
        v = ligne["valeur"]
        valeurs[ligne["joueur"]][ligne["donnee"]] = int(v) if ligne["donnee"] in NUMERIQUES else v
        sources[ligne["joueur"]][ligne["donnee"]] = ligne
    valeurs = {j["joueur"]: valeurs[j["joueur"]] for j in nommes}
    modele.completer_absents(valeurs)

    dispo = modele.elements_disponibles(valeurs)
    poids = modele.poids_effectifs(poids_config, dispo)
    for j in nommes:
        j["notes"] = modele.notes_joueur(valeurs[j["joueur"]], dispo)
        j["note"] = modele.note_finale(j["notes"], poids)
    for j, p in zip(nommes, modele.softmax([j["note"] for j in nommes], temperature)):
        j["proba"] = p
    nommes.sort(key=lambda j: -j["proba"])

    cotes = defaultdict(dict)
    for c in lire_csv("cotes_2026.csv"):
        cotes[c["source"]][c["joueur"]] = c
    with open(RACINE / "data" / "provenance.csv", encoding="utf-8") as f:
        provenance = list(csv.DictReader(f))

    SITE.mkdir(exist_ok=True)
    html = page.generer(nommes, valeurs, sources, dispo, poids_config, poids, temperature,
                        cotes, lire_csv("historique.csv"), provenance)
    (SITE / "index.html").write_text(html, encoding="utf-8")

    with open(DONNEES / "resultats.csv", "w", newline="", encoding="utf-8") as f:
        ecrivain = csv.writer(f)
        ecrivain.writerow(["rang", "joueur", "club", "probabilite_pct", "note_sur_100"] + list(poids))
        for rang, j in enumerate(nommes, start=1):
            ecrivain.writerow([rang, j["joueur"], j["club"], round(100 * j["proba"], 2), round(j["note"], 1)]
                              + [round(j["notes"][c], 3) for c in poids])

    print("Critères utilisés : " + ", ".join(f"{c} {100 * p:.0f} %" for c, p in poids.items()))
    for rang, j in enumerate(nommes[:5], start=1):
        print(f"{rang}. {j['joueur']:<24} {100 * j['proba']:5.1f} %  (note {j['note']:.1f})")


if __name__ == "__main__":
    main()
