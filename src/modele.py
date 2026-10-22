"""Le modèle : transforme les stats d'un joueur en note sur 100, puis en probabilité.

Le principe en 3 étapes :
  1. Chaque critère (CDM, club, LDC, prestige) est ramené à une note entre 0 et 1.
  2. On fait une moyenne pondérée de ces notes (poids lus dans config/poids.yaml) -> note sur 100.
  3. On applique la fonction « softmax » pour transformer les notes en probabilités
     qui totalisent 100 %.
"""

import math

# --- Barèmes (hypothèses du modèle) -------------------------------------------

# Parcours en tournoi international : 1 = vainqueur, 0 = absent.
STADES_TOURNOI = {
    "V": 1.0,     # vainqueur
    "F": 0.8,     # finaliste
    "DF": 0.6,    # demi-finale (3e ou 4e)
    "QF": 0.4,    # quart de finale
    "HF": 0.25,   # huitième de finale
    "16F": 0.15,  # seizième de finale (nouveau format à 48 équipes)
    "P": 0.05,    # phase de poules
    "ABS": 0.0,   # absent / non qualifié
}

# Parcours en Ligue des champions.
STADES_LDC = {
    "V": 1.0, "F": 0.8, "DF": 0.6, "QF": 0.4, "HF": 0.25,
    "P": 0.1,     # phase de ligue / barrages
    "ABS": 0.0,   # club absent de la LDC
}

# Prix individuels du tournoi.
PRIX_TOURNOI = {
    "ballon_or": 1.0,       # meilleur joueur du tournoi
    "ballon_argent": 0.7,
    "ballon_bronze": 0.5,
    "soulier_or": 0.5,      # meilleur buteur
    "autre": 0.3,           # meilleur gardien, meilleur jeune, soulier d'argent...
    "": 0.0,
}

# Noms des critères (ceux du fichier config/poids.yaml).
CRITERES = ["coupe_du_monde", "saison_club", "ligue_des_champions", "notes_match", "prestige"]

# Critères pour lesquels on n'a aucune donnée : leur poids est redistribué.
CRITERES_SANS_DONNEES = {"notes_match"}


def plafonner(valeur, plafond):
    """Ramène une valeur entre 0 et 1 : 0 -> 0, plafond (ou plus) -> 1."""
    return max(0.0, min(valeur / plafond, 1.0))


# --- Étape 1 : une note entre 0 et 1 par critère --------------------------------

def note_coupe_du_monde(j):
    """Parcours de l'équipe (50 %), buts + passes (30 %, 8 = note max), prix (20 %)."""
    return (0.5 * STADES_TOURNOI[j["tournoi_stade"]]
            + 0.3 * plafonner(j["tournoi_buts_passes"], 8)
            + 0.2 * PRIX_TOURNOI[j["tournoi_prix"]])


def note_saison_club(j):
    """Buts + passes par 90 min (40 %), minutes jouées (20 %), titres nationaux (40 %)."""
    par_90 = (j["buts_champ"] + j["passes_champ"]) * 90 / max(j["minutes_champ"], 1)
    titres = 0.7 * j["titre_champ"] + 0.3 * j["coupe_nat"]
    return (0.4 * plafonner(par_90, 1.5)
            + 0.2 * plafonner(j["minutes_champ"], 3000)
            + 0.4 * titres)


def note_ligue_des_champions(j):
    """Parcours du club (70 %), buts + passes en LDC (30 %, 15 = note max)."""
    return 0.7 * STADES_LDC[j["ldc_stade"]] + 0.3 * plafonner(j["ldc_buts_passes"], 15)


def note_prestige(j, points_podiums):
    """Podiums passés au Ballon d'or (50 %) + grands prix individuels de la saison (50 %).

    points_podiums : 2 points par Ballon d'or gagné, 1 point par 2e ou 3e place (années précédentes).
    prix_saison : Soulier d'or européen, meilleur joueur UEFA / de la saison de LDC.
    """
    return 0.5 * plafonner(points_podiums, 6) + 0.5 * plafonner(j["prix_saison"], 2)


def notes_criteres(j, points_podiums):
    """Renvoie un dictionnaire {critère: note entre 0 et 1} pour un joueur."""
    return {
        "coupe_du_monde": note_coupe_du_monde(j),
        "saison_club": note_saison_club(j),
        "ligue_des_champions": note_ligue_des_champions(j),
        "notes_match": 0.0,  # pas de données (voir CRITERES_SANS_DONNEES)
        "prestige": note_prestige(j, points_podiums),
    }


# --- Étape 2 : poids et note finale --------------------------------------------

def poids_effectifs(poids_config):
    """Retire les critères sans données et remet les poids à l'échelle pour totaliser 1.

    Exemple avec la config par défaut : notes_match (10) est retiré, il reste 90 points,
    donc la CDM passe de 35/100 à 35/90 = 38,9 %.
    """
    actifs = {c: float(poids_config.get(c, 0)) for c in CRITERES if c not in CRITERES_SANS_DONNEES}
    total = sum(actifs.values())
    if total <= 0:
        raise ValueError("Tous les poids sont à 0 dans config/poids.yaml")
    return {c: p / total for c, p in actifs.items()}


