"""Fabrique la page web (un seul fichier HTML, sans JavaScript) à partir des résultats du modèle."""

from html import escape

# --- Petits textes lisibles pour les codes des fichiers CSV ---------------------

TXT_TOURNOI = {"V": "Vainqueur", "F": "Finaliste", "DF": "Demi-finale", "QF": "Quart de finale",
               "HF": "8e de finale", "16F": "16e de finale", "P": "Phase de poules", "ABS": "Non qualifié"}
TXT_LDC = {"V": "Vainqueur", "F": "Finaliste", "DF": "Demi-finale", "QF": "Quart de finale",
           "HF": "8e de finale", "P": "Phase de ligue/barrages", "ABS": "Pas de LDC"}
TXT_PRIX = {"ballon_or": "Ballon d'or de la CDM", "ballon_argent": "Ballon d'argent de la CDM",
            "ballon_bronze": "Ballon de bronze", "soulier_or": "Soulier d'or de la CDM",
            "autre": "Prix individuel à la CDM", "": ""}
TXT_CRITERE = {"coupe_du_monde": "Coupe du monde 2026", "saison_club": "Saison de club",
               "ligue_des_champions": "Ligue des champions", "notes_match": "Notes de match",
               "prestige": "Prestige et récompenses"}

URL_DEPOT = "https://github.com/badis-ar/ballon-dor-2026"


def pct(p):
    """0.2604 -> « 26,0 % » (format français)."""
    if p < 0.001:
        return "< 0,1 %"
    return f"{p * 100:.1f}".replace(".", ",") + " %"


def nombre(x, decimales=1):
    return f"{x:.{decimales}f}".replace(".", ",")


def raisons(j):
    """Trois lignes qui résument pourquoi un joueur est bien placé."""
    cdm = TXT_TOURNOI[j["tournoi_stade"]]
    if j["tournoi_stade"] != "ABS":
        cdm += f" · {j['tournoi_buts_passes']} buts+passes"
    if j["tournoi_prix"]:
        cdm += f" · {TXT_PRIX[j['tournoi_prix']]}"
    ldc = TXT_LDC[j["ldc_stade"]]
    if j["ldc_stade"] != "ABS":
        ldc += f" · {j['ldc_buts_passes']} buts+passes"
    titres = []
    if j["titre_champ"]:
        titres.append("champion")
    if j["coupe_nat"]:
        titres.append("coupe nationale")
    club = f"{j['buts_champ']} buts, {j['passes_champ']} passes"
    if titres:
        club += " · " + " + ".join(titres)
    return [("CDM", cdm), ("LDC", ldc), ("Championnat", club)]


# --- Les blocs de la page -------------------------------------------------------

def bloc_podium(joueurs):
    cartes = []
    for j in joueurs[:3]:
        lignes = "".join(f"<li><span>{escape(k)}</span> {escape(v)}</li>" for k, v in raisons(j))
        cartes.append(f"""
      <article class="carte rang{j['rang']}">
        <div class="medaille">{j['rang']}</div>
        <h3>{escape(j['joueur'])}</h3>
        <p class="sous">{escape(j['club'])} · {escape(j['nation'])}</p>
        <p class="proba">{pct(j['proba'])}</p>
        <p class="sous">de chances de gagner · note {nombre(j['note'])}/100</p>
        <ul class="raisons">{lignes}</ul>
      </article>""")
    return "".join(cartes)


