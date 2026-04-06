import json
import os

# --- CONFIGURATION ---
LIMIT_MOVIES = 1000  # On s'aligne sur ton volume d'animés (~905)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_BRUT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data", "data_brut"))
DATA_CLEAN_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data", "data_clean"))
data_errors_dir = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data", "data_clean", "errors"))

FILE_INPUT = os.path.join(DATA_BRUT_DIR, "movies_raw.jsonl")
FILE_OUTPUT = os.path.join(DATA_CLEAN_DIR, "movies_final.jsonl")
FILE_ERRORS = os.path.join(data_errors_dir, "movies_errors.jsonl")

os.makedirs(DATA_CLEAN_DIR, exist_ok=True)
os.makedirs(data_errors_dir, exist_ok=True)

def lancer_nettoyage():
    print(f"🧹 Nettoyage des FILMS (Limite : {LIMIT_MOVIES} les plus populaires)...")
    
    all_valid_movies = []
    count_error = 0

    if not os.path.exists(FILE_INPUT):
        print(f"❌ Fichier source introuvable : {FILE_INPUT}")
        return

    # On ouvre le fichier d'erreurs en écriture
    with open(FILE_ERRORS, 'w', encoding='utf-8') as f_err:
        with open(FILE_INPUT, 'r', encoding='utf-8') as f_in:
            for line in f_in:
                line = line.strip()
                if not line: continue
                
                try:
                    item = json.loads(line)
                    
                    # --- RÉCUPÉRATION DES CLÉS ---
                    titre = item.get('title')
                    date_brute = item.get('release_date')
                    votes = item.get('vote_count', 0)
                    
                    # --- FILTRES DE QUALITÉ (Même logique que les animés) ---
                    if titre and date_brute and len(date_brute) >= 4 and votes >= 10:
                        annee = date_brute[:4]
                        
                        # Filtrage période 2016-2026
                        if "2016" <= annee <= "2026":
                            genres_raw = item.get('genres', [])
                            genres_list = [g['name'] for g in genres_raw if isinstance(g, dict) and 'name' in g]
                            
                            clean_item = {
                                "id": item.get('id'),
                                "is_anime": False,
                                "titre": titre,
                                "annee": annee,
                                "note": item.get('vote_average', 0),
                                "nb_votes": votes,
                                "popularite": item.get('popularity', 0),
                                "genres": genres_list,
                                "region": item.get('origin_country', ["Monde"])[0] if item.get('origin_country') else "Monde"
                            }
                            # On ajoute à la liste temporaire au lieu d'écrire de suite
                            all_valid_movies.append(clean_item)
                        else:
                            count_error += 1
                    else:
                        count_error += 1
                        
                except Exception:
                    continue

    # --- TRI ET LIMITE ---
    # On trie par popularité (les films les plus connus en premier)
    all_valid_movies.sort(key=lambda x: x['popularite'], reverse=True)
    
    # On applique le CAP
    limited_movies = all_valid_movies[:LIMIT_MOVIES]

    # --- ÉCRITURE DU FICHIER PROPRE ---
    with open(FILE_OUTPUT, 'w', encoding='utf-8') as f_out:
        for movie in limited_movies:
            f_out.write(json.dumps(movie, ensure_ascii=False) + "\n")

    print(f"\n✅ Nettoyage terminé !")
    print(f"🎬 Films sélectionnés (Top Pop) : {len(limited_movies)}")
    print(f"❌ Films écartés (Qualité/Date) : {count_error}")

if __name__ == "__main__":
    lancer_nettoyage()