def note_finale(notes, poids):
    """Moyenne pondérée des notes des critères, sur 100."""
    return 100 * sum(poids[c] * notes[c] for c in poids)


# --- Étape 3 : softmax ----------------------------------------------------------

def softmax(scores, temperature):
    """Transforme des notes en probabilités qui totalisent 1.

    p(joueur) = exp(note / T) / somme des exp(note / T)
    Plus la « température » T est petite, plus le favori écrase les autres.
    """
    plus_grand = max(scores)  # on soustrait le max pour éviter des nombres énormes
    exps = [math.exp((s - plus_grand) / temperature) for s in scores]
    total = sum(exps)
    return [e / total for e in exps]


# --- Historique : prestige, validation, calibrage -------------------------------

def points_podiums_avant(nom, annee, podiums):
    """Points de prestige d'un joueur avant une année donnée (podiums = liste de (année, rang, nom))."""
    points = 0
    for a, rang, joueur in podiums:
        if joueur == nom and a < annee:
            points += 2 if rang == 1 else (1 if rang <= 3 else 0)
    return points


def notes_par_annee(historique, podiums, poids):
    """Calcule la note finale de chaque joueur de l'historique, regroupée par année.

    Renvoie {année: [(nom, rang_réel, note), ...]}.
    """
    par_annee = {}
    for j in historique:
        pts = points_podiums_avant(j["joueur"], j["annee"], podiums)
        note = note_finale(notes_criteres(j, pts), poids)
        par_annee.setdefault(j["annee"], []).append((j["joueur"], j["rang"], note))
    return par_annee


def log_vraisemblance(par_annee, temperature):
    """Mesure à quel point le modèle donnait une forte probabilité aux vrais vainqueurs (plus haut = mieux)."""
    total = 0.0
    for joueurs in par_annee.values():
        probas = softmax([note for _, _, note in joueurs], temperature)
        for (nom, rang, _), p in zip(joueurs, probas):
            if rang == 1:
                total += math.log(p)
    return total


def calibrer_temperature(par_annee):
    """Cherche la température T (entre 0,5 et 30) qui colle le mieux à l'historique."""
    candidates = [0.5 * k for k in range(1, 61)]
    return max(candidates, key=lambda t: log_vraisemblance(par_annee, t))


def valider(par_annee, temperature):
    """Rejoue chaque année : le vrai vainqueur était-il classé 1er ? dans le top 3 ?"""
    lignes = []
    for annee in sorted(par_annee):
        joueurs = sorted(par_annee[annee], key=lambda x: -x[2])  # du meilleur au moins bon
        probas = softmax([note for _, _, note in joueurs], temperature)
        rang_predit_du_vainqueur = next(i + 1 for i, j in enumerate(joueurs) if j[1] == 1)
        vainqueur = next(j for j in joueurs if j[1] == 1)
        lignes.append({
            "annee": annee,
            "vainqueur": vainqueur[0],
            "predit": joueurs[0][0],
            "proba_predit": probas[0],
            "rang_du_vainqueur": rang_predit_du_vainqueur,
            "top1": rang_predit_du_vainqueur == 1,
            "top3": rang_predit_du_vainqueur <= 3,
        })
    return lignes


def explorer_poids(historique, podiums, poids_cdm_minimum, pas=5):
    """Teste d'autres combinaisons de poids sur l'historique (à titre indicatif).

    Contraintes : le poids de la CDM ne descend JAMAIS sous celui de la config,
    et la CDM reste le critère le plus lourd (aucun autre poids ne la dépasse).
    Renvoie la meilleure combinaison trouvée (elle n'est pas appliquée automatiquement).
    """
    cdm_min = math.ceil(poids_cdm_minimum * 100 / pas) * pas
    meilleur = None
    for cdm in range(cdm_min, 101, pas):
        for club in range(0, 101 - cdm, pas):
            for ldc in range(0, 101 - cdm - club, pas):
                prestige = 100 - cdm - club - ldc
                if max(club, ldc, prestige) > cdm:
                    continue  # la CDM doit rester le critère le plus lourd
                poids = {"coupe_du_monde": cdm / 100, "saison_club": club / 100,
                         "ligue_des_champions": ldc / 100, "prestige": prestige / 100}
                par_annee = notes_par_annee(historique, podiums, poids)
                t = calibrer_temperature(par_annee)
                lignes = valider(par_annee, t)
                cle = (sum(l["top1"] for l in lignes), sum(l["top3"] for l in lignes),
                       log_vraisemblance(par_annee, t))
                if meilleur is None or cle > meilleur[0]:
                    meilleur = (cle, poids)
    (top1, top3, _), poids = meilleur
    return {"poids": poids, "top1": top1, "top3": top3}
