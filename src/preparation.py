"""Transforme les fichiers téléchargés (data/) en tableaux propres, avec une source par valeur.

Sorties, dans site/donnees/ (publiées avec la page) :
  nommes_2026.csv   les 30 nommés (nom, nation, poste, club)
  valeurs_2026.csv  une ligne par valeur : joueur, donnée, valeur, source, URL
  historique.csv    top 5 de chaque édition 1996-2025 (classement et points)
  cotes_2026.csv    probabilités des marchés de prédiction
  controles.json    fichiers FBref présents et joueurs introuvables

Règle : une valeur sans source n'est pas écrite. Une donnée absente reste absente.
"""

import csv
import json
import re
from pathlib import Path

import wikitexte as wt

RACINE = Path(__file__).resolve().parent.parent
BRUT = RACINE / "data"
SORTIE = RACINE / "site" / "donnees"

URL_OPENFOOTBALL_CDM = "https://github.com/openfootball/worldcup.json/blob/master/2026/worldcup.json"
URL_OPENFOOTBALL_LDC = "https://github.com/openfootball/champions-league/blob/master/2025-26/cl.txt"
URL_HISTORIQUE = "https://badis-ar.github.io/ballon-dor-2026/donnees/historique.csv"
URL_POLYMARKET = "https://polymarket.com/event/ballon-dor-winner-2026"
URL_KALSHI = "https://kalshi.com/markets/kxballondor"

# Championnats et coupes nationales (fichiers de data/wikipedia/).
CHAMPIONNATS = ["angleterre_2025-26", "espagne_2025-26", "allemagne_2025-26", "italie_2025-26",
                "france_2025-26", "arabie_2025-26", "mls_2025"]
COUPE_DU_PAYS = {"angleterre_2025-26": "coupe_angleterre_2025-26", "espagne_2025-26": "coupe_espagne_2025-26",
                 "allemagne_2025-26": "coupe_allemagne_2025-26", "italie_2025-26": "coupe_italie_2025-26",
                 "france_2025-26": "coupe_france_2025-26", "arabie_2025-26": "coupe_arabie_2025-26",
                 "mls_2025": "coupe_usa_2025"}

# Noms de clubs différents entre Wikipédia et openfootball.
ALIAS_OPENFOOTBALL = {"Bayern Munich": "FC Bayern München", "Inter Milan": "FC Internazionale Milano"}

# Fichiers FBref déposés à la main dans data/fbref/ (voir docs/sources.md) : fichier -> préfixe des données.
FICHIERS_FBREF = {
    "fbref_ligues_2025-26.csv": "champ",
    "fbref_mls_2025.csv": "champ",
    "fbref_saudi_2025-26.csv": "champ",
    "fbref_ldc_2025-26.csv": "ldc",
    "fbref_cdm_2026.csv": "cdm",
}
URL_FBREF = {
    "fbref_ligues_2025-26.csv": "https://fbref.com/en/comps/Big5/2025-2026/stats/players/2025-2026-Big-5-European-Leagues-Stats",
    "fbref_mls_2025.csv": "https://fbref.com/en/comps/22/2025/stats/2025-Major-League-Soccer-Stats",
    "fbref_saudi_2025-26.csv": "https://fbref.com/en/comps/70/2025-2026/stats/2025-2026-Saudi-Pro-League-Stats",
    "fbref_ldc_2025-26.csv": "https://fbref.com/en/comps/8/2025-2026/stats/2025-2026-Champions-League-Stats",
    "fbref_cdm_2026.csv": "https://fbref.com/en/comps/1/stats/World-Cup-Stats",
}


def page(nom):
    """(titre, wikitext, url) d'une page Wikipédia téléchargée, ou None si absente."""
    chemin = BRUT / "wikipedia" / f"{nom}.json"
    if not chemin.exists():
        return None
    titre, texte = wt.lire_page(chemin)
    return titre, texte, wt.url_page(titre)


def cible_lien(cellule):
    """« [[Real Madrid CF|Real Madrid]] » -> « Real Madrid CF » (premier lien hors modèles)."""
    m = re.search(r"\[\[([^\]|]+)", re.sub(r"\{\{[^{}]*\}\}", "", cellule))
    return m.group(1).strip() if m else None


