import json
import os
import re
import urllib.request
from datetime import datetime

SPORTSTATS_URL = "https://sportstats.one/profile/273616"
RUNS_JSON_PATH = "data/runs.json"
MANUAL_RUNS_PATH = "data/manual_runs.json"

def format_time(ms):
    seconds = ms // 1000
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def fetch_sportstats_data():
    """
    Scrape data from Sportstats profile.
    """
    print(f"Fetching from {SPORTSTATS_URL}...")
    req = urllib.request.Request(
        SPORTSTATS_URL, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
        runs = []
        
        # Le contenu est échappé dans la payload Next.js.
        # On utilise une regex pour extraire directement les informations pertinentes des courses.
        pattern = r'\\"elbl\\":\\"([^\\"]+)\\".*?\\"dts\\":(\d+).*?\\"rd\\":(\d+).*?\\"rlbl\\":\\"([^\\"]+)\\".*?\\"pt\\":(\d+)'
        matches = re.findall(pattern, html)
        
        for match in matches:
            event_name = match[0]
            dts = int(match[1])
            distance_m = int(match[2])
            race_label = match[3]
            time_ms = int(match[4])
            
            # Formater la date
            date_str = datetime.fromtimestamp(dts).strftime('%Y-%m-%d')
            
            # Titre final
            title = f"{event_name} - {race_label}".strip(" -")
            
            # Distance
            distance = f"{distance_m / 1000:.1f} km"
            
            # Temps
            time_str = format_time(time_ms)
            
            runs.append({
                "date": date_str,
                "event_name": title,
                "distance": distance,
                "time": time_str,
                "source": "Sportstats",
                "url": SPORTSTATS_URL
            })

        print(f"Found {len(runs)} runs from Sportstats.")
        return runs
    except Exception as e:
        print(f"Error fetching from Sportstats: {e}")
        return []

def load_manual_runs():
    if os.path.exists(MANUAL_RUNS_PATH):
        with open(MANUAL_RUNS_PATH, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def main():
    # 1. Fetch from Sportstats
    sportstats_runs = fetch_sportstats_data()
    
    # 2. Load manual runs
    manual_runs = load_manual_runs()
    
    # 3. Merge intelligently
    unique_runs = {}
    
    # D'abord on ajoute les courses de Sportstats
    for run in sportstats_runs:
        key = f"{run['date']}_{run['event_name']}"
        unique_runs[key] = run
        
    # Ensuite on ajoute ou fusionne les courses manuelles
    for run in manual_runs:
        key = f"{run['date']}_{run['event_name']}"
        if key in unique_runs:
            # Si la course existe déjà (ex: récupérée sur Sportstats),
            # on met à jour les champs personnalisés (ex: elevation)
            for k, v in run.items():
                if v is not None and v != "":
                    # On évite d'écraser la source avec "Manuel" si c'est Sportstats, 
                    # mais on le fait si on le veut vraiment. 
                    # Pour l'instant on écrase tout, sauf si c'est source:Manuel qui remplacerait Sportstats
                    if k == "source" and unique_runs[key]["source"] == "Sportstats":
                        continue
                    unique_runs[key][k] = v
        else:
            unique_runs[key] = run
            
    final_runs = list(unique_runs.values())
    
    # Sort by date descending
    final_runs.sort(key=lambda x: x['date'], reverse=True)
    
    # 4. Save to runs.json
    os.makedirs(os.path.dirname(RUNS_JSON_PATH), exist_ok=True)
    with open(RUNS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_runs, f, indent=2, ensure_ascii=False)
        
    print(f"\nSuccessfully saved {len(final_runs)} runs to {RUNS_JSON_PATH}")
    
    # Print for the user to see
    print("\n--- Aperçu des données récupérées ---")
    for r in final_runs:
        elevation = f" [⛰️ {r['elevation']}]" if 'elevation' in r else ""
        print(f"- {r['date']} : {r['event_name']} ({r['distance']} en {r['time']}){elevation} [Source: {r['source']}]")

if __name__ == "__main__":
    main()
