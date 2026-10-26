"""Le modèle : une note sur 100 par joueur, puis une probabilité par softmax.

Deux méthodes, au choix dans config/poids.yaml :
  - « chiffres » : statistiques individuelles de la saison (championnat + LDC réunis),
    performances individuelles à la Coupe du monde, et à part le parcours de la sélection
    et les titres du club ;
  - « criteres » : un critère par compétition (Coupe du monde, club, LDC), qui mélange
    résultats collectifs et individuels.

1. Chaque critère est fait de plusieurs éléments (parcours, buts, titres...).
   Chaque élément est ramené entre 0 et 1.
2. Un élément n'est utilisé que s'il est connu pour les 30 nommés. Sinon il est écarté
   pour tout le monde (aucune valeur n'est estimée), et les autres éléments du critère
   se partagent son poids.
3. Note finale = moyenne pondérée des critères (poids de config/poids.yaml), sur 100.
4. Probabilité = softmax des notes : p = exp(note / T) / somme des exp(note / T).
"""

import math

STADES_TOURNOI = {"V": 1.0, "F": 0.8, "DF": 0.6, "QF": 0.4, "HF": 0.25, "16F": 0.15, "P": 0.05, "ABS": 0.0}
STADES_LDC = {"V": 1.0, "F": 0.8, "DF": 0.6, "QF": 0.4, "HF": 0.25, "P": 0.1, "ABS": 0.0}
PRIX_TOURNOI = {"ballon_or": 1.0, "ballon_argent": 0.7, "soulier_or": 0.5, "ballon_bronze": 0.5,
                "autre": 0.3, "": 0.0}


def plafonner(valeur, plafond):
    """0 -> 0, plafond ou plus -> 1."""
    return max(0.0, min(valeur / plafond, 1.0))


def corriger_niveau(valeurs, correction):
    """Buts et passes de championnat pondérés par le niveau du championnat.

    Coefficient = note Opta du championnat / meilleure note parmi les championnats des nommés.
    Sans correction, les valeurs sont reprises telles quelles. Avec correction, un joueur dont le
    championnat n'a pas de note n'a pas de valeur corrigée (l'élément sera écarté, rien n'est estimé).
    """
    notes = [v["champ_niveau"] for v in valeurs.values() if "champ_niveau" in v]
    meilleure = max(notes) if notes else None
    for v in valeurs.values():
        for d in ("champ_buts", "champ_passes"):
            if d not in v:
                continue
            if not correction:
                v[d + "_corr"] = v[d]
            elif "champ_niveau" in v:
                v[d + "_corr"] = v[d] * v["champ_niveau"] / meilleure


def buts_saison(v):
    return v["champ_buts_corr"] + v["ldc_buts"]


def passes_saison(v):
    return v["champ_passes_corr"] + v["ldc_passes"]


def ga_par_90(v):
    return (buts_saison(v) + passes_saison(v)) * 90 / max(v["champ_minutes"] + v["ldc_minutes"], 1)


