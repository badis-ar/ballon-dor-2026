"""Fabrique la page web (un seul fichier HTML, sans JavaScript)."""

from html import escape

URL_DEPOT = "https://github.com/badis-ar/ballon-dor-2026"

TXT_STADE = {"V": "Vainqueur", "F": "Finale", "DF": "Demi-finale", "QF": "Quart", "HF": "8e",
             "16F": "16e", "P": "Phase de groupes", "ABS": "Absent"}
TXT_STADE_LDC = dict(TXT_STADE, P="Phase de ligue")
TXT_PRIX = {"ballon_or": "Ballon d'or", "ballon_argent": "Ballon d'argent", "ballon_bronze": "Ballon de bronze",
            "soulier_or": "Soulier d'or", "autre": "Autre prix", "": ""}
TXT_METHODE = {"chiffres": "statistiques individuelles", "criteres": "par compétition"}
TXT_CRITERE = {"coupe_du_monde": "Coupe du monde 2026", "saison_club": "Saison de club 2025-26",
               "ligue_des_champions": "Ligue des champions 2025-26", "prestige": "Palmarès au Ballon d'or",
               "stats_saison": "Statistiques de la saison 2025-26", "cdm_individuel": "Coupe du monde : performances",
               "cdm_parcours": "Coupe du monde : parcours de la sélection", "titres_club": "Titres du club 2025-26"}
TXT_ELEMENT = {
    "stats_saison": {"buts": "buts (championnat + LDC)", "passes": "passes décisives (championnat + LDC)",
                     "ga_90": "buts et passes par 90 minutes", "notes_match": "notes de match"},
    "cdm_individuel": {"buts": "buts", "passes": "passes décisives", "prix": "prix individuels du tournoi"},
    "cdm_parcours": {"parcours": "dernier tour atteint"},
    "titres_club": {"titre": "titre de champion", "coupe": "coupe nationale", "ldc": "parcours en LDC"},
    "coupe_du_monde": {"parcours": "parcours de la sélection", "buts": "buts", "passes": "passes décisives",
                       "prix": "prix individuels du tournoi"},
    "saison_club": {"titre": "titre de champion", "coupe": "coupe nationale",
                    "buts_passes_90": "buts et passes par 90 minutes", "minutes": "minutes jouées"},
    "ligue_des_champions": {"parcours": "parcours du club", "buts_passes": "buts et passes"},
    "prestige": {"podiums": "podiums des éditions précédentes"},
}

# Colonnes du tableau des données : (donnée, titre de colonne, groupe, mise en forme)
COLONNES = [
    ("cdm_stade", "Parcours", "Coupe du monde", lambda v: TXT_STADE[v]),
    ("cdm_buts", "Buts", "Coupe du monde", str),
    ("cdm_passes", "Passes", "Coupe du monde", str),
    ("cdm_prix", "Prix", "Coupe du monde", lambda v: TXT_PRIX[v] if v else "aucun"),
    ("ldc_stade", "Parcours", "Ligue des champions", lambda v: TXT_STADE_LDC[v]),
    ("ldc_buts", "Buts", "Ligue des champions", str),
    ("ldc_passes", "Passes", "Ligue des champions", str),
    ("ldc_minutes", "Minutes", "Ligue des champions", lambda v: f"{v:,}".replace(",", "\u202f")),
    ("champ_titre", "Champion", "Championnat", lambda v: "oui" if v else "non"),
    ("coupe_nat", "Coupe", "Championnat", lambda v: "oui" if v else "non"),
    ("champ_buts", "Buts", "Championnat", str),
    ("champ_passes", "Passes", "Championnat", str),
    ("champ_minutes", "Minutes", "Championnat", lambda v: f"{v:,}".replace(",", " ")),
    ("podiums_points", "Points", "Ballon d'or", str),
]


def pct(p):
    if p < 0.001:
        return "< 0,1 %"
    return f"{p * 100:.1f}".replace(".", ",") + " %"


