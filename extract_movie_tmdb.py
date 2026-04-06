import requests
import json
import time
import os

# --- GESTION DES CHEMINS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Remonte de 2 niveaux pour aller dans data/data_brut
OUTPUT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data", "data_brut"))
FILENAME = os.path.join(OUTPUT_DIR, "movies_raw.jsonl")

# Sécurité : création du dossier s'il n'existe pas
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- CONFIGURATION API ---
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzNDAzYjFhMmE4Yjk4M2I2Yzk2MmNkZGY1MWI3NjE2NiIsIm5iZiI6MTc3MzczNzEzNy4yMTQwMDAyLCJzdWIiOiI2OWI5MTRiMThlODFlNWIyZDUwOGY3ZjciLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.GlyZa5K95ZWxD40a3XXWKxKFgCOcPq1dLB5ozWQFjk4"
MAX_PAGES = 300 

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

def get_already_processed_ids():
    """Évite de retélécharger les films déjà présents dans le fichier"""
    ids = set()
    if os.path.exists(FILENAME):
        with open(FILENAME, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    ids.add(data['id'])
                except:
                    continue
    return ids

def fetch_details(media_type, item_id):
    """Récupère les détails complets (credits, images, etc.)"""
    url = f"https://api.themoviedb.org/3/{media_type}/{item_id}"
    params = {
        "append_to_response": "credits,images,keywords",
        "language": "fr-FR",
        "include_image_language": "fr,en,null"
    }
    
    while True:
        try:
            res = requests.get(url, headers=HEADERS, params=params, timeout=10)
            if res.status_code == 200:
                return res.json()
            elif res.status_code == 429: # Rate Limit
                retry_after = int(res.headers.get("Retry-After", 5))
                print(f"   ⚠️ Limite API. Pause de {retry_after}s...")
                time.sleep(retry_after)
                continue
            else:
                return None
        except:
            time.sleep(10)
            continue

def run():
    processed_ids = get_already_processed_ids()
    print(f"🚀 Démarrage Extraction Films (Mode Deep Scraping)")
    print(f"📊 Déjà extraits : {len(processed_ids)} items.")
    print(f"📂 Destination : {FILENAME}")

    # Pour ce script on ne traite que les 'movie'
    m_type = 'movie'
    
    for page in range(1, MAX_PAGES + 1):
        # On filtre à partir de 2016 pour coller à ton projet
        discover_url = f"https://api.themoviedb.org/3/discover/{m_type}"
        params = {
            "sort_by": "popularity.desc", 
            "page": page, 
            "language": "fr-FR",
            "primary_release_date.gte": "2016-01-01"
        }
        
        try:
            resp = requests.get(discover_url, headers=HEADERS, params=params, timeout=10)
            if resp.status_code != 200: continue
            
            results = resp.json().get('results', [])
            if not results: break

            # On ouvre en mode 'a' (append) pour ajouter à la suite
            with open(FILENAME, 'a', encoding='utf-8') as f:
                for item in results:
                    item_id = item['id']
                    
                    if item_id in processed_ids:
                        continue
                    
                    name = item.get('title')
                    print(f"Page {page}/{MAX_PAGES} | ID {item_id} | {name}")
                    
                    full_data = fetch_details(m_type, item_id)
                    if full_data:
                        # On s'assure d'avoir les infos minimales même si les détails sont vides
                        full_data['media_type_tag'] = m_type
                        f.write(json.dumps(full_data, ensure_ascii=False) + "\n")
                        f.flush() 
                        processed_ids.add(item_id)
                    
                    time.sleep(0.1) # Stabilité

        except Exception as e:
            print(f"💥 Erreur page {page}: {e}")
            time.sleep(5)

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n🛑 Interrompu. Les données sont sauvegardées.")