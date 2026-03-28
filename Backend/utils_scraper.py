import re

import requests
from recipe_scrapers import scrape_html


def extract_recipe_from_url(url: str):
    """
    Extracts recipe data from a given URL using recipe-scrapers library.
    Fetches HTML manually to support generic Schema.org sites (wild_mode equivalent).
    """
    try:
        # Fetch HTML content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html_content = response.text

        # Use scrape_html with supported_only=False to allow generic Schema.org scraping
        scraper = scrape_html(html=html_content, org_url=url, supported_only=False)

        title = scraper.title()
        image = scraper.image()

        # Servings parsing
        try:
            yields = scraper.yields()
            servings = parse_servings(yields)
        except:
            servings = 2

        # Ingredients parsing
        ingredients = []
        try:
            raw_ingredients = scraper.ingredients()
            for raw in raw_ingredients:
                parsed = parse_ingredient_string(raw)
                ingredients.append(parsed)
        except:
            pass

        # Instructions parsing
        instructions = []
        try:
            raw_instructions = scraper.instructions()
            if raw_instructions:
                # Split by newlines if it's a big block
                instructions = raw_instructions.split('\n')
                # Clean up empty strings
                instructions = [i.strip() for i in instructions if i.strip()]
        except:
            pass

        return {
            "title": title,
            "ingredients": ingredients,
            "instructions": instructions,
            "servings": servings,
            "image_url": image,
            "source_url": url
        }

    except Exception as e:
        print(f"Scraping error: {str(e)}")
        # Raise generic message for UI
        raise Exception(f"Tarif çekilemedi: {str(e)}")

def parse_servings(yields):
    if not yields:
        return 2
    match = re.search(r'\d+', str(yields))
    if match:
        return int(match.group())
    return 2

def parse_ingredient_string(text):
    """
    Parses a string like '2 su bardağı şeker' into {amount, unit, name}.
    """
    text = text.strip()

    # 1. Extract amount (number at start)
    # Matches: "2", "2.5", "2,5", "1/2" (basic fraction)
    amount = 1.0
    amount_match = re.match(r'^([\d\.\,]+)\s*(.*)', text)

    rest = text
    if amount_match:
        amount_str = amount_match.group(1).replace(',', '.')
        try:
            amount = float(amount_str)
            rest = amount_match.group(2).strip()
        except ValueError:
            pass

    # 2. Extract Unit (Longest match wins)
    # Define known units and their standard representation
    # Order matters: longer phrases first to avoid partial matches
    unit_map = {
        'su bardağı': 'bardak',
        'çay bardağı': 'çay bardağı',
        'yemek kaşığı': 'yemek kaşığı',
        'tatlı kaşığı': 'tatlı kaşığı',
        'çay kaşığı': 'çay kaşığı',
        'kahve fincanı': 'kahve fincanı',
        'paket': 'paket',
        'adet': 'adet',
        'tane': 'adet',
        'diş': 'diş',
        'demet': 'demet',
        'tutam': 'tutam',
        'bardak': 'bardak',
        'kaşık': 'kaşık',
        'kase': 'kase',
        'kilo': 'kg',
        'kilogram': 'kg',
        'gram': 'g',
        'gr': 'g',
        'ml': 'ml',
        'litre': 'l',
        'lt': 'l',
        'cup': 'bardak',
        'tbsp': 'yemek kaşığı',
        'tsp': 'çay kaşığı',
    }

    found_unit = 'adet'
    is_special = True

    # Try to find a unit at the beginning of 'rest'
    # We sort keys by length descending to match 'su bardağı' before 'su' (if 'su' was a unit)
    sorted_units = sorted(unit_map.keys(), key=len, reverse=True)

    lower_rest = rest.lower()

    for unit_key in sorted_units:
        # Check if the remaining string starts with this unit
        # We add a space check or end of string check to avoid partial word matches
        if lower_rest.startswith(unit_key):
            # Verify it's a whole word match?
            # e.g. "gram" matches "gramofon" -> need boundary check
            # For simplicity, check if next char is space or end of string
            after_unit = lower_rest[len(unit_key):]
            if not after_unit or after_unit[0].isspace() or after_unit[0] in ['.', ',']:
                found_unit = unit_map[unit_key]

                # Update rest to be everything after the unit
                rest = rest[len(unit_key):].strip()

                # Check formatting of rest (remove leading dots etc)
                rest = rest.lstrip('.,- ')

                # Determine if special unit (standard ones imply not special)
                if found_unit in ['kg', 'g', 'l', 'ml']:
                    is_special = False
                elif found_unit in ['bardak', 'yemek kaşığı', 'çay kaşığı', 'tatlı kaşığı', 'çay bardağı']:
                    # Assuming these are standard enough or user can pick them
                    is_special = False # Actually UI treats 'bardak' as special unit potentially?
                    # Let's check logic: is_special_unit=True usually means "not a weight/volume"
                    # But if we have a selector for them, we might want consistent handling.
                    # For now, let's say volume/weight = False, others = True?
                    # Actually looking at AddRecipe.tsx logic, unit selector has limited options.
                    pass

                break

    name = rest

    # Clean up name
    # Remove common noise words if they appear at start
    noise_words = ['bir', 'iki', 'üç', 'kadar']
    for noise in noise_words:
        if name.lower().startswith(noise + ' '):
            name = name[len(noise)+1:].strip()

    # Capitalize first letter
    if name:
        name = name[0].upper() + name[1:]

    return {
        "name": name,
        "amount": amount,
        "unit": found_unit,
        "is_special_unit": is_special
    }
