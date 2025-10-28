import re
from typing import Any

try:
    import requests
except Exception:
    raise RuntimeError('requests is required for recipe_fetcher.py')

API_URL = 'https://api.api-ninjas.com/v1/recipe'

_mass_units = {
    'g',
    'gram',
    'grams',
    'kg',
    'kilogram',
    'kilograms',
    'mg',
    'lb',
    'pound',
    'pounds',
    'oz',
    'ounce',
    'ounces',
}
_volume_units = {
    'ml',
    'milliliter',
    'milliliters',
    'l',
    'liter',
    'liters',
    'cup',
    'cups',
    'tbsp',
    'tablespoon',
    'tablespoons',
    'tsp',
    'teaspoon',
    'teaspoons',
    'tb',
    'pt',
    'c',
}
_piece_units = {
    'clove',
    'cloves',
    'piece',
    'pieces',
    'bay',
    'pod',
    'pods',
    'slice',
    'slices',
}

QTY_RE = re.compile(
    r'^\s*(?P<qty>\d+\s+\d+\/\d+|\d+\/\d+|\d+[\.\d]*)\s*(?P<unit>[A-Za-z]+)?\s*(?:of\s+)?(?P<name>.+)$'
)


def fetch_recipe(
    name: str, api_key: str | None = None, limit: int = 1
) -> list[dict[str, Any]]:
    headers = {}
    if api_key:
        headers['X-Api-Key'] = api_key

    params = {'query': name, 'limit': limit}

    try:
        r = requests.get(API_URL, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f'API request failed: {e}')
        return []


def _split_ingredients(ingredients_raw: Any) -> list[str]:
    if not ingredients_raw:
        return []

    parts = []

    if isinstance(ingredients_raw, list):
        for line in ingredients_raw:
            s = str(line).strip()  
            if s and not (s.startswith('===') and s.endswith('===')):
                parts.append(s)

    elif isinstance(ingredients_raw, str):
        for chunk in ingredients_raw.split('|'):
            stripped_chunk = chunk.strip() 
            
            if not stripped_chunk:
                continue
            if stripped_chunk.startswith('===') and stripped_chunk.endswith('==='):
                continue

            for sub in stripped_chunk.split('\n'): 
                s = sub.strip()
                if s:
                    parts.append(s)

    return parts


def _parse_ingredient_line(line: str) -> dict[str, Any]:
    m = QTY_RE.match(line)
    if not m:
        return {'name': line}

    qty = m.group('qty')
    unit = (m.group('unit') or '').lower()
    name = m.group('name').strip()

    qty_value = None
    try:
        if ' ' in qty and '/' in qty:  # handle "1 1/2"
            whole, frac = qty.split(' ', 1)
            num, den = frac.split('/', 1)
            qty_value = float(whole) + (float(num) / float(den))
        elif '/' in qty:  # handle "1/2"
            num, den = qty.split('/', 1)
            qty_value = float(num) / float(den)
        else:  # handle "1" or "1.5"
            qty_value = float(qty)
    except Exception:
        try:
            qty_value = float(qty.split(' ')[0])
        except Exception:
            qty_value = None

    result = {'name': name}
    if qty_value is None:
        result['name'] = line
        return result

    m_def_schema_package = 'nomad_tajine_plugin.schema_packages.schema_package'
    if unit in _mass_units:
        result['m_def'] = m_def_schema_package + '.IngredientAmount'
        result['mass'] = qty_value
        result['unit'] = unit
    elif unit in _volume_units:
        result['m_def'] = m_def_schema_package + '.IngredientVolume'
        result['volume'] = qty_value
        result['unit'] = unit
    elif unit in _piece_units or unit.endswith('s') or unit == 'whole':
        result['m_def'] = m_def_schema_package + '.IngredientPiece'
        result['pieces'] = int(qty_value) if qty_value.is_integer() else qty_value
        result['unit'] = unit
    else:
        # Fallback for unknown units (like "whole")
        result['m_def'] = m_def_schema_package + '.IngredientPiece'
        result['pieces'] = int(qty_value) if qty_value.is_integer() else qty_value
        result['unit'] = unit
    return result


def _parse_instructions(instructions_raw: str) -> list[dict[str, Any]]:
    """
    Parses the raw instruction string into a list of steps.
    Handles two formats:
    1. (Paella-style): A single block of text. Splits by sentence.
    2. (Lentil Soup-style): A numbered list. Splits by number and removes prefix.
    """
    if not instructions_raw:
        return []

    parts = []
    text = instructions_raw.strip()

    # 1. Check for numeric list format (e.g., "1. Do this", "2. Do that")
    numeric_split_pattern = r'(?=\d+\.\s*)'
    numeric_steps = re.split(numeric_split_pattern, text)

    # Filter out empty strings that re.split might create (if text starts with "1.")
    cleaned_numeric_steps = [s.strip() for s in numeric_steps if s and s.strip()]

    # Check if this split was "successful"
    # Successful means > 1 step, OR 1 step that *starts* with "1."
    is_numeric_format = False
    if cleaned_numeric_steps:
        if len(cleaned_numeric_steps) > 1:
            is_numeric_format = True
        elif re.match(r'^\d+\.\s*', cleaned_numeric_steps[0]):
            is_numeric_format = True

    if is_numeric_format:
        for step_text in cleaned_numeric_steps:
            cleaned_text = re.sub(r'^\d+\.\s*', '', step_text).strip()
            if cleaned_text:
                parts.append({'instruction': cleaned_text})

    elif cleaned_numeric_steps:
        full_text = cleaned_numeric_steps[0]
        sentence_split_pattern = r'(?<=[.!?])\s+'
        sentence_steps = re.split(sentence_split_pattern, full_text)

        for step_text in sentence_steps:
            cleaned_text = step_text.strip()
            if cleaned_text:
                parts.append({'instruction': cleaned_text})

    return parts


def _parse_servings(servings_raw: str) -> int | None:
    if not servings_raw:
        return None
    m = re.search(r'(\d+)', servings_raw)
    if m:
        return int(m.group(1))
    return None


def populate_recipe_if_empty(
    data: dict[str, Any], api_key: str | None = None
) -> dict[str, Any]:
    name = data.get('name')
    if not name:
        return data

    existing_steps = data.get('steps')
    if existing_steps:
        return data

    # fetching
    try:
        recipes = fetch_recipe(name=name, api_key=api_key, limit=1)
    except Exception:
        return data

    if not recipes:
        return data

    recipe = recipes[0]
    title = recipe.get('title')
    servings_raw = recipe.get('servings')

    ingredients_raw_or_list = recipe.get('ingredients', [])
    instructions_raw = recipe.get('instructions', '')

    ingredients_lines = _split_ingredients(ingredients_raw_or_list)
    ingredients = [_parse_ingredient_line(line) for line in ingredients_lines]

    steps = _parse_instructions(instructions_raw)
    if steps and ingredients:
        steps[0].setdefault('ingredients', ingredients)
    elif ingredients:
        steps = [{'instruction': instructions_raw or title, 
                  'ingredients': ingredients}]

    # populate top-level fields conservatively
    if title and not data.get('summary'):
        data['summary'] = f'{title}'
    if servings_raw and not data.get('number_of_servings'):
        data['number_of_servings'] = _parse_servings(servings_raw)
    if not data.get('steps'):
        data['steps'] = steps

    data.setdefault('_fetched_recipe_meta', {})['api_ninjas_raw_title'] = title
    return data