def date_telechargement(fichier):
    """Date de téléchargement notée dans data/provenance.csv."""
    with open(BRUT / "provenance.csv", encoding="utf-8") as f:
        for l in csv.DictReader(f):
            if l["fichier"] == fichier:
                return l["telecharge_le"][:16].replace("T", " ") + " UTC"
    return ""


def lire_json(chemin):
    return json.loads(chemin.read_text(encoding="utf-8"))


# --- Les 30 nommés ---------------------------------------------------------------

def nommes():
    titre, texte, url = page("ballon_dor_2026")
    for entetes, lignes in wt.tableaux(texte):
        if "Player" in entetes and "Club" in entetes:
            i_j, i_n, i_p, i_c = (entetes.index(c) for c in ("Player", "Nationality", "Position", "Club"))
            joueurs = []
            for l in lignes:
                joueurs.append({
                    "joueur": wt.premier_lien(l[i_j]),
                    "nation": wt.nettoyer(l[i_n]),
                    "poste": wt.nettoyer(l[i_p]) or wt.premier_lien(l[i_p]),
                    "club": wt.nettoyer(l[i_c]),
                    "club_page": cible_lien(l[i_c]),
                    "source": url,
                })
            return joueurs
    raise SystemExit("Tableau des nommés introuvable sur la page Wikipédia 2026.")


# --- Historique ------------------------------------------------------------------

def historique():
    lignes_sortie = []
    for chemin in sorted((BRUT / "wikipedia").glob("ballon_dor_[0-9][0-9][0-9][0-9].json")):
        annee = int(chemin.stem[-4:])
        if annee >= 2026:
            continue
        titre, texte = wt.lire_page(chemin)
        trouves = {}
        for entetes, lignes in wt.tableaux(texte):
            if "Rank" not in entetes or "Player" not in entetes:
                continue
            i_j = entetes.index("Player")
            i_pts = next((entetes.index(c) for c in ("Points", "Total", "Percent") if c in entetes), None)
            for l in lignes:
                m = re.match(r"^\s*(\d+)", wt.nettoyer(l[0]) if l else "")
                if not m or len(l) <= i_j:
                    continue
                rang = int(m.group(1))
                if rang <= 5 and rang not in trouves:
                    points = wt.nettoyer(l[i_pts]) if i_pts is not None and len(l) > i_pts else ""
                    trouves[rang] = (wt.premier_lien(l[i_j]), points)
        for rang in sorted(trouves):
            joueur, points = trouves[rang]
            if joueur:
                lignes_sortie.append({"annee": annee, "rang": rang, "joueur": joueur,
                                      "points": points, "source": wt.url_page(titre)})
    return lignes_sortie


# --- Coupe du monde 2026 (openfootball + Wikipédia pour les prix) ---------------

def stades_cdm(matchs):
    """Dernier tour atteint par chaque sélection : V, F, DF, QF, HF, 16F, P."""
    ordre = {"Round of 32": "16F", "Round of 16": "HF", "Quarter-final": "QF",
             "Semi-final": "DF", "Match for third place": "DF"}
    stades = {}
    for m in matchs:
        for equipe in (m["team1"], m["team2"]):
            stades.setdefault(equipe, "P")
            if m["round"] in ordre:
                stades[equipe] = ordre[m["round"]]
        if m["round"] == "Final":
            s = m["score"]
            final = s.get("p") or s.get("et") or s["ft"]
            gagnant, perdant = (m["team1"], m["team2"]) if final[0] > final[1] else (m["team2"], m["team1"])
            stades[gagnant], stades[perdant] = "V", "F"
    return stades


def buts_cdm(matchs):
    """{(sélection, nom sans accents): buts}, sans les buts contre son camp."""
    buts = {}
    for m in matchs:
        for cle, equipe in (("goals1", m["team1"]), ("goals2", m["team2"])):
            for b in m.get(cle, []):
                if not b.get("owngoal"):
                    k = (equipe, wt.sans_accents(b["name"]))
                    buts[k] = buts.get(k, 0) + 1
    return buts


