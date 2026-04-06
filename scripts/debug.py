import json
import os

FILE_INPUT = "../data/data_brut/movies_raw.jsonl"

if os.path.exists(FILE_INPUT):
    with open(FILE_INPUT, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        if first_line:
            data = json.loads(first_line)
            print("--- ANALYSE DE LA PREMIÈRE LIGNE BRUTE ---")
            for key, value in data.items():
                print(f"Clé: {key} | Valeur: {value} | Type: {type(value)}")
        else:
            print("Le fichier est vide.")
else:
    print("Fichier introuvable.")