def cellule(joueur, donnee, mise_en_forme, valeurs, sources):
    v = valeurs[joueur].get(donnee)
    if v is None:
        return '<td class="vide"></td>'
    texte = escape(mise_en_forme(v))
    src = sources[joueur].get(donnee)
    if not src:  # 0 déduit d'une absence de la compétition
        return f'<td title="Équipe absente de la compétition">{texte}</td>'
    titre = f"Source : {src['source']}" + (f" ({src['detail']})" if src["detail"] else "")
    return f'<td><a href="{escape(src["url"])}" title="{escape(titre)}">{texte}</a></td>'


def bloc_classement(joueurs, cotes, autre):
    sources_cotes = sorted(cotes)
    p_max = joueurs[0]["proba"]
    entete = "".join(f'<th class="num">{escape(s.split(" (")[0])}</th>' for s in sources_cotes)
    lignes = []
    for rang, j in enumerate(joueurs, start=1):
        cells = []
        for s in sources_cotes:
            c = cotes[s].get(j["joueur"])
            cells.append(f'<td class="num"><a href="{escape(c["url"])}" title="{escape(s)}, {escape(c["horodatage"])}">'
                         f'{pct(float(c["probabilite"]))}</a></td>' if c else '<td class="num vide"></td>')
        lignes.append(f"""
        <tr>
          <td class="num rang">{rang}</td>
          <td><span class="nom">{escape(j['joueur'])}</span><span class="sous">{escape(j['club'])} · {escape(j['nation'])}</span></td>
          <td class="barre-cellule"><span class="piste"><span class="barre" style="width:{100 * j['proba'] / p_max:.1f}%"></span></span>
            <span class="num valeur">{pct(j['proba'])}</span></td>
          <td class="num autre">{pct(j['proba_autre'])}</td>
          {''.join(cells)}
        </tr>""")
    return f"""
    <table class="classement">
      <thead><tr><th class="num">#</th><th>Joueur</th><th>Modèle</th>
        <th class="num" title="Même données, méthode {TXT_METHODE[autre]}">Autre méthode</th>{entete}</tr></thead>
      <tbody>{''.join(lignes)}</tbody>
    </table>"""


def bloc_donnees(joueurs, valeurs, sources):
    groupes = []
    for _, _, groupe, _ in COLONNES:
        if not groupes or groupes[-1][0] != groupe:
            groupes.append([groupe, 0])
        groupes[-1][1] += 1
    ligne_groupes = "".join(f'<th colspan="{n}" class="groupe">{escape(g)}</th>' for g, n in groupes)
    ligne_titres = "".join(f"<th>{escape(t)}</th>" for _, t, _, _ in COLONNES)
    lignes = []
    for j in joueurs:
        cells = "".join(cellule(j["joueur"], d, f, valeurs, sources) for d, _, _, f in COLONNES)
        lignes.append(f'<tr><th scope="row">{escape(j["joueur"])}</th>{cells}</tr>')
    return f"""
    <table class="donnees">
      <thead><tr><th></th>{ligne_groupes}</tr><tr><th>Joueur</th>{ligne_titres}</tr></thead>
      <tbody>{''.join(lignes)}</tbody>
    </table>"""


def bloc_methode(methode, info):
    from modele import METHODES
    elements_methode = METHODES[methode]
    dispo, poids_config, poids = info["dispo"], info["poids_config"], info["poids"]
    lignes = []
    for critere in elements_methode:
        utilises = dispo.get(critere, {})
        ecartes = [e for e in elements_methode[critere] if e not in utilises]
        txt_utilises = ", ".join(f"{TXT_ELEMENT[critere][e]} ({round(100 * p)} %)" for e, p in utilises.items()) or "aucun"
        txt_ecartes = ", ".join(TXT_ELEMENT[critere][e] for e in ecartes) or "aucun"
        applique = pct(poids[critere]) if critere in poids else "0 %"
        lignes.append(f"""
        <tr>
          <th scope="row">{TXT_CRITERE[critere]}</th>
          <td class="num">{poids_config.get(critere, 0)}</td>
          <td class="num">{applique}</td>
          <td>{escape(txt_utilises)}</td>
          <td class="ecarte">{escape(txt_ecartes)}</td>
        </tr>""")
    return f"""
    <table class="methode">
      <thead><tr><th>Critère</th><th class="num">Poids réglé</th><th class="num">Poids appliqué</th>
        <th>Éléments utilisés</th><th>Écartés faute de données</th></tr></thead>
      <tbody>{''.join(lignes)}</tbody>
    </table>"""


