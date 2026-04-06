import json
import os
import re

# --- CONFIGURATION ---
LIMIT_ANIME = 1000  # Limite pour équilibrer avec les films

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_BRUT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data", "data_brut"))
DATA_CLEAN_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data", "data_clean"))
data_errors_dir = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data", "data_clean", "errors"))

FILE_TMDB = os.path.join(DATA_BRUT_DIR, "anime_raw.jsonl")
FILE_JIKAN = os.path.join(DATA_BRUT_DIR, "anilist_raw.jsonl")
FILE_OUTPUT = os.path.join(DATA_CLEAN_DIR, "anime_final.jsonl")
FILE_ERRORS = os.path.join(data_errors_dir, "anime_errors.jsonl")

os.makedirs(DATA_CLEAN_DIR, exist_ok=True)
os.makedirs(data_errors_dir, exist_ok=True)

def normaliser_titre(title):
    if not title: return ""
    return re.sub(r'[^a-z0-9\s]', '', title.lower()).strip()

def charger_donnees_anilist():
    jikan_data = []
    if os.path.exists(FILE_JIKAN):
        with open(FILE_JIKAN, 'r', encoding='utf-8') as f:
            for line in f:
                try: jikan_data.append(json.loads(line))
                except: continue
    return jikan_data

def lancer_nettoyage():
    print(f" Nettoyage des ANIMÉS (Qualité + Limite {LIMIT_ANIME})...")
    
    jikan_list = charger_donnees_anilist()
    all_valid_anime = []
    count_discarded = 0

    if not os.path.exists(FILE_TMDB):
        print(f"Fichier source introuvable : {FILE_TMDB}")
        return

    with open(FILE_ERRORS, 'w', encoding='utf-8') as f_err:
        with open(FILE_TMDB, 'r', encoding='utf-8') as f_in:
            for line in f_in:
                try:
                    item = json.loads(line)
                    
                    # --- RÉCUPÉRATION DES INFOS ---
                    note = item.get('vote_average') or item.get('note') or 0
                    votes = item.get('vote_count') or item.get('nb_votes') or 0
                    tmdb_title = item.get('title') or item.get('titre')
                    date_brute = item.get('release_date') or item.get('date') or ""
                    
                    # --- FILTRES DE QUALITÉ ---
                    is_quality_content = (note > 0) and (votes >= 10)
                    has_basic_info = tmdb_title and date_brute and len(date_brute) >= 4
                    
                    if is_quality_content and has_basic_info:
                        annee = date_brute[:4]
                        
                        # --- LIAISON JIKAN (POPULATION) ---
                        population_trouvee = 0
                        norm_title = normaliser_titre(tmdb_title)
                        for jk in jikan_list:
                            if str(jk.get('annee')) == annee:
                                jk_titles = [normaliser_titre(t) for t in jk.get('titles', [])]
                                if norm_title in jk_titles:
                                    population_trouvee = jk.get('population', 0)
                                    break
                        
                        if population_trouvee > 0:
                            clean_item = {
                                "id": item.get('id'),
                                "is_anime": True,
                                "titre": tmdb_title,
                                "annee": annee,
                                "note": note,
                                "nb_votes": votes,
                                "population": population_trouvee,
                                "popularite_tmdb": item.get('popularite', 0),
                                "genres_list" : item.get('genres', []),
                                "region": "JP"
                            }
                            all_valid_anime.append(clean_item)
                        else:
                            item["error_reason"] = "Population Jikan non trouvée"
                            f_err.write(json.dumps(item, ensure_ascii=False) + "\n")
                            count_discarded += 1
                    else:
                        item["error_reason"] = "Critères de qualité non remplis"
                        f_err.write(json.dumps(item, ensure_ascii=False) + "\n")
                        count_discarded += 1
                        
                except Exception:
                    continue

    # --- TRI ET LIMITATION ---
    # On trie par population décroissante (les plus vus d'abord)
    all_valid_anime.sort(key=lambda x: x['population'], reverse=True)
    
    # On applique la limite
    limited_anime = all_valid_anime[:LIMIT_ANIME]

    # --- ÉCRITURE DU FICHIER FINAL ---
    with open(FILE_OUTPUT, 'w', encoding='utf-8') as f_out:
        for anime in limited_anime:
            f_out.write(json.dumps(anime, ensure_ascii=False) + "\n")

    print(f"Animés validés et limités : {len(limited_anime)}")
    print(f"Animés écartés (erreurs/qualité) : {count_discarded}")

if __name__ == "__main__":
    lancer_nettoyage()