# Pour chaque méthode et chaque critère : élément -> (poids dans le critère, données nécessaires, calcul).
# Un joueur absent d'une compétition (ex. club hors LDC) a 0 but, 0 passe et 0 minute dans
# cette compétition : ces valeurs ne sont alors pas « manquantes ».
METHODES = {
    "chiffres": {
        "stats_saison": {
            "buts": (0.40, ["champ_buts_corr", "ldc_buts"], lambda v: plafonner(buts_saison(v), 40)),
            "passes": (0.30, ["champ_passes_corr", "ldc_passes"], lambda v: plafonner(passes_saison(v), 20)),
            "ga_90": (0.30, ["champ_buts_corr", "ldc_buts", "champ_passes_corr", "ldc_passes",
                             "champ_minutes", "ldc_minutes"],
                      lambda v: plafonner(ga_par_90(v), 1.2)),
            # Aucune source réutilisable : toujours écarté, affiché pour mémoire.
            "notes_match": (0.20, ["note_match"], lambda v: v["note_match"]),
        },
        "cdm_individuel": {
            "buts": (0.40, ["cdm_buts"], lambda v: plafonner(v["cdm_buts"], 8)),
            "passes": (0.30, ["cdm_passes"], lambda v: plafonner(v["cdm_passes"], 6)),
            "prix": (0.30, ["cdm_prix"], lambda v: PRIX_TOURNOI[v["cdm_prix"]]),
        },
        "cdm_parcours": {
            "parcours": (1.0, ["cdm_stade"], lambda v: STADES_TOURNOI[v["cdm_stade"]]),
        },
        "titres_club": {
            "titre": (0.40, ["champ_titre"], lambda v: v["champ_titre"]),
            "coupe": (0.15, ["coupe_nat"], lambda v: v["coupe_nat"]),
            "ldc": (0.45, ["ldc_stade"], lambda v: STADES_LDC[v["ldc_stade"]]),
        },
        "prestige": {
            "podiums": (1.0, ["podiums_points"], lambda v: plafonner(v["podiums_points"], 6)),
        },
    },
    "criteres": {
        "coupe_du_monde": {
            "parcours": (0.45, ["cdm_stade"], lambda v: STADES_TOURNOI[v["cdm_stade"]]),
            "buts": (0.20, ["cdm_buts"], lambda v: plafonner(v["cdm_buts"], 8)),
            "passes": (0.15, ["cdm_passes"], lambda v: plafonner(v["cdm_passes"], 6)),
            "prix": (0.20, ["cdm_prix"], lambda v: PRIX_TOURNOI[v["cdm_prix"]]),
        },
        "saison_club": {
            "titre": (0.30, ["champ_titre"], lambda v: v["champ_titre"]),
            "coupe": (0.10, ["coupe_nat"], lambda v: v["coupe_nat"]),
            "buts_passes_90": (0.40, ["champ_buts", "champ_passes", "champ_minutes"],
                               lambda v: plafonner((v["champ_buts"] + v["champ_passes"]) * 90
                                                   / max(v["champ_minutes"], 1), 1.5)),
            "minutes": (0.20, ["champ_minutes"], lambda v: plafonner(v["champ_minutes"], 3000)),
        },
        "ligue_des_champions": {
            "parcours": (0.70, ["ldc_stade"], lambda v: STADES_LDC[v["ldc_stade"]]),
            "buts_passes": (0.30, ["ldc_buts", "ldc_passes"],
                            lambda v: plafonner(v["ldc_buts"] + v["ldc_passes"], 15)),
        },
        "prestige": {
            "podiums": (1.0, ["podiums_points"], lambda v: plafonner(v["podiums_points"], 6)),
        },
    },
}

# Équipe absente d'une compétition : 0 but et 0 passe dans cette compétition.
ZERO_SI_ABSENT = {"cdm": ("cdm_stade", ["cdm_buts", "cdm_passes"]),
                  "ldc": ("ldc_stade", ["ldc_buts", "ldc_passes", "ldc_minutes"])}


def completer_absents(valeurs):
    """Un joueur dont l'équipe n'a pas joué la compétition y a 0 but et 0 passe."""
    for v in valeurs.values():
        for stade, donnees in ZERO_SI_ABSENT.values():
            if v.get(stade) == "ABS":
                for d in donnees:
                    v.setdefault(d, 0)


def elements_disponibles(valeurs, methode):
    """{critère: {élément: poids remis à l'échelle}} pour les éléments connus chez les 30 nommés."""
    dispo = {}
    for critere, elements in METHODES[methode].items():
        gardes = {e: p for e, (p, besoins, _) in elements.items()
                  if all(all(b in v for b in besoins) for v in valeurs.values())}
        total = sum(gardes.values())
        if total > 0:
            dispo[critere] = {e: p / total for e, p in gardes.items()}
    return dispo


def poids_effectifs(poids_config, dispo, methode):
    """Poids des critères utilisables, remis à l'échelle pour totaliser 1."""
    actifs = {c: float(poids_config.get(c, 0)) for c in METHODES[methode] if c in dispo}
    total = sum(actifs.values())
    if total <= 0:
        raise ValueError("Aucun critère utilisable : tous les poids sont à 0 ou toutes les données manquent.")
    return {c: p / total for c, p in actifs.items() if p > 0}


def notes_joueur(v, dispo, methode):
    """{critère: note entre 0 et 1} d'un joueur."""
    return {c: sum(poids * METHODES[methode][c][e][2](v) for e, poids in elements.items())
            for c, elements in dispo.items()}


def note_finale(notes, poids):
    return 100 * sum(p * notes[c] for c, p in poids.items())


def softmax(scores, temperature):
    plus_grand = max(scores)
    exps = [math.exp((s - plus_grand) / temperature) for s in scores]
    total = sum(exps)
    return [e / total for e in exps]