def bloc_historique(historique):
    par_annee = {}
    for h in historique:
        par_annee.setdefault(int(h["annee"]), []).append(h)
    lignes = []
    for annee in sorted(par_annee, reverse=True):
        rangs = sorted(par_annee[annee], key=lambda h: int(h["rang"]))
        url = rangs[0]["source"]
        cells = "".join(f'<td>{escape(h["joueur"])} <span class="sous">{escape(h["points"])}</span></td>' for h in rangs)
        cells += "<td></td>" * (5 - len(rangs))
        lignes.append(f'<tr><th scope="row"><a href="{escape(url)}">{annee}</a></th>{cells}</tr>')
    return f"""
    <table class="historique">
      <thead><tr><th>Année</th><th>1er</th><th>2e</th><th>3e</th><th>4e</th><th>5e</th></tr></thead>
      <tbody>{''.join(lignes)}</tbody>
    </table>"""


def bloc_sources(provenance):
    familles = [
        ("Wikipédia", "wikipedia/", "Licence CC BY-SA 4.0",
         "Liste des nommés, prix de la Coupe du monde, champions et vainqueurs de coupe, classements 1996-2025."),
        ("openfootball", "openfootball/", "Domaine public (CC0)",
         "Matchs et buteurs de la Coupe du monde 2026, tableau de la Ligue des champions 2025-26."),
        ("Polymarket", "cotes/polymarket", "API publique",
         "Prix du marché « Ballon d'Or Winner 2026 » (un prix de 0,68 $ correspond à 68 %)."),
        ("Kalshi", "cotes/kalshi", "API publique", "Dernier prix échangé du marché KXBALLONDOR."),
        ("FBref", "fbref/", "Usage personnel, citation obligatoire",
         "Buts, passes décisives et minutes. Fichiers déposés à la main (le site bloque les robots)."),
    ]
    lignes = []
    for nom, prefixe, licence, contenu in familles:
        fichiers = [p for p in provenance if p["fichier"].startswith(prefixe)]
        if fichiers:
            dates = sorted(p["telecharge_le"] for p in fichiers)
            quand = f"{len(fichiers)} fichier{'s' if len(fichiers) > 1 else ''}, {dates[-1][:10]}"
        else:
            quand = "pas encore intégré"
        lignes.append(f"<tr><th scope='row'>{nom}</th><td>{escape(contenu)}</td><td>{licence}</td><td>{quand}</td></tr>")
    return f"""
    <table class="sources">
      <thead><tr><th>Source</th><th>Contenu</th><th>Conditions</th><th>Collecte</th></tr></thead>
      <tbody>{''.join(lignes)}</tbody>
    </table>"""