def prix_cdm():
    """{nom sans accents: code du meilleur prix} d'après le tableau « Awards » de Wikipédia."""
    titre, texte, url = page("cdm_2026")
    codes = {"Golden Ball": "ballon_or", "Silver Ball": "ballon_argent", "Bronze Ball": "ballon_bronze",
             "Golden Boot": "soulier_or", "Silver Boot": "autre", "Bronze Boot": "autre",
             "Golden Glove": "autre", "FIFA Young Player Award": "autre"}
    rang = ["ballon_or", "ballon_argent", "soulier_or", "ballon_bronze", "autre"]
    prix = {}
    for entetes, lignes in wt.tableaux(texte):
        if "Golden Ball" not in entetes:
            continue
        rangees = [entetes] + [[wt.nettoyer(c) for c in l] for l in lignes]
        brutes = [None] + lignes
        for i in range(0, len(rangees) - 1, 2):
            for nom_prix, cellule in zip(rangees[i], brutes[i + 1]):
                joueur = wt.premier_lien(cellule)
                code = codes.get(nom_prix)
                if joueur and code:
                    k = wt.sans_accents(joueur)
                    if k not in prix or rang.index(code) < rang.index(prix[k]):
                        prix[k] = code
    return prix, url


def meme_joueur(nom, autre):
    """Même nom complet, ou même nom de famille quand l'un des deux n'a qu'un mot de plus."""
    a, b = wt.sans_accents(nom), wt.sans_accents(autre)
    return a == b or (a.split()[-1] == b.split()[-1] and (a in b or b in a))


# --- Ligue des champions 2025-26 (openfootball) ----------------------------------

def stades_ldc():
    """{nom openfootball du club: dernier tour atteint}."""
    codes = {"League": "P", "Playoffs": "P", "Round of 16": "HF", "Quarterfinals": "QF",
             "Semifinals": "DF", "Final": "F"}
    stades, tour = {}, None
    for ligne in (BRUT / "openfootball" / "ldc_2025-26.txt").read_text(encoding="utf-8").splitlines():
        if ligne.startswith("▪"):
            tour = next((c for t, c in codes.items() if t in ligne), tour)
            continue
        m = re.match(r"\s*(?:\d\d:\d\d\s+)?(.+?) \([A-Z]{3}\)\s+v (.+?) \([A-Z]{3}\)\s+(.*)$", ligne)
        if m and tour:
            for club in (m.group(1).strip(), m.group(2).strip()):
                stades[club] = tour
            if tour == "F":
                score = m.group(3)
                pen = re.match(r"(\d+)-(\d+) pen", score)
                buts = pen or re.match(r"(\d+)-(\d+)", score)
                g1, g2 = int(buts.group(1)), int(buts.group(2))
                stades[m.group(1).strip() if g1 > g2 else m.group(2).strip()] = "V"
    return stades


def club_ldc(club, stades):
    nom = ALIAS_OPENFOOTBALL.get(club, club)
    candidats = [c for c in stades if wt.sans_accents(nom) in wt.sans_accents(c)]
    return candidats[0] if len(candidats) == 1 else None


# --- Titres nationaux (Wikipédia, infobox « winners ») ---------------------------

def vainqueur(nom_page):
    p = page(nom_page)
    if not p:
        return None, None
    titre, texte, url = p
    champ = wt.champ_infobox(texte, "winners") or wt.champ_infobox(texte, "mlscup") or wt.champ_infobox(texte, "champions")
    return (cible_lien(champ) if champ else None), url


def cle_club(nom):
    """« Paris Saint-Germain F.C. » et « Paris Saint-Germain FC » -> même clé."""
    mots = re.sub(r"[^a-z0-9 ]", " ", wt.sans_accents(nom).replace(".", "")).split()
    return " ".join(m for m in mots if m not in ("fc", "cf", "afc", "sc"))


