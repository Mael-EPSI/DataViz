import json
import os

# --- CONFIGURATION DES CHEMINS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_CLEAN_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data", "data_clean"))
DATA_FORMAT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data", "data_format"))

FILE_MOVIES = os.path.join(DATA_CLEAN_DIR, "movies_final.jsonl")
FILE_ANIME = os.path.join(DATA_CLEAN_DIR, "anime_final.jsonl")
OUTPUT_FILE = os.path.join(DATA_FORMAT_DIR, "map_data.json")

os.makedirs(DATA_FORMAT_DIR, exist_ok=True)

def lancer_formatage():
    print("🔧 Formatage des données pour le Dashboard Web...")
    final_data = []

    # 1. Traitement des FILMS
    if os.path.exists(FILE_MOVIES):
        with open(FILE_MOVIES, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    item = json.loads(line)
                    # On s'assure que la structure est compatible avec le JS
                    item["type_media"] = "Film"
                    if "population" not in item:
                        item["population"] = 0
                    final_data.append(item)
                except: continue
        print(f"Films intégrés.")

    # 2. Traitement des ANIMÉS
    if os.path.exists(FILE_ANIME):
        with open(FILE_ANIME, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    item = json.loads(line)
                    item["type_media"] = "Animé"
                    # La région est déjà fixée à "JP" dans ton clean_anime
                    final_data.append(item)
                except: continue
        print(f"Animés intégrés.")

    # 3. Écriture du fichier JSON final (Tableau d'objets)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
        # indent=2 est important pour que tu puisses vérifier le fichier à l'oeil nu
        json.dump(final_data, f_out, ensure_ascii=False, indent=2)

    print(f"\nSuccès ! Fichier généré : {OUTPUT_FILE}")
    print(f"Nombre total d'entrées : {len(final_data)}")

if __name__ == "__main__":
    lancer_formatage()