CSS = """
:root {
  color-scheme: light;
  --fond: #f7f7f5; --surface: #ffffff; --bord: #e3e2de; --texte: #161616; --texte-2: #555450;
  --texte-3: #7a7873; --accent: #1f5fbf; --piste: #ecebe7; --barre: #1f5fbf; --note-fond: #f3f1ea;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --fond: #121212; --surface: #1a1a1a; --bord: #303030; --texte: #ededeb; --texte-2: #bdbcb7;
    --texte-3: #8f8e89; --accent: #7aa7f0; --piste: #2a2a2a; --barre: #5b8fe0; --note-fond: #1f1e1b;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --fond: #121212; --surface: #1a1a1a; --bord: #303030; --texte: #ededeb; --texte-2: #bdbcb7;
  --texte-3: #8f8e89; --accent: #7aa7f0; --piste: #2a2a2a; --barre: #5b8fe0; --note-fond: #1f1e1b;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--fond); color: var(--texte);
  font: 15px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
main { max-width: 1040px; margin: 0 auto; padding: 0 16px 56px; }
header { padding: 40px 0 8px; border-bottom: 1px solid var(--bord); margin-bottom: 8px; }
h1 { font-size: 1.9rem; line-height: 1.2; margin: 0 0 6px; font-weight: 650; letter-spacing: -0.01em; }
h2 { font-size: 1.15rem; margin: 40px 0 6px; font-weight: 650; }
h3 { font-size: 1rem; margin: 22px 0 4px; font-weight: 600; }
.autre { color: var(--texte-2); }
p { margin: 0 0 10px; max-width: 72ch; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.sous { color: var(--texte-3); font-size: .85em; }
.intro { color: var(--texte-2); }
.note { background: var(--note-fond); border-left: 3px solid var(--texte-3); padding: 10px 14px; margin: 14px 0; max-width: 80ch; }
.cadre { background: var(--surface); border: 1px solid var(--bord); border-radius: 6px; overflow-x: auto; margin-top: 10px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 7px 10px; text-align: left; border-bottom: 1px solid var(--bord); vertical-align: top; }
thead th { font-size: .78rem; font-weight: 600; color: var(--texte-3); white-space: nowrap; }
tbody tr:last-child > * { border-bottom: 0; }
tbody th { font-weight: 500; }
.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.classement td { vertical-align: middle; }
.classement .rang { color: var(--texte-3); width: 2.5em; }
.nom { display: block; font-weight: 500; }
.barre-cellule { white-space: nowrap; width: 40%; }
.piste { display: inline-block; width: calc(100% - 70px); max-width: 260px; height: 8px; background: var(--piste); vertical-align: middle; }
.barre { display: block; height: 100%; background: var(--barre); }
.valeur { display: inline-block; width: 64px; }
.donnees { font-size: .85rem; }
.donnees td { white-space: nowrap; }
.donnees th.groupe { text-align: left; border-left: 1px solid var(--bord); color: var(--texte-2); }
.donnees tbody th { white-space: nowrap; position: sticky; left: 0; background: var(--surface); }
.donnees td a { color: inherit; border-bottom: 1px dotted var(--texte-3); }
.methode td, .sources td { font-size: .9rem; }
.ecarte { color: var(--texte-3); }
.historique { font-size: .85rem; }
.historique td { white-space: nowrap; }
details { margin-top: 10px; }
summary { cursor: pointer; color: var(--accent); }
code { font-size: .9em; background: var(--piste); padding: 1px 4px; border-radius: 3px; }
footer { color: var(--texte-3); font-size: .85rem; border-top: 1px solid var(--bord); margin-top: 48px; padding-top: 14px; }
@media (max-width: 640px) {
  h1 { font-size: 1.5rem; }
  .classement th:nth-child(n+5), .classement td:nth-child(n+5) { display: none; }
  .barre-cellule { width: auto; }
  .piste { width: 56px; }
}
"""


