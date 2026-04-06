import json
import os

# config paths (chemins)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_CLEAN_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data", "data_clean"))
DATA_FORMAT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data", "data_format"))

FILE_MOVIES = os.path.join(DATA_CLEAN_DIR, "movies_final.jsonl")
FILE_ANIME  = os.path.join(DATA_CLEAN_DIR, "anime_final.jsonl")
OUTPUT_FILE = os.path.join(DATA_FORMAT_DIR, "comparaison.json")

os.makedirs(DATA_FORMAT_DIR, exist_ok=True)

def charger_tout(filepath):
    items = []
    if not os.path.exists(filepath):
        return items
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                items.append(json.loads(line))
            except Exception:
                continue
    return items

def normaliser_genre(g):
    """Extrait le nom d'un genre (string ou dict) et découpe les composés."""
    raw = g.get('name') if isinstance(g, dict) else g
    if not raw:
        return []
    return [part.strip() for part in raw.split(' & ')]

def calculer_stats(items, pop_key, genre_key):
    notes     = [i['note']      for i in items if i.get('note', 0) > 0]
    votes     = [i['nb_votes']  for i in items if i.get('nb_votes', 0) > 0]
    pops      = [i[pop_key]     for i in items if i.get(pop_key, 0) > 0]
    regions   = set(i.get('region', '') for i in items if i.get('region'))
    genres    = set()
    for i in items:
        for g in i.get(genre_key, []):
            for name in normaliser_genre(g):
                if name:
                    genres.add(name)

    return {
        "count":           len(items),
        "note_moy":        round(sum(notes) / len(notes), 2) if notes else 0,
        "note_max":        round(max(notes), 2) if notes else 0,
        "votes_moy":       round(sum(votes) / len(votes), 2) if votes else 0,
        "pop_moy":         round(sum(pops) / len(pops), 2) if pops else 0,
        "nb_genres":       len(genres),
        "genres_list":     sorted(genres),
        "nb_regions":      len(regions),
        "regions_list":    sorted(regions),
    }

def normaliser_radar(films_val, animes_val):
    """Ramène les deux valeurs sur [0, 10] relatif l'une à l'autre."""
    vmax = max(films_val, animes_val)
    if vmax == 0:
        return 5.0, 5.0
    return round(films_val / vmax * 10, 2), round(animes_val / vmax * 10, 2)

def lancer_formatage():
    print("Calcul des statistiques comparatives globales...")

    films  = charger_tout(FILE_MOVIES)
    animes = charger_tout(FILE_ANIME)

    fs = calculer_stats(films,  pop_key='popularite', genre_key='genres')
    as_ = calculer_stats(animes, pop_key='population', genre_key='genres_list')

    # --- Radar : 5 axes normalisés sur [0, 10] ---
    r_note_f,    r_note_a    = normaliser_radar(fs['note_moy'],   as_['note_moy'])
    r_votes_f,   r_votes_a   = normaliser_radar(fs['votes_moy'],  as_['votes_moy'])
    r_pop_f,     r_pop_a     = normaliser_radar(fs['pop_moy'],    as_['pop_moy'])
    r_genres_f,  r_genres_a  = normaliser_radar(fs['nb_genres'],  as_['nb_genres'])
    r_regions_f, r_regions_a = normaliser_radar(fs['nb_regions'], as_['nb_regions'])

    output = {
        "films": {
            **fs,
            "radar": [r_note_f, r_votes_f, r_pop_f, r_genres_f, r_regions_f]
        },
        "animes": {
            **as_,
            "radar": [r_note_a, r_votes_a, r_pop_a, r_genres_a, r_regions_a]
        },
        "radar_labels": ["Note moyenne", "Votes /titre", "Popularité moy.", "Diversité genres", "Couverture géo."]
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
        json.dump(output, f_out, ensure_ascii=False, indent=2)

    print(f"Films  : {fs['count']} titres | note {fs['note_moy']} | {fs['nb_genres']} genres | {fs['nb_regions']} régions")
    print(f"Animés : {as_['count']} titres | note {as_['note_moy']} | {as_['nb_genres']} genres | {as_['nb_regions']} régions")
    print(f"\nSuccès ! Fichier généré : {OUTPUT_FILE}")

if __name__ == "__main__":
    lancer_formatage()