def bloc_tableau(joueurs):
    p_max = joueurs[0]["proba"]
    lignes = []
    for j in joueurs:
        n = j["notes"]
        largeur = 100 * j["proba"] / p_max
        lignes.append(f"""
        <tr>
          <td class="num">{j['rang']}</td>
          <td><strong>{escape(j['joueur'])}</strong><br><span class="sous">{escape(j['club'])} · {escape(j['nation'])}</span></td>
          <td class="cellule-barre" title="{escape(j['joueur'])} : {pct(j['proba'])}">
            <span class="barre-fond"><span class="barre" style="width:{largeur:.1f}%"></span></span>
            <span class="valeur">{pct(j['proba'])}</span>
          </td>
          <td class="num">{nombre(j['note'])}</td>
          <td class="num detail">{round(100 * n['coupe_du_monde'])}</td>
          <td class="num detail">{round(100 * n['saison_club'])}</td>
          <td class="num detail">{round(100 * n['ligue_des_champions'])}</td>
          <td class="num detail">{round(100 * n['prestige'])}</td>
          <td class="detail"><span class="badge {escape(j['fiabilite'])}" title="{escape(j['commentaire'])}">{escape(j['fiabilite'])}</span></td>
        </tr>""")
    return "".join(lignes)


def bloc_poids(poids_config, poids):
    lignes = []
    p_max = max(poids.values())
    for critere in ["coupe_du_monde", "saison_club", "ligue_des_champions", "notes_match", "prestige"]:
        brut = poids_config.get(critere, 0)
        if critere in poids:
            p = poids[critere]
            barre = f'<span class="barre" style="width:{100 * p / p_max:.1f}%"></span>'
            valeur = pct(p)
            note = f"config : {brut}"
        else:
            barre = ""
            valeur = "0 %"
            note = f"config : {brut} · désactivé, redistribué"
        lignes.append(f"""
        <div class="ligne-poids" title="{TXT_CRITERE[critere]} : {valeur} ({note})">
          <span class="nom-poids">{TXT_CRITERE[critere]}<br><span class="sous">{note}</span></span>
          <span class="barre-fond">{barre}</span>
          <span class="valeur">{valeur}</span>
        </div>""")
    return "".join(lignes)


def bloc_validation(validation):
    lignes = []
    for v in validation:
        ok1 = "✔" if v["top1"] else "✘"
        lignes.append(f"""
        <tr>
          <td class="num">{v['annee']}</td>
          <td>{escape(v['vainqueur'])}</td>
          <td>{escape(v['predit'])} <span class="sous">({pct(v['proba_predit'])})</span></td>
          <td class="num"><span class="{'ok' if v['top1'] else 'ko'}" aria-label="{'retrouvé' if v['top1'] else 'manqué'}">{ok1}</span> {v['rang_du_vainqueur']}<sup>e</sup></td>
        </tr>""")
    return "".join(lignes)


def bloc_cotes(joueurs, cotes):
    """Tableau modèle vs bookmakers. cotes = {(source, date): {joueur: proba implicite}}."""
    colonnes = sorted(cotes, key=lambda cle: cle[1])
    noms = []
    for cle in colonnes:
        for nom in cotes[cle]:
            if nom not in noms:
                noms.append(nom)
    par_nom = {j["joueur"]: j for j in joueurs}
    noms.sort(key=lambda nom: -par_nom[nom]["proba"])
    entete = "".join(f"<th class='num'>{escape(src.split(' (')[0])}<br><span class='sous'>{date[8:10]}/{date[5:7]}</span></th>"
                     for src, date in colonnes)
    lignes = []
    for nom in noms:
        j = par_nom[nom]
        cellules = "".join(f"<td class='num'>{pct(cotes[cle][nom]) if nom in cotes[cle] else '–'}</td>" for cle in colonnes)
        lignes.append(f"<tr><td>{escape(nom)} <span class='sous'>({j['rang']}<sup>e</sup>)</span></td>"
                      f"<td class='num'><strong>{pct(j['proba'])}</strong></td>{cellules}</tr>")
    return f"""
      <table>
        <thead><tr><th>Joueur <span class="sous">(rang modèle)</span></th><th class="num">Modèle</th>{entete}</tr></thead>
        <tbody>{''.join(lignes)}</tbody>
      </table>"""


def bloc_exemple(j, poids):
    """Le calcul détaillé pour le n°1, pour montrer comment on obtient la note."""
    termes = " + ".join(f"{nombre(poids[c] * 100, 1)} % × {nombre(j['notes'][c], 2)}" for c in poids)
    return f"{termes} = <strong>{nombre(j['note'])}/100</strong>"


