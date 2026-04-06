import requests
import json
import time
import os

# --- GESTION DES CHEMINS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# On remonte de scripts/anime/ vers DataViz/ puis on va dans data/data_brut/
OUTPUT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data", "data_brut"))
FILENAME = os.path.join(OUTPUT_DIR, "anime_raw.jsonl")

# Sécurité : création du dossier s'il n'existe pas
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- CONFIGURATION ---
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzNDAzYjFhMmE4Yjk4M2I2Yzk2MmNkZGY1MWI3NjE2NiIsIm5iZiI6MTc3MzczNzEzNy4yMTQwMDAyLCJzdWIiOiI2OWI5MTRiMThlODFlNWIyZDUwOGY3ZjciLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.GlyZa5K95ZWxD40a3XXWKxKFgCOcPq1dLB5ozWQFjk4"
MAX_PAGES = 300 

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

def clean_anime_data(raw_data, m_type):
    """Nettoyage et formatage des données récupérées via l'API de détails"""
    return {
        "id": raw_data.get("id"),
        "is_anime": True, # Flag important pour tes graphiques
        "format": "Film" if m_type == "movie" else "Série",
        "titre": raw_data.get("name") or raw_data.get("title"),
        "titre_original": raw_data.get("original_name") or raw_data.get("original_title"),
        "synopsis": raw_data.get("overview"),
        "date": raw_data.get("first_air_date") or raw_data.get("release_date"),
        "note": raw_data.get("vote_average"),
        "nb_votes": raw_data.get("vote_count"),
        "popularite": raw_data.get("popularity"),
        "genres": [g["name"] for g in raw_data.get("genres", [])],
        "origin_country": raw_data.get("origin_country", []),
        "poster": raw_data.get("poster_path"),
        "episodes": raw_data.get("number_of_episodes", 0),
        "saisons": raw_data.get("number_of_seasons", 0),
        "status": raw_data.get("status")
    }

def fetch_details(m_type, item_id):
    """Récupère la fiche détaillée d'un animé (TV ou Movie)"""
    url = f"https://api.themoviedb.org/3/{m_type}/{item_id}?language=fr-FR"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            return clean_anime_data(res.json(), m_type)
        elif res.status_code == 429: # Gestion du Rate Limit
            retry_after = int(res.headers.get("Retry-After", 5))
            print(f"   ⚠️ Limite API atteinte. Pause de {retry_after}s...")
            time.sleep(retry_after)
            return fetch_details(m_type, item_id)
        return None
    except Exception as e:
        print(f"   💥 Erreur détails ID {item_id}: {e}")
        return None

def run():
    print(f"DÉMARRAGE EXTRACTION ANIMÉS (TMDB)")
    print(f"Destination : {FILENAME}")

    # On boucle sur 'tv' (Séries) puis 'movie' (Films d'animation)
    for m_type in ['tv', 'movie']:
        print(f"\n--- ⏳ TYPE : {m_type.upper()} ---")
        
        for page in range(1, MAX_PAGES + 1):
            discover_url = f"https://api.themoviedb.org/3/discover/{m_type}"
            # Filtre : Genre 16 (Animation), Origine JP (Japon), Date >= 2016
            params = {
                "with_genres": "16",
                "with_origin_country": "JP",
                "first_air_date.gte" if m_type == "tv" else "primary_release_date.gte": "2016-01-01",
                "sort_by": "popularity.desc",
                "page": page,
                "language": "fr-FR"
            }
            
            try:
                resp = requests.get(discover_url, headers=HEADERS, params=params, timeout=10)
                if resp.status_code != 200:
                    print(f"Erreur {resp.status_code} à la page {page}")
                    continue
                
                results = resp.json().get('results', [])
                if not results:
                    print(f"🏁 Plus de résultats pour {m_type} à la page {page}.")
                    break

                with open(FILENAME, 'a', encoding='utf-8') as f:
                    for item in results:
                        # Appel pour avoir les détails (nb épisodes, genres complets...)
                        data = fetch_details(m_type, item['id'])
                        if data:
                            f.write(json.dumps(data, ensure_ascii=False) + "\n")
                            f.flush()
                        
                        # Anti-spam API
                        time.sleep(0.05)
                    
                    print(f"Page {page}/{MAX_PAGES} ({m_type}) enregistrée.")

            except Exception as e:
                print(f"Erreur critique page {page}: {e}")
                time.sleep(5)

if __name__ == "__main__":
    run()