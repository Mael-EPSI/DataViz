# DataViz — Animés vs Films (2016–2026)

Projet de visualisation de données réalisé dans le cadre du BTS 2026.  
**Problématique : Quelle est la place des animés dans le monde du cinéma/série ?**

---

## Présentation

Ce projet compare **1 000 films** et **1 000 animés** sortis entre 2016 et 2026 à travers quatre dashboards interactifs :

| Page | Contenu |
|---|---|
| `info.html` | Page d'accueil avec statistiques globales et navigation |
| `region.html` | Carte mondiale des productions + filtres par région et type |
| `categories.html` | Distribution des genres films / animés |
| `timeline.html` | Évolution temporelle de la note, popularité et score combiné |
| `comparaison.html` | Comparaison globale : KPIs, donut, radar, conclusion automatique |

---

## Sources de données

| Source | Données |
|---|---|
| [TMDB API](https://www.themoviedb.org/documentation/api) | Films et animés (note, popularité, genres, région) |
| [AniList API (Jikan)](https://jikan.moe/) | Audience des animés (membres AniList) |

---

## Structure du projet

```
DataViz/
├── data/
│   ├── data_brut/          # Données brutes extraites des APIs
│   │   ├── movies_raw.jsonl
│   │   ├── anime_raw.jsonl
│   │   └── anilist_raw.jsonl
│   ├── data_clean/         # Données nettoyées et filtrées
│   │   ├── movies_final.jsonl
│   │   ├── anime_final.jsonl
│   │   └── errors/
│   └── data_format/        # Fichiers JSON pour le web
│       ├── map_data.json
│       ├── categories.json
│       ├── timeline.json
│       └── comparaison.json
├── scripts/
│   ├── main.py             # Orchestrateur du pipeline ETL complet
│   ├── movie/
│   │   ├── extract_movie_tmdb.py   # Extraction films TMDB
│   │   └── clean_movie.py          # Nettoyage et filtrage films
│   ├── anime/
│   │   ├── extract_anime_tmdb.py   # Extraction animés TMDB
│   │   ├── extract_anime_anylist.py # Extraction audience AniList
│   │   └── clean_anime.py          # Nettoyage et jointure animés
│   └── format/
│       ├── format_map_data.py      # Fusion pour la carte
│       ├── format_categories.py    # Comptage des genres
│       ├── format_timeline.py      # Stats par année
│       └── format_comparaison.py   # Statistiques comparatives
└── web/
    ├── style.css           # CSS unifié (thème beige, variables CSS)
    ├── info.html
    ├── region.html
    ├── categories.html
    ├── timeline.html
    └── comparaison.html
```

---

## Pipeline ETL

```
EXTRACTION        NETTOYAGE          FORMATAGE          AFFICHAGE
──────────        ─────────          ─────────          ─────────
TMDB (films)  →  clean_movie    →   format_map_data  →  region.html
TMDB (animés) →  clean_anime    →   format_categories → categories.html
AniList       →  (jointure)     →   format_timeline  →  timeline.html
                                    format_comparaison→  comparaison.html
```

### Lancer le pipeline complet

```bash
python scripts/main.py
```

> Les étapes d'extraction sont commentées par défaut dans `main.py` (données brutes déjà présentes).  
> Pour relancer une extraction, décommenter les appels correspondants.

### Lancer une étape individuellement

```bash
python scripts/format/format_categories.py
python scripts/format/format_timeline.py
python scripts/format/format_comparaison.py
python scripts/format/format_map_data.py
```

---

## Données nettoyées

### Films (`movies_final.jsonl`)
| Champ | Description |
|---|---|
| `id` | Identifiant TMDB |
| `is_anime` | `false` |
| `titre` | Titre français |
| `annee` | Année de sortie |
| `note` | Note moyenne TMDB (0–10) |
| `nb_votes` | Nombre de votes |
| `popularite` | Score de popularité TMDB |
| `genres` | Liste de genres en français |
| `region` | Code pays d'origine (ex: `"US"`) |

### Animés (`anime_final.jsonl`)
| Champ | Description |
|---|---|
| `id` | Identifiant TMDB |
| `is_anime` | `true` |
| `titre` | Titre français |
| `annee` | Année de sortie |
| `note` | Note moyenne TMDB (0–10) |
| `nb_votes` | Nombre de votes TMDB |
| `population` | Nombre de membres AniList |
| `popularite_tmdb` | Score popularité TMDB |
| `genres_list` | Liste de genres (strings ou dicts) |
| `region` | `"JP"` (Japon) |

---

## Technologies

| Technologie | Usage |
|---|---|
| Python 3 | Pipeline ETL |
| Bootstrap 5.3 | Mise en page |
| Chart.js | Graphiques (barres, lignes, donut, radar) |
| Leaflet 1.9.4 | Carte interactive |

---

## Lancer le site web

Ouvrir `web/info.html` avec un serveur local (ex: Live Server dans VS Code).  
Les pages chargent les fichiers JSON depuis `../data/data_format/` via `fetch()`.

---

## Auteur

Projet BTS — 2026