def championnat_du_club(club_page):
    """Page du championnat où le club apparaît le plus souvent (liste des équipes, résultats)."""
    meilleur, compte_max = None, 0
    for nom in CHAMPIONNATS:
        p = page(nom)
        if p:
            cibles = re.findall(r"\[\[([^\]|#]+)", p[1])
            compte = sum(cle_club(c) == cle_club(club_page) for c in cibles)
            if compte > compte_max:
                meilleur, compte_max = nom, compte
    return meilleur


# --- Saisons des clubs (Wikipédia) : buts dans les autres compétitions ---------------

# Club (tel qu'écrit dans la liste des nommés) -> (page de saison, titre de la section, colonnes).
# Colonnes : une lettre par nombre lu après le nom du joueur, dans l'ordre du tableau.
#   L = championnat, U = Ligue des champions (déjà lus dans FBref, servent de contrôle),
#   C = autre compétition de club comptée (coupes, supercoupes, autres coupes continentales),
#   X = ignoré (matchs joués, ou Coupe du monde des clubs 2025, jouée avant août 2025).
# « liste_buteurs » : le tableau ne liste que les buteurs, un joueur absent a donc 0 but.
SAISONS = {
    "Real Madrid": ("saison_real_madrid_2025-26", "===Goals===", "LCUC", True),
    "Barcelona": ("saison_barcelone_2025-26", "===Goalscorers===", "LCCU", True),
    "Chelsea": ("saison_chelsea_2025-26", "===Goalscorers===", "LCCU", True),
    "Paris Saint-Germain": ("saison_psg_2025-26", "===Appearances and goals===", "XLXCXCXUXCXC", False),
    "Bayern Munich": ("saison_bayern_2025-26", "===Goalscorers===", "LCCU", True),
    "Manchester United": ("saison_manchester_united_2025-26", "==Squad statistics==", "XLXCXC", False),
    "Arsenal": ("saison_arsenal_2025-26", "===Goals===", "LCCU", True),
    "Manchester City": ("saison_manchester_city_2025-26", "===Goalscorers===", "LCCU", True),
    "Inter Milan": ("saison_inter_2025-26", "===Goalscorers===", "LCCU", True),
    "Al Nassr": ("saison_al_nassr_2025-26", "===Goalscorers===", "LCCC", True),
    "Al-Qadsiah": ("saison_al_qadsiah_2025-26", "===Goalscorers===", "LCC", True),
    "Inter Miami": ("saison_inter_miami_2025", "=== Goalscorers ===", "LCCXC", True),
}
NOMBRE = re.compile(r"^(\d+(\+\d+)?(\(\d+\))?|—|-)$")


def section(texte, titre):
    """Texte d'une section, de son titre jusqu'au titre suivant."""
    i = texte.find("\n" + titre)
    if i < 0:
        return None
    fin = texte.find("\n==", i + len(titre) + 1)
    return texte[i:fin if fin > 0 else None]


def nombres_apres(texte, fin_nom):
    """Nombres de la rangée qui suit le nom du joueur (jusqu'à la rangée suivante)."""
    reste = texte[fin_nom:]
    if reste.lstrip("]").startswith("|") and "{{Efs" in texte:  # rangée dans un modèle {{Efs player|...}}
        reste = reste[:reste.find("}}")]
    else:
        coupe = [k for k in (reste.find("\n|-"), reste.find("\n|}")) if k >= 0]
        reste = reste[:min(coupe)] if coupe else reste
        reste = re.sub(r"\[\[[^\]]*\]\]|\{\{[^{}]*\}\}", "", reste)
    reste = re.sub(r"<ref[^>]*/>|<ref.*?</ref>|<sup>.*?</sup>", "", reste, flags=re.S)
    reste = re.sub(r"(rowspan|colspan|style|align)\s*=\s*\"?[^|\"]*\"?\s*\|(?!\|)", "", reste)
    jetons = [c.strip().strip("'").strip() for c in re.split(r"\|\||!!|\||!|\n", reste)]
    return [c for c in jetons if NOMBRE.match(c)]


