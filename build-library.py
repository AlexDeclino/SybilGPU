#!/usr/bin/env python3
"""
Scans the library folder and generates library.json

Folder structure: library/YEAR/ArcN/ARTISTNAME/

Run: python3 build-library.py

After running, edit library.json to add collection titles.
"""

import os
import json
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIBRARY_PATH = os.path.join(SCRIPT_DIR, 'library')
OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'library.json')

# Load existing library.json to preserve titles
existing_titles = {}
try:
    with open(OUTPUT_FILE, 'r') as f:
        existing = json.load(f)
        for col in existing.get('collections', []):
            key = f"{col['artist']}-{col['name']}-{col['year']}-{col['arc']}"
            existing_titles[key] = col['name']
except:
    pass

collections = []

# Scan year folders
for year in sorted(os.listdir(LIBRARY_PATH)):
    year_path = os.path.join(LIBRARY_PATH, year)
    if not os.path.isdir(year_path) or not re.match(r'^\d{4}$', year):
        continue

    # Scan arc folders
    for arc in sorted(os.listdir(year_path)):
        arc_path = os.path.join(year_path, arc)
        if not os.path.isdir(arc_path) or not re.match(r'^Arc\d+$', arc, re.I):
            continue

        arc_num = int(re.sub(r'^Arc', '', arc, flags=re.I))

        # Scan artist folders
        for artist in sorted(os.listdir(arc_path)):
            artist_path = os.path.join(arc_path, artist)
            if not os.path.isdir(artist_path):
                continue

            # Scan collection subfolders
            for collection in sorted(os.listdir(artist_path)):
                col_path = os.path.join(artist_path, collection)
                if not os.path.isdir(col_path):
                    continue

                # Find all image files
                images = []
                for f in sorted(os.listdir(col_path)):
                    if re.match(r'.*\.(png|jpg|jpeg|gif|svg)$', f, re.I):
                        images.append(f'library/{year}/{arc}/{artist}/{collection}/{f}')

                if images:
                    key = f"{artist}-{collection}-{year}-{arc_num}"
                    collections.append({
                        'name': existing_titles.get(key, collection),
                        'artist': artist,
                        'year': int(year),
                        'arc': arc_num,
                        'images': images
                    })

# Sort by year desc, then arc
collections.sort(key=lambda x: (-x['year'], x['arc']))

output = {'collections': collections}

with open(OUTPUT_FILE, 'w') as f:
    json.dump(output, f, indent=2)

print(f"Generated library.json with {len(collections)} collection(s):")
for col in collections:
    print(f"  - \"{col['name']}\" by {col['artist']} ({col['year']}, Arc {col['arc']}) - {len(col['images'])} images")
