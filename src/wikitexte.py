"""Lecture des tableaux et des infobox dans le texte source (wikitext) des pages Wikipédia."""

import json
import re
import unicodedata
import urllib.parse
from pathlib import Path


def sans_accents(texte):
    """« Mbappé » -> « mbappe », pour comparer des noms écrits différemment."""
    decompose = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c)).lower().strip()


def lire_page(chemin):
    """Renvoie (titre, wikitext) d'un fichier téléchargé par collecte.py."""
    donnees = json.loads(Path(chemin).read_text(encoding="utf-8"))["parse"]
    return donnees["title"], donnees["wikitext"]


def url_page(titre):
    return "https://en.wikipedia.org/wiki/" + urllib.parse.quote(titre.replace(" ", "_"), safe="()_,'")


def _decouper(texte, separateur):
    """Découpe sur un séparateur, sauf à l'intérieur de [[...]] et {{...}}."""
    morceaux, profondeur, courant, i = [], 0, "", 0
    while i < len(texte):
        deux = texte[i:i + 2]
        if deux in ("[[", "{{"):
            profondeur += 1
            courant += deux
            i += 2
            continue
        if deux in ("]]", "}}"):
            profondeur = max(0, profondeur - 1)
            courant += deux
            i += 2
            continue
        if profondeur == 0 and texte.startswith(separateur, i):
            morceaux.append(courant)
            courant = ""
            i += len(separateur)
            continue
        courant += texte[i]
        i += 1
    morceaux.append(courant)
    return morceaux


def _sans_attributs(cellule):
    """« align="left"|[[Kane]] » -> « [[Kane]] »."""
    parties = _decouper(cellule, "|")
    if len(parties) > 1 and "=" in parties[0] and "[[" not in parties[0] and "{{" not in parties[0]:
        return "|".join(parties[1:]).strip()
    return cellule.strip()


def tableaux(wikitext):
    """Renvoie la liste des tableaux de la page : [(entêtes, lignes)], chaque ligne = liste de cellules brutes.

    Les lignes faites uniquement de cellules d'entête (« ! ») placées en haut du tableau
    forment les entêtes ; les suivantes sont des lignes de données.
    """
    resultat = []
    for bloc in re.findall(r"\{\|.*?\n\|\}", wikitext, flags=re.S):
        rangees, courante, entete_seule = [], [], True
        for ligne in bloc.split("\n")[1:] + ["|-"]:
            ligne = ligne.strip()
            if ligne.startswith("|-") or ligne.startswith("|}"):
                if courante:
                    rangees.append((courante, entete_seule))
                courante, entete_seule = [], True
            elif ligne.startswith("|+") or not ligne:
                continue
            elif ligne[0] in "!|":
                sep = "!!" if ligne[0] == "!" else "||"
                courante += [_sans_attributs(c) for c in _decouper(ligne[1:], sep)]
                entete_seule = entete_seule and ligne[0] == "!"
            elif courante:
                courante[-1] += "\n" + ligne
        entetes, lignes = [], []
        for cellules, entete in rangees:
            if entete and not lignes:
                entetes += [nettoyer(c) for c in cellules]
            else:
                lignes.append(cellules)
        resultat.append((entetes, lignes))
    return resultat


def premier_lien(cellule):
    """Texte affiché du premier lien [[...]] (ou du modèle {{sortname|Prénom|Nom}})."""
    m = re.search(r"(?i)\{\{sortname\|([^|}]+)\|([^|}]+)", cellule)
    if m:
        return f"{m.group(1).strip()} {m.group(2).strip()}"
    for cible, affiche in re.findall(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", cellule):
        if not cible.startswith(("File:", "Image:")):
            return (affiche or cible).strip()
    return None


def nettoyer(cellule):
    """Texte lisible d'une cellule : liens -> texte affiché, modèles et références retirés."""
    t = re.sub(r"<ref[^>]*/>|<ref.*?</ref>", "", cellule, flags=re.S)
    t = re.sub(r"\[\[(?:[^\]|]+\|)?([^\]]+)\]\]", r"\1", t)
    t = re.sub(r"\{\{[^{}]*\}\}", "", t)
    t = re.sub(r"<[^>]+>", " ", t).replace("'''", "").replace("''", "")
    return re.sub(r"\s+", " ", t).strip()


def champ_infobox(wikitext, nom):
    """Valeur brute d'un champ d'infobox, ex. « champions »."""
    m = re.search(r"^\s*\|\s*" + re.escape(nom) + r"\s*=(.*)$", wikitext, flags=re.M)
    return m.group(1).strip() if m else None