def bloc_verification(verif):
    if not verif:
        return "Vérification en ligne pas encore effectuée (elle a lieu à chaque passage de la GitHub Action)."
    if verif.get("statut") == "non vérifié":
        return f"Vérification impossible le {escape(verif['date'])} : {escape(verif.get('detail', ''))}"
    texte = (f"{verif['trouves']}/{verif['total']} nommés retrouvés sur la page Wikipédia "
             f"« 2026 Ballon d'Or » ({escape(verif['origine'])}).")
    if verif["manquants"]:
        texte += " À vérifier : " + ", ".join(escape(n) for n in verif["manquants"]) + "."
    return texte


# --- La page complète -----------------------------------------------------------

CSS = """
:root {
  color-scheme: light;
  --fond: #f6f5f2; --surface: #fcfcfb; --bord: #e2e0da;
  --texte: #0b0b0b; --texte-2: #52514e; --texte-3: #75736d;
  --serie: #2a78d6; --piste: #ebe9e4;
  --or: #b8860b; --argent: #8a8f98; --bronze: #a0623a;
  --ok: #1a7f37; --ko: #c62828; --alerte-fond: #fff4e5; --alerte-bord: #eda100;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --fond: #121211; --surface: #1a1a19; --bord: #33322f;
    --texte: #f0efec; --texte-2: #c3c2b7; --texte-3: #9a988f;
    --serie: #3987e5; --piste: #2a2a28;
    --or: #e0b23c; --argent: #b5bac2; --bronze: #cf8a5c;
    --ok: #4cc26a; --ko: #ef6b6b; --alerte-fond: #2e2410; --alerte-bord: #c98500;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --fond: #121211; --surface: #1a1a19; --bord: #33322f;
  --texte: #f0efec; --texte-2: #c3c2b7; --texte-3: #9a988f;
  --serie: #3987e5; --piste: #2a2a28;
  --or: #e0b23c; --argent: #b5bac2; --bronze: #cf8a5c;
  --ok: #4cc26a; --ko: #ef6b6b; --alerte-fond: #2e2410; --alerte-bord: #c98500;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--fond); color: var(--texte);
  font: 16px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
main { max-width: 980px; margin: 0 auto; padding: 0 16px 48px; }
header { padding: 32px 0 8px; }
h1 { font-size: clamp(1.7rem, 5vw, 2.4rem); line-height: 1.15; margin: 0 0 8px; }
h2 { font-size: 1.35rem; margin: 40px 0 12px; }
h3 { margin: 0; font-size: 1.15rem; }
p { margin: 0 0 12px; }
a { color: var(--serie); }
.sous { color: var(--texte-3); font-size: .85rem; }
.chapeau { color: var(--texte-2); font-size: 1.05rem; }
.maj { color: var(--texte-3); font-size: .85rem; }
section > .boite, .boite { background: var(--surface); border: 1px solid var(--bord); border-radius: 12px; padding: 16px; }
.alerte { background: var(--alerte-fond); border: 1px solid var(--alerte-bord); border-radius: 12px; padding: 12px 16px; margin: 16px 0; }
.podium { display: grid; gap: 12px; grid-template-columns: repeat(3, 1fr); align-items: start; }
.carte { background: var(--surface); border: 1px solid var(--bord); border-top: 4px solid var(--bord); border-radius: 12px; padding: 16px; position: relative; }
.carte.rang1 { border-top-color: var(--or); }
.carte.rang2 { border-top-color: var(--argent); }
.carte.rang3 { border-top-color: var(--bronze); }
.medaille { position: absolute; top: 12px; right: 14px; font-weight: 700; color: var(--texte-3); font-size: 1.4rem; }
.carte .proba { font-size: 2.4rem; font-weight: 700; line-height: 1.1; margin: 12px 0 2px; }
.carte.rang1 .proba { font-size: 3rem; }
.raisons { list-style: none; padding: 0; margin: 12px 0 0; font-size: .88rem; color: var(--texte-2); }
.raisons li { padding: 4px 0; border-top: 1px solid var(--bord); display: grid; grid-template-columns: 96px 1fr; gap: 6px; }
.raisons span { color: var(--texte-3); }
.defile { overflow-x: auto; background: var(--surface); border: 1px solid var(--bord); border-radius: 12px; }
table { width: 100%; border-collapse: collapse; font-size: .92rem; }
th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--bord); vertical-align: middle; }
th { font-size: .78rem; text-transform: uppercase; letter-spacing: .03em; color: var(--texte-3); font-weight: 600; }
tbody tr:last-child td { border-bottom: 0; }
.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.cellule-barre { min-width: 150px; white-space: nowrap; }
.barre-fond { display: inline-block; width: 90px; height: 12px; background: var(--piste); border-radius: 0 4px 4px 0; vertical-align: middle; }
.barre { display: block; height: 100%; background: var(--serie); border-radius: 0 4px 4px 0; }
.valeur { display: inline-block; min-width: 62px; text-align: right; font-variant-numeric: tabular-nums; }
.badge { font-size: .75rem; padding: 2px 8px; border-radius: 999px; border: 1px solid var(--bord); color: var(--texte-2); white-space: nowrap; }
.badge.confirmé { border-color: var(--ok); }
.badge.estimation { border-style: dashed; }
.ligne-poids { display: grid; grid-template-columns: minmax(130px, 210px) 1fr 70px; gap: 12px; align-items: center; padding: 8px 0; }
.ligne-poids + .ligne-poids { border-top: 1px solid var(--bord); }
.ligne-poids .barre-fond { width: 100%; height: 20px; }
.tuiles { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 12px; }
.tuile { background: var(--surface); border: 1px solid var(--bord); border-radius: 12px; padding: 14px 16px; }
.tuile b { display: block; font-size: 2rem; line-height: 1.1; }
.ok { color: var(--ok); font-weight: 700; }
.ko { color: var(--ko); font-weight: 700; }
ol.etapes { padding-left: 22px; }
ol.etapes li { margin-bottom: 10px; }
code { background: var(--piste); padding: 1px 5px; border-radius: 4px; font-size: .88em; }
footer { color: var(--texte-3); font-size: .85rem; border-top: 1px solid var(--bord); margin-top: 48px; padding-top: 16px; }
@media (max-width: 720px) {
  .podium, .tuiles { grid-template-columns: 1fr; }
  .detail { display: none; }
  .barre-fond { width: 60px; }
  .cellule-barre { min-width: 0; }
  .ligne-poids { grid-template-columns: 1fr 64px; }
  .ligne-poids .barre-fond { grid-column: 1 / -1; grid-row: 2; }
}
"""


