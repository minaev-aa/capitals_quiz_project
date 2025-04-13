# quiz_app/csv_utils.py
"""Обработка csv файлов - чтение и запись"""
import csv
import os
from django.conf import settings

COUNTRIES_FILE = os.path.join(settings.DATA_DIR, 'countries_capitals.csv')
LEADERS_FILE = os.path.join(settings.DATA_DIR, 'leaders.csv')

def initialize_csv_files():
    """Открытие файлов"""
    if not os.path.exists(COUNTRIES_FILE) or os.path.getsize(COUNTRIES_FILE) == 0:
        with open(COUNTRIES_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['country', 'capital', 'image_path'])

    if not os.path.exists(LEADERS_FILE) or os.path.getsize(LEADERS_FILE) == 0:
        with open(LEADERS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'score'])

initialize_csv_files()


def read_countries():
    """Чтение страны"""
    countries = []
    try:
        with open(COUNTRIES_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                countries.append(row)
    except FileNotFoundError:
        print(f"Error: File not found at {COUNTRIES_FILE}")
        return []
    except UnicodeDecodeError as e:
        print(f"Encoding Error: {e} while reading {COUNTRIES_FILE}. Checking file encoding.")
        return []
    return countries

def write_country(country, capital, image_path):
    """Запись страны"""
    with open(COUNTRIES_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([country, capital, image_path])

def read_leaders():
    """Чтение лидеров"""
    leaders = []
    try:
        with open(LEADERS_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row['score'] = int(row['score'].strip())
                except (ValueError, TypeError, KeyError):
                    row['score'] = 0
                row['name'] = row.get('name', 'Unknown').strip()
                leaders.append(row)
    except FileNotFoundError:
        print(f"Error: File not found at {LEADERS_FILE}")
        return []
    except UnicodeDecodeError as e:
        print(f"Encoding Error: {e} while reading {LEADERS_FILE}. Try checking the file encoding.")
        return []
    leaders.sort(key=lambda x: x['score'], reverse=True)
    return leaders

def write_leader(name, score):
    """Запись лидеров"""
    leaders = read_leaders()
    found = False
    for leader in leaders:
        if leader['name'].lower() == name.lower():
            if score > leader['score']:
                leader['score'] = score
            found = True
            break

    if not found:
        leaders.append({'name': name, 'score': score})

    leaders.sort(key=lambda x: x['score'], reverse=True)

    with open(LEADERS_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'score'])
        writer.writeheader()
        writer.writerows(leaders)
