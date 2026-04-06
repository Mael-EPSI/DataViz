import json
import os

# --- CONFIGURATION DES CHEMINS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_CLEAN_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data", "data_clean"))
DATA_FORMAT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data", "data_format"))

FILE_MOVIES = os.path.join(DATA_CLEAN_DIR, "movies_final.jsonl")
FILE_ANIME  = os.path.join(DATA_CLEAN_DIR, "anime_final.jsonl")
OUTPUT_FILE = os.path.join(DATA_FORMAT_DIR, "timeline.json")

os.makedirs(DATA_FORMAT_DIR, exist_ok=True)

YEARS = [str(y) for y in range(2016, 2027)]

def charger_elements(filepath, pop_key):
    """Charge les items et retourne un dict année → liste de (note, popularite)."""
    per_year = {y: [] for y in YEARS}
    if not os.path.exists(filepath):
        print(f"Fichier introuvable : {filepath}")
        return per_year
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                item = json.loads(line)
                annee = str(item.get('annee', ''))
                note  = item.get('note', 0) or 0
                pop   = item.get(pop_key, 0) or 0
                if annee in per_year and note > 0:
                    per_year[annee].append({'note': note, 'pop': pop})
            except Exception:
                continue
    return per_year

def calculer_stats(per_year):
    """Calcule la note moyenne et la popularité moyenne par année."""
    note_moy = []
    pop_moy  = []
    count    = []
    for y in YEARS:
        items = per_year[y]
        if items:
            note_moy.append(round(sum(i['note'] for i in items) / len(items), 2))
            pop_moy.append(round(sum(i['pop']  for i in items) / len(items), 2))
            count.append(len(items))
        else:
            note_moy.append(None)
            pop_moy.append(None)
            count.append(0)
    return note_moy, pop_moy, count

def normaliser(values):
    """Min-max normalisation → [0, 10] en ignorant les None."""
    cleaned = [v for v in values if v is not None]
    if not cleaned:
        return values
    vmin, vmax = min(cleaned), max(cleaned)
    if vmax == vmin:
        return [5.0 if v is not None else None for v in values]
    return [
        round((v - vmin) / (vmax - vmin) * 10, 2) if v is not None else None
        for v in values
    ]

def calculer_score(note_moy, pop_norm):
    """Score combiné = 60% note normalisée + 40% popularité normalisée (les deux sur [0,10])."""
    note_norm = normaliser(note_moy)
    scores = []
    for n, p in zip(note_norm, pop_norm):
        if n is None or p is None:
            scores.append(None)
        else:
            scores.append(round(n * 0.6 + p * 0.4, 2))
    return scores

def lancer_formatage():
    print("🔧 Calcul de l'évolution temporelle (2016-2026)...")

    # --- Films (popularite = score TMDB) ---
    films_per_year = charger_elements(FILE_MOVIES, 'popularite')
    films_note, films_pop, films_count = calculer_stats(films_per_year)
    films_pop_norm = normaliser(films_pop)
    films_score    = calculer_score(films_note, films_pop_norm)
    print(f"Films traités.")

    # --- Animés (population = audience AniList) ---
    animes_per_year = charger_elements(FILE_ANIME, 'popularite_tmdb')
    animes_note, animes_pop, animes_count = calculer_stats(animes_per_year)
    animes_pop_norm = normaliser(animes_pop)
    animes_score    = calculer_score(animes_note, animes_pop_norm)
    print(f"Animés traités.")

    output = {
        "labels": YEARS,
        "films": {
            "note_moy":  films_note,
            "pop_moy":   films_pop,
            "score":     films_score,
            "count":     films_count
        },
        "animes": {
            "note_moy":  animes_note,
            "pop_moy":   animes_pop,
            "score":     animes_score,
            "count":     animes_count
        }
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
        json.dump(output, f_out, ensure_ascii=False, indent=2)

    print(f"\nSuccès ! Fichier généré : {OUTPUT_FILE}")

if __name__ == "__main__":
    lancer_formatage()
