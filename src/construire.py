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
              "champ_buts", "champ_passes", "champ_minutes", "champ_titre", "coupe_nat", "podiums_points", "champ_niveau"}


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
    temperature = config.get("temperature")
    if not isinstance(temperature, (int, float)) or temperature <= 0:
        erreur("config/poids.yaml : « temperature » doit être un nombre positif.")
    methode = config.get("methode")
    if methode not in modele.METHODES:
        erreur(f"config/poids.yaml : « methode » doit valoir {' ou '.join(modele.METHODES)}.")
    poids = {}
    for m, criteres in modele.METHODES.items():
        poids[m] = config.get(m) or {}
        for critere, valeur in poids[m].items():
            if critere not in criteres:
                erreur(f"config/poids.yaml, méthode {m} : critère inconnu « {critere} » "
                       f"(possibles : {', '.join(criteres)}).")
            if not isinstance(valeur, (int, float)) or valeur < 0:
                erreur(f"config/poids.yaml : le poids de « {critere} » doit être un nombre positif.")
    correction = config.get("correction_niveau", False)
    if not isinstance(correction, bool):
        erreur("config/poids.yaml : « correction_niveau » doit valoir true ou false.")
    return methode, poids, temperature, correction


def appliquer(nommes, valeurs, methode, poids_config, temperature):
    """Notes et probabilités d'une méthode : {joueur: {notes, note, proba}}, éléments utilisés, poids."""
    dispo = modele.elements_disponibles(valeurs, methode)
    poids = modele.poids_effectifs(poids_config, dispo, methode)
    res = {}
    for j in nommes:
        notes = modele.notes_joueur(valeurs[j["joueur"]], dispo, methode)
        res[j["joueur"]] = {"notes": notes, "note": modele.note_finale(notes, poids)}
    probas = modele.softmax([res[j["joueur"]]["note"] for j in nommes], temperature)
    for j, p in zip(nommes, probas):
        res[j["joueur"]]["proba"] = p
    return res, dispo, poids


def main():
    methode, poids_config, temperature, correction = lire_config()
    autre = next(m for m in modele.METHODES if m != methode)
    nommes = lire_csv("nommes_2026.csv")

    # Valeurs sourcées : {joueur: {donnée: valeur}} et {joueur: {donnée: ligne source}}
    valeurs, sources = defaultdict(dict), defaultdict(dict)
    for ligne in lire_csv("valeurs_2026.csv"):
        v = ligne["valeur"]
        valeurs[ligne["joueur"]][ligne["donnee"]] = (float(v) if "." in v else int(v)) if ligne["donnee"] in NUMERIQUES else v
        sources[ligne["joueur"]][ligne["donnee"]] = ligne
    valeurs = {j["joueur"]: valeurs[j["joueur"]] for j in nommes}
    modele.completer_absents(valeurs)
    modele.corriger_niveau(valeurs, correction)

    resultats = {m: appliquer(nommes, valeurs, m, poids_config[m], temperature) for m in modele.METHODES}
    res, dispo, poids = resultats[methode]
    for j in nommes:
        j.update(res[j["joueur"]])
        j["proba_autre"] = resultats[autre][0][j["joueur"]]["proba"]
    nommes.sort(key=lambda j: -j["proba"])

    cotes = defaultdict(dict)
    for c in lire_csv("cotes_2026.csv"):
        cotes[c["source"]][c["joueur"]] = c
    with open(RACINE / "data" / "provenance.csv", encoding="utf-8") as f:
        provenance = list(csv.DictReader(f))

    SITE.mkdir(exist_ok=True)
    methodes = {m: {"dispo": r[1], "poids": r[2], "poids_config": poids_config[m]} for m, r in resultats.items()}
    html = page.generer(nommes, valeurs, sources, methode, methodes, temperature, correction,
                        cotes, lire_csv("historique.csv"), provenance)
    (SITE / "index.html").write_text(html, encoding="utf-8")

    with open(DONNEES / "resultats.csv", "w", newline="", encoding="utf-8") as f:
        ecrivain = csv.writer(f)
        ecrivain.writerow(["rang", "joueur", "club", f"probabilite_pct_{methode}", "note_sur_100"]
                          + list(poids) + [f"probabilite_pct_{autre}"])
        for rang, j in enumerate(nommes, start=1):
            ecrivain.writerow([rang, j["joueur"], j["club"], round(100 * j["proba"], 2), round(j["note"], 1)]
                              + [round(j["notes"][c], 3) for c in poids] + [round(100 * j["proba_autre"], 2)])

    print(f"Méthode {methode}. Critères utilisés : " + ", ".join(f"{c} {100 * p:.0f} %" for c, p in poids.items()))
    for rang, j in enumerate(nommes[:5], start=1):
        print(f"{rang}. {j['joueur']:<24} {100 * j['proba']:5.1f} %  (note {j['note']:.1f}, "
              f"méthode {autre} : {100 * j['proba_autre']:.1f} %)")


if __name__ == "__main__":
    main()