def buts_saison_club(joueur, club):
    """{championnat, ldc, autres, detail} lus sur la page de saison du club, ou None."""
    if club not in SAISONS:
        return None
    nom, titre, colonnes, liste_buteurs = SAISONS[club]
    p = page(nom)
    texte = section(p[1], titre) if p else None
    if not texte:
        return None
    for m in re.finditer(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]|\{\{sortname\|([^|}]+)\|([^|}]+)[^}]*\}\}", texte):
        affiche = (m.group(2) or m.group(1)) if m.group(1) else f"{m.group(3)} {m.group(4)}"
        if not meme_joueur(joueur, affiche.strip()):
            continue
        nombres = nombres_apres(texte, m.end())
        if len(nombres) < len(colonnes):
            return None
        valeurs = {"L": 0, "U": 0, "C": 0}
        for lettre, n in zip(colonnes, nombres):
            if lettre != "X":
                valeurs[lettre] += 0 if n in ("—", "-") else int(n)
        return {"championnat": valeurs["L"], "ldc": valeurs["U"], "autres": valeurs["C"], "url": p[2],
                "detail": f"{p[0]}, section {titre.strip('= ')}"}
    if liste_buteurs:
        return {"championnat": 0, "ldc": 0, "autres": 0, "url": p[2],
                "detail": f"{p[0]} : absent de la liste des buteurs"}
    return None


# --- FBref (fichiers déposés à la main) ------------------------------------------

def lire_fbref(chemin):
    """Lit un export CSV FBref « Player Standard Stats ». Renvoie [{joueur, minutes, buts, passes}]."""
    lignes = list(csv.reader(chemin.read_text(encoding="utf-8-sig").splitlines()))
    i_entete = next(i for i, l in enumerate(lignes) if "Player" in l and "Min" in l)
    entete = lignes[i_entete]
    i_j, i_min, i_b, i_p = (entete.index(c) for c in ("Player", "Min", "Gls", "Ast"))  # 1re occurrence = totaux
    i_club = entete.index("Squad") if "Squad" in entete else None  # absent de l'export Coupe du monde
    sortie = []
    for l in lignes[i_entete + 1:]:
        if len(l) <= max(i_j, i_min, i_b, i_p) or l[i_j] in ("", "Player"):
            continue
        nombres = [l[i].replace(",", "") for i in (i_min, i_b, i_p)]
        club = re.sub(r"^[a-z]{2,3} ", "", l[i_club]) if i_club is not None else None  # « de Bayern Munich »
        sortie.append({"joueur": l[i_j], "club": club, "minutes": nombres[0], "buts": nombres[1],
                       "passes": nombres[2]})
    return sortie


# Nom du club dans FBref, quand il diffère de la liste des nommés.
CLUB_FBREF = {"Paris Saint-Germain": "Paris SG", "Manchester United": "Manchester Utd",
              "Inter Milan": "Inter", "Al Nassr": "Al-Nassr"}


def lignes_fbref_du_joueur(nom, club, lignes):
    """Lignes FBref d'un joueur de ce club : même nom, sinon un seul joueur dont le nom complet commence
    par celui-ci (« Fabián Ruiz » -> « Fabián Ruiz Peña »). Le club écarte les homonymes
    (deux « Vitinha », deux « Luis Díaz »)."""
    if club:
        lignes = [l for l in lignes if l["club"] is None or l["club"] == CLUB_FBREF.get(club, club)]
    cle = wt.sans_accents(nom)
    exactes = [l for l in lignes if wt.sans_accents(l["joueur"]) == cle]
    if exactes:
        return exactes
    debut = [l for l in lignes if wt.sans_accents(l["joueur"]).startswith(cle + " ")]
    return debut if len({l["joueur"] for l in debut}) == 1 else []


# --- Assemblage ------------------------------------------------------------------

