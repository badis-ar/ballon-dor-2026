"""Construit la page web : python src/build.py

Lit les données (data/), les poids (config/poids.yaml), fait tourner le modèle,
puis écrit le site dans le dossier site/ (index.html + resultats.csv).
"""

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

import modele
import page

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_SITE = RACINE / "site"
DATE_COLLECTE = "21 octobre 2026"
ANNEE_DEBUT_VALIDATION = 2010

# Colonnes qui doivent contenir des nombres entiers.
COLONNES_ENTIERES = ["annee", "rang", "buts_champ", "passes_champ", "minutes_champ", "titre_champ",
                     "coupe_nat", "ldc_buts_passes", "tournoi_buts_passes", "prix_saison"]


def erreur(message):
    """Arrête le programme avec un message clair (visible dans l'onglet Actions de GitHub)."""
    print(f"❌ ERREUR : {message}")
    sys.exit(1)


def lire_csv(nom_fichier):
    """Lit un fichier CSV de data/ et vérifie chaque valeur."""
    chemin = RACINE / "data" / nom_fichier
    with open(chemin, encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    for numero, ligne in enumerate(lignes, start=2):  # ligne 1 = les titres des colonnes
        for colonne in COLONNES_ENTIERES:
            if colonne in ligne:
                try:
                    ligne[colonne] = int(ligne[colonne])
                except (TypeError, ValueError):
                    erreur(f"{nom_fichier}, ligne {numero} : « {colonne} » doit être un nombre entier "
                           f"(valeur lue : {ligne[colonne]!r})")
        if "ldc_stade" in ligne and ligne["ldc_stade"] not in modele.STADES_LDC:
            erreur(f"{nom_fichier}, ligne {numero} : ldc_stade inconnu {ligne['ldc_stade']!r} "
                   f"(valeurs possibles : {', '.join(modele.STADES_LDC)})")
        if "tournoi_stade" in ligne and ligne["tournoi_stade"] not in modele.STADES_TOURNOI:
            erreur(f"{nom_fichier}, ligne {numero} : tournoi_stade inconnu {ligne['tournoi_stade']!r} "
                   f"(valeurs possibles : {', '.join(modele.STADES_TOURNOI)})")
        if "tournoi_prix" in ligne and ligne["tournoi_prix"] not in modele.PRIX_TOURNOI:
            erreur(f"{nom_fichier}, ligne {numero} : tournoi_prix inconnu {ligne['tournoi_prix']!r}")
    return lignes


def lire_poids():
    """Lit config/poids.yaml et vérifie que chaque poids est un nombre positif."""
    try:
        poids = yaml.safe_load((RACINE / "config" / "poids.yaml").read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        erreur(f"config/poids.yaml est mal écrit : {e}")
    if not isinstance(poids, dict):
        erreur("config/poids.yaml doit contenir des lignes « critère: poids »")
    for critere, valeur in poids.items():
        if critere not in modele.CRITERES:
            erreur(f"config/poids.yaml : critère inconnu « {critere} » "
                   f"(critères possibles : {', '.join(modele.CRITERES)})")
        if not isinstance(valeur, (int, float)) or valeur < 0:
            erreur(f"config/poids.yaml : le poids de « {critere} » doit être un nombre positif (lu : {valeur!r})")
    return poids


def cote_en_probabilite(cote):
    """« 5/4 » -> 1 / (1 + 5/4) = 0,44 ; « 66% » -> 0,66."""
    cote = cote.strip()
    if cote.endswith("%"):
        return float(cote[:-1]) / 100
    gain, mise = cote.split("/")
    return 1 / (1 + float(gain) / float(mise))


def main():
    # 1. Lecture des fichiers
    poids_config = lire_poids()
    poids = modele.poids_effectifs(poids_config)
    historique = lire_csv("historique_top5.csv")
    nommes = lire_csv("nommes_2026.csv")
    avant_2003 = lire_csv("podiums_avant_2003.csv")
    if len(nommes) != 30:
        print(f"⚠ Attention : {len(nommes)} nommés au lieu de 30 dans nommes_2026.csv")

    # Liste de tous les podiums connus (année, rang, nom), pour le critère « prestige ».
    podiums = [(j["annee"], j["rang"], j["joueur"]) for j in avant_2003 + historique if j["rang"] <= 3]

    # 2. Validation sur l'historique et calibrage de la température
    historique_validation = [j for j in historique if j["annee"] >= ANNEE_DEBUT_VALIDATION]
    par_annee = modele.notes_par_annee(historique_validation, podiums, poids)
    temperature = modele.calibrer_temperature(par_annee)
    validation = modele.valider(par_annee, temperature)
    exploration = modele.explorer_poids(historique_validation, podiums, poids["coupe_du_monde"])

    # 3. Notes et probabilités des 30 nommés
    for j in nommes:
        points = modele.points_podiums_avant(j["joueur"], 2026, podiums)
        j["notes"] = modele.notes_criteres(j, points)
        j["note"] = modele.note_finale(j["notes"], poids)
    for j, p in zip(nommes, modele.softmax([j["note"] for j in nommes], temperature)):
        j["proba"] = p
    nommes.sort(key=lambda j: -j["proba"])
    for rang, j in enumerate(nommes, start=1):
        j["rang"] = rang

    # 4. Cotes des bookmakers : {(source, date): {joueur: probabilité implicite}}
    cotes = {}
    noms_connus = {j["joueur"] for j in nommes}
    with open(RACINE / "data" / "cotes_2026.csv", encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            if ligne["joueur"] not in noms_connus:
                erreur(f"cotes_2026.csv : joueur inconnu « {ligne['joueur']} » (doit être écrit comme dans nommes_2026.csv)")
            cotes.setdefault((ligne["source"], ligne["date"]), {})[ligne["joueur"]] = cote_en_probabilite(ligne["cote"])

    # 5. Résultat de la vérification en ligne (fait par fetch_data.py), s'il existe
    fichier_verif = RACINE / "data" / "cache" / "verification.json"
    verification = json.loads(fichier_verif.read_text(encoding="utf-8")) if fichier_verif.exists() else None

    # 6. Écriture du site
    try:
        maintenant = datetime.now(ZoneInfo("Europe/Paris"))
        date_maj = maintenant.strftime("%d/%m/%Y à %H:%M (heure de Paris)")
    except Exception:  # fuseau horaire indisponible
        date_maj = datetime.now(timezone.utc).strftime("%d/%m/%Y à %H:%M UTC")

    html = page.generer(nommes, poids_config, poids, temperature, validation, exploration,
                        cotes, verification, date_maj, DATE_COLLECTE)
    DOSSIER_SITE.mkdir(exist_ok=True)
    (DOSSIER_SITE / "index.html").write_text(html, encoding="utf-8")

    with open(DOSSIER_SITE / "resultats.csv", "w", newline="", encoding="utf-8") as f:
        ecrivain = csv.writer(f)
        ecrivain.writerow(["rang", "joueur", "club", "probabilite_pct", "note_sur_100",
                           "note_cdm", "note_club", "note_ldc", "note_prestige", "fiabilite"])
        for j in nommes:
            n = j["notes"]
            ecrivain.writerow([j["rang"], j["joueur"], j["club"], round(100 * j["proba"], 2), round(j["note"], 1),
                               round(n["coupe_du_monde"], 3), round(n["saison_club"], 3),
                               round(n["ligue_des_champions"], 3), round(n["prestige"], 3), j["fiabilite"]])

    # 7. Résumé dans la console
    print("Poids utilisés : " + ", ".join(f"{c} {100 * p:.1f} %" for c, p in poids.items()))
    print(f"Température T = {temperature}")
    print(f"Validation {ANNEE_DEBUT_VALIDATION}-2025 : {sum(v['top1'] for v in validation)}/{len(validation)} "
          f"vainqueurs retrouvés (top 3 : {sum(v['top3'] for v in validation)}/{len(validation)})")
    print("Top 5 2026 :")
    for j in nommes[:5]:
        print(f"  {j['rang']}. {j['joueur']:<24} {100 * j['proba']:5.1f} %  (note {j['note']:.1f})")
    print(f"✔ Page écrite dans {DOSSIER_SITE / 'index.html'}")


if __name__ == "__main__":
    main()
