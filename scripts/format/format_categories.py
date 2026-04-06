import json
import os

# --- CONFIGURATION DES CHEMINS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_CLEAN_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data", "data_clean"))
DATA_FORMAT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data", "data_format"))

FILE_MOVIES = os.path.join(DATA_CLEAN_DIR, "movies_final.jsonl")
FILE_ANIME = os.path.join(DATA_CLEAN_DIR, "anime_final.jsonl")
OUTPUT_FILE = os.path.join(DATA_FORMAT_DIR, "categories.json")

os.makedirs(DATA_FORMAT_DIR, exist_ok=True)

# Traduction des genres anglais (animés TMDB) vers leur équivalent français (films TMDB)
GENRE_EN_TO_FR = {
    "Adventure":       "Aventure",
    "Animation":       "Animation",
    "Comedy":          "Comédie",
    "Crime":           "Crime",
    "Documentary":     "Documentaire",
    "Drama":           "Drame",
    "Family":          "Familial",
    "Fantasy":         "Fantastique",
    "History":         "Histoire",
    "Horror":          "Horreur",
    "Music":           "Musique",
    "Mystery":         "Mystère",
    "Romance":         "Romance",
    "Science Fiction": "Science-Fiction",
    "Sci-Fi":          "Science-Fiction",
    "Thriller":        "Thriller",
    "War":             "Guerre",
    "Western":         "Western",
    "Action":          "Action",
}

def normaliser_genre_anime(genre):
    """Traduit un genre anglais vers le français utilisé pour les films."""
    return GENRE_EN_TO_FR.get(genre, genre)

def lancer_formatage():
    print("🔧 Comptage des genres pour le Dashboard...")

    films_genres = {}
    animes_genres = {}

    # 1. Comptage des genres des FILMS (champ : "genres" → liste de strings)
    if os.path.exists(FILE_MOVIES):
        with open(FILE_MOVIES, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    item = json.loads(line)
                    for genre in item.get('genres', []):
                        if genre:
                            films_genres[genre] = films_genres.get(genre, 0) + 1
                except Exception:
                    continue
        print(f"✅ Genres films comptés.")

    # 2. Comptage des genres des ANIMÉS (champ : "genres_list" → liste de dicts ou strings)
    # Les genres composés comme "Action & Adventure" sont découpés en genres individuels
    if os.path.exists(FILE_ANIME):
        with open(FILE_ANIME, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    item = json.loads(line)
                    for g in item.get('genres_list', []):
                        raw = g.get('name') if isinstance(g, dict) else g
                        if not raw:
                            continue
                        # Découpage sur " & " pour séparer les genres composés
                        for genre in [part.strip() for part in raw.split(' & ')]:
                            genre = normaliser_genre_anime(genre)
                            if genre:
                                animes_genres[genre] = animes_genres.get(genre, 0) + 1
                except Exception:
                    continue
        print(f"✅ Genres animés comptés.")

    # 3. Tri par fréquence décroissante
    films_sorted  = sorted(films_genres.items(),  key=lambda x: x[1], reverse=True)
    animes_sorted = sorted(animes_genres.items(), key=lambda x: x[1], reverse=True)

    output = {
        "films":  [{"genre": g, "count": c} for g, c in films_sorted],
        "animes": [{"genre": g, "count": c} for g, c in animes_sorted]
    }

    # 4. Écriture du fichier JSON final
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
        json.dump(output, f_out, ensure_ascii=False, indent=2)

    print(f"\n✨ Succès ! Fichier généré : {OUTPUT_FILE}")
    print(f"📊 Genres films : {len(films_sorted)} | Genres animés : {len(animes_sorted)}")


if __name__ == "__main__":
    lancer_formatage()