def main():
    SORTIE.mkdir(parents=True, exist_ok=True)
    liste = nommes()
    valeurs = []

    def ajouter(joueur, donnee, valeur, source, url, detail=""):
        if any(v["joueur"] == joueur and v["donnee"] == donnee for v in valeurs):
            raise SystemExit(f"{joueur} : « {donnee} » trouvé dans deux sources, vérifier les homonymes.")
        valeurs.append({"joueur": joueur, "donnee": donnee, "valeur": valeur, "source": source,
                        "url": url, "detail": detail})

    # Coupe du monde
    matchs = lire_json(BRUT / "openfootball" / "cdm_2026.json")["matches"]
    stades, buts, (prix, url_prix) = stades_cdm(matchs), buts_cdm(matchs), prix_cdm()
    for j in liste:
        nation = j["nation"]
        stade = stades.get(nation, "ABS")
        ajouter(j["joueur"], "cdm_stade", stade, "openfootball", URL_OPENFOOTBALL_CDM)
        if stade != "ABS":
            total = sum(n for (equipe, nom), n in buts.items() if equipe == nation and meme_joueur(j["joueur"], nom))
            ajouter(j["joueur"], "cdm_buts", total, "openfootball", URL_OPENFOOTBALL_CDM)
        ajouter(j["joueur"], "cdm_prix", prix.get(wt.sans_accents(j["joueur"]), ""), "Wikipédia", url_prix)

    # Ligue des champions
    ldc = stades_ldc()
    for j in liste:
        club = club_ldc(j["club"], ldc)
        ajouter(j["joueur"], "ldc_stade", ldc[club] if club else "ABS", "openfootball", URL_OPENFOOTBALL_LDC)

    # Niveau des championnats (Opta Power Rankings, relevé à la main), s'il a été déposé
    niveaux = {}
    fichier_niveaux = BRUT / "opta" / "niveau_championnats.csv"
    if fichier_niveaux.exists():
        with open(fichier_niveaux, encoding="utf-8") as f:
            niveaux = {l["fichier_championnat"]: l for l in csv.DictReader(f)}

    # Titres nationaux
    for j in liste:
        championnat = championnat_du_club(j["club_page"])
        if not championnat:
            continue
        if championnat in niveaux:
            n = niveaux[championnat]
            ajouter(j["joueur"], "champ_niveau", n["note"], n["source"], n["url"], n["championnat"])
        gagnant, url = vainqueur(championnat)
        if gagnant:
            ajouter(j["joueur"], "champ_titre", int(cle_club(gagnant) == cle_club(j["club_page"])), "Wikipédia", url)
        coupe = COUPE_DU_PAYS.get(championnat)
        gagnant, url = vainqueur(coupe) if coupe else (None, None)
        if gagnant:
            ajouter(j["joueur"], "coupe_nat", int(cle_club(gagnant) == cle_club(j["club_page"])), "Wikipédia", url)

    # Prestige : podiums au Ballon d'or avant 2026
    histo = historique()
    for j in liste:
        podiums = [h for h in histo if h["rang"] <= 3 and meme_joueur(j["joueur"], h["joueur"])]
        points = sum(2 if h["rang"] == 1 else 1 for h in podiums)
        detail = ", ".join(f"{h['annee']} : {h['rang']}e" for h in podiums)
        ajouter(j["joueur"], "podiums_points", points, "Wikipédia (historique.csv)",
                URL_HISTORIQUE, detail)

    # FBref, si les fichiers ont été déposés
    trouves_fbref, prefixes_deposes = set(), set()
    for fichier, prefixe in FICHIERS_FBREF.items():
        chemin = BRUT / "fbref" / fichier
        if not chemin.exists():
            continue
        lignes = lire_fbref(chemin)
        prefixes_deposes.add(prefixe)
        for j in liste:
            # À la Coupe du monde, la colonne « Squad » est la sélection : pas de filtre par club.
            trouves = lignes_fbref_du_joueur(j["joueur"], None if prefixe == "cdm" else j["club"], lignes)
            if not trouves:
                continue
            trouves_fbref.add((prefixe, j["joueur"]))
            for donnee in ("buts", "passes", "minutes"):
                if prefixe == "cdm" and donnee == "buts":
                    continue  # déjà lus dans openfootball (les deux sources concordent)
                total = sum(int(l[donnee] or 0) for l in trouves)
                ajouter(j["joueur"], f"{prefixe}_{donnee}", total, f"FBref ({fichier})", URL_FBREF[fichier])

    # Buts dans les autres compétitions de club (coupes, supercoupes...), pages de saison Wikipédia.
    # Le championnat et la LDC de ces pages servent de contrôle avec FBref.
    ecarts_saisons, saisons_manquantes = [], []
    lus = {(v["joueur"], v["donnee"]): v["valeur"] for v in valeurs}
    for j in liste:
        r = buts_saison_club(j["joueur"], j["club"])
        if r is None:
            saisons_manquantes.append(j["joueur"])
            continue
        ajouter(j["joueur"], "autres_buts", r["autres"], "Wikipédia", r["url"], r["detail"])
        for cle, donnee in (("championnat", "champ_buts"), ("ldc", "ldc_buts")):
            if "absent" not in r["detail"] and lus.get((j["joueur"], donnee), 0) != r[cle]:
                ecarts_saisons.append(f"{j['joueur']} : {donnee} FBref {lus.get((j['joueur'], donnee))}, "
                                      f"Wikipédia {r[cle]}")

    # Cotes
    cotes = []
    poly = lire_json(BRUT / "cotes" / "polymarket.json")[0]["markets"]
    for m in poly:
        if m.get("closed") or "outcomePrices" not in m:
            continue
        prix_oui = float(json.loads(m["outcomePrices"])[0])
        cotes.append({"joueur": m["groupItemTitle"], "source": "Polymarket (prix moyen)", "probabilite": prix_oui,
                      "horodatage": m["updatedAt"][:16].replace("T", " ") + " UTC", "url": URL_POLYMARKET})
    for m in lire_json(BRUT / "cotes" / "kalshi.json")["markets"]:
        if m.get("status") != "active":
            continue
        # Kalshi ne date pas le dernier prix : on note l'heure du téléchargement.
        cotes.append({"joueur": m["yes_sub_title"], "source": "Kalshi (dernier prix échangé)",
                      "probabilite": float(m["last_price_dollars"]),
                      "horodatage": date_telechargement("cotes/kalshi.json"), "url": URL_KALSHI})
    for c in cotes:  # rattacher les noms des marchés à ceux de Wikipédia ; les non-nommés sont écartés
        c["joueur"] = next((j["joueur"] for j in liste if meme_joueur(j["joueur"], c["joueur"])), None)
    cotes = [c for c in cotes if c["joueur"]]

    def stade_de(joueur, prefixe):
        """Parcours dans la compétition (ABS = équipe absente, rien à chercher dans FBref)."""
        return next((v["valeur"] for v in valeurs if v["joueur"] == joueur and v["donnee"] == f"{prefixe}_stade"), None)

    # Écriture
    ecrire("nommes_2026.csv", [{k: j[k] for k in ("joueur", "nation", "poste", "club", "source")} for j in liste])
    ecrire("valeurs_2026.csv", valeurs)
    ecrire("historique.csv", histo)
    ecrire("cotes_2026.csv", cotes)
    (SORTIE / "controles.json").write_text(json.dumps({
        "nommes": len(liste),
        "fbref_deposes": sorted(f for f in FICHIERS_FBREF if (BRUT / "fbref" / f).exists()),
        # Joueurs absents de tous les fichiers déposés pour une compétition (ex. aucun fichier
        # de championnat ne contient ce nom) : à vérifier, l'orthographe peut différer.
        "fbref_joueurs_non_trouves": {p: [j["joueur"] for j in liste if (p, j["joueur"]) not in trouves_fbref
                                          and stade_de(j["joueur"], p) != "ABS"]
                                      for p in sorted(prefixes_deposes)},
        "saisons_clubs_manquantes": saisons_manquantes,
        "saisons_clubs_ecarts_avec_fbref": ecarts_saisons,
        "editions_historique": sorted({h["annee"] for h in histo}),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(liste)} nommés, {len(valeurs)} valeurs sourcées, {len(histo)} lignes d'historique, {len(cotes)} cotes")


def ecrire(nom, lignes):
    with open(SORTIE / nom, "w", newline="", encoding="utf-8") as f:
        ecrivain = csv.DictWriter(f, fieldnames=list(lignes[0]))
        ecrivain.writeheader()
        ecrivain.writerows(lignes)


if __name__ == "__main__":
    main()
