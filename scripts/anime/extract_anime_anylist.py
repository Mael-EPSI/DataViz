import requests
import json
import time
import os

# --- GESTION DES CHEMINS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data", "data_brut"))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "anilist_raw.jsonl")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def run():
    print("DÉMARRAGE DE L'EXTRACTION MASSIVE JIKAN (2016-2026)")
    print(f"Destination : {OUTPUT_FILE}")
    
    count_total = 0
    # On vide le fichier au début pour repartir sur du propre
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        pass

    # On boucle par année pour maximiser les résultats
    for year in range(2016, 2027):
        print(f"\nExtraction de l'année : {year}")
        page = 1
        
        while True:
            # Recherche par année, trié par popularité
            url = f"https://api.jikan.moe/v4/anime?start_date={year}-01-01&end_date={year}-12-31&order_by=members&sort=desc&page={page}"
            
            try:
                response = requests.get(url, timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('data', [])
                    pagination = data.get('pagination', {})
                    
                    if not items:
                        break # Plus de résultats pour cette année
                    
                    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                        for item in items:
                            titles = [item.get('title'), item.get('title_english'), item.get('title_japanese')]
                            
                            clean_record = {
                                "mal_id": item['mal_id'],
                                "titles": list(set([t for t in titles if t])),
                                "population": item.get('members', 0),
                                "score_mal": item.get('score', 0),
                                "annee": year,
                                "type": item.get('type') # TV, Movie, OVA...
                            }
                            f.write(json.dumps(clean_record, ensure_ascii=False) + "\n")
                            count_total += 1
                    
                    print(f"Année {year} | Page {page} récupérée ({len(items)} animés)")
                    
                    # Vérifier s'il y a une page suivante
                    if not pagination.get('has_next_page'):
                        break
                        
                    page += 1
                    # PAUSE CRITIQUE : Jikan limite à 3 req/sec. On assure avec 1.5s
                    time.sleep(1.5) 
                    
                elif response.status_code == 429:
                    print("Limite atteinte (429). Pause de 20 secondes...")
                    time.sleep(20)
                    continue # On retente la même page
                else:
                    print(f"Erreur {response.status_code} sur l'année {year}")
                    break

            except Exception as e:
                print(f"Crash sur page {page}: {e}")
                time.sleep(5)
                continue

    print(f"\n fini : {count_total} animés extraits au total.")

if __name__ == "__main__":
    run()