def generer(joueurs, poids_config, poids, temperature, validation, exploration,
            cotes, verification, date_maj, date_collecte):
    """Assemble toute la page et renvoie le texte HTML."""
    n1 = joueurs[0]
    nb = len(validation)
    top1 = sum(v["top1"] for v in validation)
    top3 = sum(v["top3"] for v in validation)
    premiere, derniere = validation[0]["annee"], validation[-1]["annee"]

    alerte = ""
    poids_cdm = poids.get("coupe_du_monde", 0)
    if any(p > poids_cdm for c, p in poids.items() if c != "coupe_du_monde"):
        alerte = ("<div class='alerte'><strong>Attention :</strong> avec les poids actuels de "
                  "<code>config/poids.yaml</code>, la Coupe du monde n'est plus le critère le plus lourd.</div>")

    expl = exploration["poids"]
    expl_txt = ", ".join(f"{TXT_CRITERE[c]} {pct(p)}" for c, p in expl.items())

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pronostic Ballon d'or 2026</title>
<meta name="description" content="Probabilités de victoire des 30 nommés au Ballon d'or 2026, calculées par un modèle simple et transparent.">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚽</text></svg>">
<style>{CSS}</style>
</head>
<body>
<main>
  <header>
    <h1>Ballon d'or 2026 : qui va gagner ?</h1>
    <p class="chapeau">Probabilités de victoire des 30 nommés, calculées par un modèle simple et transparent.
      Cérémonie le 26 octobre 2026 au London Palladium (Londres).</p>
    <p class="maj">Page mise à jour le {escape(date_maj)} · Données collectées le {escape(date_collecte)}</p>
  </header>
  {alerte}

  <section aria-labelledby="t-podium">
    <h2 id="t-podium">Le podium prédit</h2>
    <div class="podium">{bloc_podium(joueurs)}</div>
  </section>

  <section aria-labelledby="t-classement">
    <h2 id="t-classement">Classement complet des 30 nommés</h2>
    <p class="sous">Notes de 0 à 100 par critère. Sur téléphone, seules la probabilité et la note finale sont affichées.
      La colonne « fiabilité » indique la qualité des données du joueur (passez la souris pour le détail).</p>
    <div class="defile">
      <table>
        <thead><tr>
          <th class="num">#</th><th>Joueur</th><th>Probabilité</th><th class="num">Note</th>
          <th class="num detail">CDM</th><th class="num detail">Club</th><th class="num detail">LDC</th>
          <th class="num detail">Prestige</th><th class="detail">Fiabilité</th>
        </tr></thead>
        <tbody>{bloc_tableau(joueurs)}</tbody>
      </table>
    </div>
  </section>

  <section aria-labelledby="t-poids">
    <h2 id="t-poids">Le poids de chaque critère</h2>
    <div class="boite">{bloc_poids(poids_config, poids)}</div>
    <p class="sous" style="margin-top:8px">Poids lus dans <a href="{URL_DEPOT}/blob/main/config/poids.yaml"><code>config/poids.yaml</code></a>.
      Les notes de match n'ont pas de source gratuite et fiable : leur poids est réparti entre les autres critères,
      au prorata.</p>
  </section>

  <section aria-labelledby="t-calcul">
    <h2 id="t-calcul">Comment le calcul fonctionne (version débutant)</h2>
    <div class="boite">
      <ol class="etapes">
        <li><strong>On note chaque critère de 0 à 1.</strong> Exemple pour la Coupe du monde : la moitié de la note vient
          du parcours de l'équipe (vainqueur = 1, finaliste = 0,8, demi-finale = 0,6…), 30 % des buts + passes
          (8 ou plus = note maximale) et 20 % des prix individuels (Ballon d'or de la CDM = 1…).
          Même principe pour la saison de club (buts + passes par 90 minutes, minutes jouées, titres),
          la Ligue des champions (parcours, buts + passes) et le prestige (podiums passés au Ballon d'or, Soulier d'or européen…).</li>
        <li><strong>On fait une moyenne pondérée.</strong> Chaque note est multipliée par le poids du critère, puis on additionne.
          Pour {escape(n1['joueur'])} : {bloc_exemple(n1, poids)}.</li>
        <li><strong>On transforme les notes en probabilités avec la « softmax ».</strong> Chaque note devient
          e<sup>note / T</sup>, puis on divise par la somme de tous les joueurs, pour que le total fasse 100 %.
          Un écart de {nombre(temperature, 0)} points de note multiplie environ les chances par 2,7.</li>
        <li><strong>On choisit T grâce à l'historique.</strong> T = {nombre(temperature, 1)} est la valeur qui donnait
          les probabilités les plus réalistes aux vrais vainqueurs de {premiere} à {derniere}.</li>
      </ol>
    </div>
  </section>

  <section aria-labelledby="t-validation">
    <h2 id="t-validation">Le modèle aurait-il trouvé les anciens vainqueurs ?</h2>
    <p>On rejoue le modèle (mêmes poids, mêmes règles) sur chaque édition de {premiere} à {derniere}
      ({nb} éditions, pas de Ballon d'or en 2020), en comparant les 5 premiers du vote réel.</p>
    <div class="tuiles">
      <div class="tuile"><b>{top1}/{nb}</b>vainqueurs classés 1ers par le modèle</div>
      <div class="tuile"><b>{top3}/{nb}</b>vainqueurs dans le top 3 du modèle</div>
      <div class="tuile"><b>{round(nb / 5)}/{nb}</b>et {round(3 * nb / 5)}/{nb} : ce qu'on obtiendrait au hasard</div>
    </div>
    <div class="defile">
      <table>
        <thead><tr><th class="num">Année</th><th>Vrai vainqueur</th><th>1er selon le modèle</th><th class="num">Rang du vainqueur</th></tr></thead>
        <tbody>{bloc_validation(validation)}</tbody>
      </table>
    </div>
    <p class="sous" style="margin-top:8px">Attention : c'est un test plus facile que 2026, car il n'y a que 5 candidats par an au lieu de 30.</p>
    <div class="boite" style="margin-top:12px">
      <strong>Et avec d'autres poids ?</strong> En testant toutes les combinaisons par pas de 5 %
      (avec la règle : la CDM jamais sous le poids de la config, et toujours le critère le plus lourd),
      la meilleure trouvée sur l'historique est : {expl_txt}. Elle retrouve
      {exploration['top1']}/{nb} vainqueurs (top 3 : {exploration['top3']}/{nb}).
      <span class="sous">Elle n'est pas appliquée automatiquement : sur si peu d'années, la meilleure combinaison
      du passé n'est pas forcément la meilleure pour l'avenir (c'est le « surapprentissage »). À vous de décider
      dans <code>config/poids.yaml</code>.</span>
    </div>
  </section>

  <section aria-labelledby="t-cotes">
    <h2 id="t-cotes">Comparaison avec les bookmakers</h2>
    <p>Probabilités « implicites » des cotes (cote 5/4 → 1 / 2,25 = 44 %). Les bookmakers prennent une marge,
      donc leurs chiffres totalisent plus de 100 %.</p>
    <div class="defile">{bloc_cotes(joueurs, cotes)}</div>
  </section>

  <section aria-labelledby="t-limites">
    <h2 id="t-limites">Les limites du modèle</h2>
    <div class="boite">
      <ul>
        <li><strong>Des données imparfaites.</strong> Beaucoup de stats 2025-26 sont des « photos » prises un peu avant la fin de la saison,
          et celles de 7 défenseurs sont estimées. Les minutes de l'historique sont approximatives.
          Détails dans <a href="{URL_DEPOT}/blob/main/data/SOURCES.md">data/SOURCES.md</a>.</li>
        <li><strong>Le vote reste humain.</strong> 100 journalistes votent : réputation, récit de la saison, moments marquants
          (le but en finale de Ferran Torres, par exemple) ne se mesurent pas bien avec des chiffres.</li>
        <li><strong>Les défenseurs et milieux défensifs sont désavantagés</strong> : on mesure surtout les buts et les passes.</li>
        <li><strong>Pas de notes de match</strong> : aucune source gratuite et réutilisable.</li>
        <li><strong>La CAN 2025 n'est pas comptée</strong>, seule la Coupe du monde l'est.</li>
        <li><strong>Peu d'historique</strong> : {nb} éditions, c'est peu pour régler un modèle.</li>
        <li><strong>Les barèmes</strong> (vainqueur = 1, finaliste = 0,8…) sont des choix raisonnables, pas des vérités.</li>
      </ul>
    </div>
  </section>

  <section aria-labelledby="t-sources">
    <h2 id="t-sources">Données et vérification</h2>
    <p>{bloc_verification(verification)}</p>
    <p>Sources, hypothèses et valeurs estimées : <a href="{URL_DEPOT}/blob/main/data/SOURCES.md">data/SOURCES.md</a>.
      Résultats bruts : <a href="resultats.csv">resultats.csv</a>. Code : <a href="{URL_DEPOT}">dépôt GitHub</a>.</p>
  </section>

  <footer>
    Page générée automatiquement par GitHub Actions le {escape(date_maj)}. Projet personnel, sans lien avec France Football.
    Pour changer les poids : modifiez <code>config/poids.yaml</code> sur GitHub, la page se met à jour en 1 à 2 minutes.
  </footer>
</main>
</body>
</html>
"""
