import os
import subprocess
import time
import sys

# --- CONFIGURATION DES CHEMINS ---
# On se base sur l'emplacement du script main.py (dans /scripts)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# On remonte d'un cran pour être à la racine de DataViz
ROOT_DIR = os.path.join(BASE_DIR, "..")

# Dossiers de données (pour vérification)
DATA_DIRS = [
    os.path.join(ROOT_DIR, "data", "data_brut"),
    os.path.join(ROOT_DIR, "data", "data_clean"),
    os.path.join(ROOT_DIR, "data", "data_format")
]

def verifier_dossiers():
    """Vérifie que l'arborescence de données existe"""
    for d in DATA_DIRS:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"📁 Création du dossier : {d}")

def executer_etape(relative_path, description):
    """Exécute un sous-script Python"""
    script_path = os.path.join(BASE_DIR, relative_path)
    print(f"\n--- ⏳ {description.upper()} ---")
    
    if not os.path.exists(script_path):
        print(f"❌ ERREUR : Impossible de trouver {script_path}")
        return False

    try:
        # On utilise sys.executable pour être sûr d'utiliser le même Python
        subprocess.run([sys.executable, script_path], check=True)
        print(f"✅ {description} terminée.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"💥 ERREUR CRITIQUE lors de {description} : {e}")
        return False

def principal():
    start_time = time.time()
    print("==========================================")
    print("🚀 DÉMARRAGE DU PIPELINE ETL AUTOMATISÉ")
    print("==========================================")
    
    verifier_dossiers()

    # --- ÉTAPE 1 : EXTRACTION (E) ---
    # Récupération des données brutes
    if not executer_etape("movie/extract_movie_tmdb.py", "Extraction Films TMDB"):
        sys.exit(1)
        
    if not executer_etape("anime/extract_anime_tmdb.py", "Extraction Animés TMDB"):
        sys.exit(1)
        
    if not executer_etape("anime/extract_anime_anylist.py", "Extraction Population AniList"):
        sys.exit(1)

    # --- ÉTAPE 2 : NETTOYAGE ET JOINTURE (T) ---
    # Transformation des données brutes en données propres (Mapping AniList inclus)
    if not executer_etape("movie/clean_movie.py", "Nettoyage Films"):
        sys.exit(1)
        
    if not executer_etape("anime/clean_anime.py", "Nettoyage et Jointure Animés"):
        sys.exit(1)

    # --- ÉTAPE 3 : CHARGEMENT POUR LE WEB (L) ---
    # Génération des fichiers JSON finaux pour le web
    if not executer_etape("format/format_map_data.py", "Génération Map Data"):
        sys.exit(1)

    if not executer_etape("format/format_categories.py", "Génération Catégories"):
        sys.exit(1)

    if not executer_etape("format/format_timeline.py", "Génération Timeline"):
        sys.exit(1)

    if not executer_etape("format/format_comparaison.py", "Génération Comparaison"):
        sys.exit(1)

    end_time = time.time()
    duration = round(end_time - start_time, 2)
    
    print("\n==========================================")
    print(f"✨ PIPELINE TERMINÉ AVEC SUCCÈS")
    print(f"⏱️  Durée totale : {duration} secondes")
    print(f"📂 Prêt pour affichage : web/info.html")
    print("==========================================")

if __name__ == "__main__":
    principal()