def generer(joueurs, valeurs, sources, methode, methodes, temperature, cotes, historique, provenance):
    from modele import METHODES
    autre = next(m for m in methodes if m != methode)
    dates = sorted(p["telecharge_le"] for p in provenance)
    date_collecte = dates[-1][:16].replace("T", " à ") + " UTC" if dates else "date inconnue"
    dispo = methodes[methode]["dispo"]
    ecartes = [TXT_ELEMENT[c][e] for c in METHODES[methode] for e in METHODES[methode][c]
               if e not in dispo.get(c, {}) and e != "notes_match"]
    note_ecartes = ""
    if ecartes:
        note_ecartes = (f'<p class="note">Données incomplètes. Ces éléments ne sont pas disponibles pour les '
                        f'30 joueurs et ne comptent pour personne : {escape(", ".join(ecartes))}.</p>')
    j1 = joueurs[0]
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ballon d'or 2026, pronostic</title>
<meta name="description" content="Probabilités de victoire des 30 nommés au Ballon d'or 2026, calculées à partir de données sourcées.">
<style>{CSS}</style>
</head>
<body>
<main>
  <header>
    <h1>Ballon d'or 2026, pronostic</h1>
    <p class="intro">Probabilité de victoire des 30 nommés, calculée à partir de leurs résultats de la saison 2025-26.
      Cérémonie le 26 octobre 2026 à Londres. Données collectées le {date_collecte}.</p>
  </header>

  <section>
    <h2>Classement</h2>
    <p>Méthode {TXT_METHODE[methode]}. En tête : {escape(j1['joueur'])}, {pct(j1['proba'])}.
      La colonne « Autre méthode » donne le résultat de la méthode {TXT_METHODE[autre]} avec les mêmes données.
      Polymarket et Kalshi donnent, pour comparaison, la probabilité implicite des marchés de prédiction
      au moment de la collecte.</p>
    {note_ecartes}
    <div class="cadre">{bloc_classement(joueurs, cotes, autre)}</div>
  </section>

  <section>
    <h2>Données par joueur</h2>
    <p>Chaque valeur renvoie à sa source. Une case vide signifie que la donnée n'est pas disponible :
      elle n'est jamais estimée. « Points » : 2 par Ballon d'or gagné, 1 par 2e ou 3e place avant 2026.</p>
    <div class="cadre">{bloc_donnees(joueurs, valeurs, sources)}</div>
  </section>

  <section>
    <h2>Méthode</h2>
    <p>Deux méthodes utilisent les mêmes données. La méthode « statistiques individuelles » note d'abord les buts
      et passes de la saison, championnat et LDC réunis, puis sépare à la Coupe du monde les performances du joueur
      et le parcours de sa sélection. La méthode « par compétition » fait un critère par compétition.
      Dans les deux cas, chaque critère est noté de 0 à 100, puis les critères sont pondérés. Un élément manquant chez un seul
      joueur est écarté pour tous, et son poids est réparti entre les autres éléments du même critère.
      Les notes sont ensuite converties en probabilités (fonction softmax, température {str(temperature).replace(".", ",")}).
      La température est réglée à la main : elle n'est pas encore calibrée sur les éditions passées.</p>
    <h3>Méthode {TXT_METHODE[methode]} (classement principal)</h3>
    <div class="cadre">{bloc_methode(methode, methodes[methode])}</div>
    <h3>Méthode {TXT_METHODE[autre]} (comparaison)</h3>
    <div class="cadre">{bloc_methode(autre, methodes[autre])}</div>
    <p class="sous">Les notes de match ne sont pas utilisées : aucune source gratuite ne permet de les réutiliser.
      Les poids se règlent dans <a href="{URL_DEPOT}/blob/main/config/poids.yaml"><code>config/poids.yaml</code></a>.</p>
  </section>

  <section>
    <h2>Historique</h2>
    <p>Top 5 des éditions 1996 à 2025 (pas d'édition en 2020), avec les points ou le pourcentage de votes.</p>
    <details><summary>Afficher le tableau</summary>
      <div class="cadre">{bloc_historique(historique)}</div>
    </details>
  </section>

  <section>
    <h2>Sources</h2>
    <div class="cadre">{bloc_sources(provenance)}</div>
    <p class="sous">Les fichiers téléchargés sont conservés dans
      <a href="{URL_DEPOT}/tree/main/data"><code>data/</code></a>, avec leur adresse, leur date et leur empreinte
      dans <a href="{URL_DEPOT}/blob/main/data/provenance.csv"><code>provenance.csv</code></a>.</p>
  </section>

  <footer>
    <a href="{URL_DEPOT}">Code et données</a> · <a href="donnees/resultats.csv">Résultats en CSV</a> ·
    <a href="donnees/valeurs_2026.csv">Données sourcées en CSV</a>
  </footer>
</main>
</body>
</html>
"""
