import requests
import json
import os
from pathlib import Path
from dotenv import dotenv_values
from rapidfuzz import fuzz

# Load .env from the same directory as this script so running from any CWD works.
env_path = Path(__file__).resolve().parent / '.env'
config = dotenv_values(str(env_path))
# Prefer .env value, then environment variable fallback.
API_KEY = config.get('USDA_API_KEY') or os.environ.get('USDA_API_KEY')
if not API_KEY:
    raise RuntimeError(
        f'USDA API key not found. Looked in {env_path} and environment variables. Please set USDA_API_KEY.'
    )

FOOD_CATEGORY_CLASSIFICATION = {
    # --------------------------------------------------------------------
    # ANIMAL_PRODUCT: Categories that are inherently meat, poultry, or fish.
    # --------------------------------------------------------------------
    'Poultry Products': 'ANIMAL_PRODUCT',
    'Sausages and Luncheon Meats': 'ANIMAL_PRODUCT',
    'Pork Products': 'ANIMAL_PRODUCT',
    'Beef Products': 'ANIMAL_PRODUCT',
    'Finfish and Shellfish Products': 'ANIMAL_PRODUCT',
    'Lamb, Veal, and Game Products': 'ANIMAL_PRODUCT',
    # --------------------------------------------------------------------
    # VEGETARIAN: Non-meat animal products. Not vegan.
    # --------------------------------------------------------------------
    'Dairy and Egg Products': 'VEGETARIAN',
    'Breakfast Cereals': 'VEGETARIAN',  # (May contain honey, milk, or Vit. D3 from lanolin)
    'Beverages': 'VEGETARIAN',  # (e.g., soy milk vs. dairy milk)
    'Sweets': 'VEGETARIAN',  # (May contain gelatin, milk, eggs, honey) debatable
    'Cereal Grains and Pasta': 'VEGETARIAN',  # (e.g., plain pasta vs. egg pasta)
    'Alcoholic Beverages': 'VEGETARIAN',  # (May be fined with animal products)
    # --------------------------------------------------------------------
    # VEGAN: Categories that are inherently plant-based.
    # --------------------------------------------------------------------
    'Spices and Herbs': 'VEGAN',
    'Fruits and Fruit Juices': 'VEGAN',
    'Vegetables and Vegetable Products': 'VEGAN',
    'Nut and Seed Products': 'VEGAN',
    'Legumes and Legume Products': 'VEGAN',
    # --------------------------------------------------------------------
    # AMBIGUOUS: These categories are too broad. A product from this
    # category could be vegan, vegetarian, or contain meat.
    # You MUST check the specific ingredients.
    # --------------------------------------------------------------------
    'Baby Foods': 'AMBIGUOUS',
    'Fats and Oils': 'AMBIGUOUS',  # (e.g., olive oil vs. lard)
    'Soups, Sauces, and Gravies': 'AMBIGUOUS',  # (e.g., tomato soup vs. beef gravy)
    'Baked Products': 'AMBIGUOUS',  # (May contain eggs, butter, milk)
    'Fast Foods': 'AMBIGUOUS',
    'Meals, Entrees, and Side Dishes': 'AMBIGUOUS',
    'Snacks': 'AMBIGUOUS',
    'American Indian/Alaska Native Foods': 'AMBIGUOUS',
    'Restaurant Foods': 'AMBIGUOUS',
    'Branded Food Products Database': 'AMBIGUOUS',
    'Quality Control Materials': 'AMBIGUOUS',
    'Unknown': 'AMBIGUOUS',
}


def get_usda_data(
    ingredient_name,
):
    """
    Finds a food by its name and returns its calorie count.
    """
    print(f'Searching for ingredient: {ingredient_name}...')

    search_url = 'https://api.nal.usda.gov/fdc/v1/foods/search'
    search_params = {
        'query': ingredient_name,
        'dataType': ['SR Legacy'],
        'pageSize': 1000,
        'api_key': API_KEY,
    }

    result = {}
    try:
        response = requests.get(search_url, params=search_params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        search_data = response.json()

        if not search_data.get('foods'):
            print(f"Error: No food found for ingredient '{ingredient_name}'")
            return
        # Initialize variables to store the best match
        best_score = -1  # Start with -1 so any score (0-100) will be higher
        best_food = None

        # The ingredient name to search for
        # ingredient_name = "your_ingredient"
        # search_data = {'foods': [...]}

        # for food in search_data['foods']:
        #     # Get the description, default to empty string if missing
        #     food_description = food.get('description', '').lower()

        #     # Calculate the similarity score
        #     score = fuzz.ratio(ingredient_name.lower(), food_description)

        #     # If this food's score is higher than the current best, update it
        #     if score > best_score:
        #         best_score = score
        #         best_food = food

        # After the loop, 'best_food' will be the item with the highest score
        if not best_food:
            print('No food items were processed.')
            food = search_data['foods'][
                0
            ]  # Fallback to the first item if none processed
        food_category = food.get('foodCategory', 'Unknown')
        diet_type = FOOD_CATEGORY_CLASSIFICATION.get(
            food_category, 'AMBIGUOUS'
        )
        result['food_category'] = food_category
        result['diet_type'] = diet_type
        fdc_id = food.get('fdcId')
        result['fdc_id'] = fdc_id
        ndb_id = food.get('ndbNumber')
        result['ndb_id'] = ndb_id
        # Get nutrients
        nutrients = food.get('foodNutrients', [])
        for nutrient in nutrients:
            if nutrient.get('nutrientId') == 1003:  # 1003 is the ID for "Protein"
                result['protein'] = nutrient.get('value')
            elif (
                nutrient.get('nutrientId') == 1004
            ):  # 1004 is the ID for "Total lipid (fat)"
                result['fat'] = nutrient.get('value')
            elif (
                nutrient.get('nutrientId') == 1005
            ):  # 1005 is the ID for "Carbohydrate, by difference"
                result['carbohydrates'] = nutrient.get('value')
            elif (
                nutrient.get('nutrientId') == 1008
            ):  # 1008 is the ID for energy in kcal
                result['calories_kcal'] = nutrient.get('value')
        description = food.get('description')
        print(
            f"Found Food: '{description}' with FDC ID: {fdc_id} and Category: {food_category},  diet type: {diet_type}"
        )
        return result

    except requests.exceptions.RequestException as e:
        print(f'An error occurred during search: {e}')
        return
    except json.JSONDecodeError:
        print('Error: Could not decode JSON response from search API.')
        return


# def get_calories_by_ndb(api_key, ndb_number):
#     """
#     Finds a food by its NDB number and returns its calorie count.
#     """
#     print(f'Searching for NDB Number: {ndb_number}...')

#     # --- Step 1: Search for the food by NDB number to get its FDC ID ---
#     # The NDB number is stored in the 'SR Legacy' data type. We search for
#     # the number within that specific data type.
#     search_url = 'https://api.nal.usda.gov/fdc/v1/foods/search'
#     search_params = {
#         'query': ndb_number,
#         'dataType': ['SR Legacy'],  # SR Legacy is the old NDB
#         'api_key': api_key,
#     }

#     try:
#         response = requests.get(search_url, params=search_params)
#         response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
#         search_data = response.json()

#         # Check if any food was found
#         if not search_data.get('foods'):
#             print(f'Error: No food found for NDB number {ndb_number}')
#             return

#         # Find the exact match for the NDB number
#         target_food = None
#         for food in search_data['foods']:
#             # The NDB number is stored in the 'ndbNumber' field
#             if food.get('ndbNumber') == int(ndb_number):
#                 target_food = food
#                 break

#         if not target_food:
#             print(
#                 f'Error: Could not find an exact match for NDB {ndb_number} in search results.'
#             )
#             return

#         fdc_id = target_food.get('fdcId')
#         description = target_food.get('description')
#         print(f"Found Food: '{description}' with FDC ID: {fdc_id}")

#     except requests.exceptions.RequestException as e:
#         print(f'An error occurred during search: {e}')
#         return
#     except json.JSONDecodeError:
#         print('Error: Could not decode JSON response from search API.')
#         return

#     # --- Step 2: Fetch the full food details using the FDC ID ---
#     print(f'Fetching details for FDC ID: {fdc_id}...')
#     details_url = f'https://api.nal.usda.gov/fdc/v1/food/{fdc_id}'
#     details_params = {'api_key': api_key}

#     try:
#         response = requests.get(details_url, params=details_params)
#         response.raise_for_status()
#         food_details = response.json()

#         # --- Step 3: Find the calorie information in the nutrient list ---
#         calories = None
#         # foodNutrients is a list of all nutrients for that food
#         for nutrient in food_details.get('foodNutrients', []):
#             # We are looking for "Energy", which is measured in "KCAL"
#             if (
#                 nutrient['nutrient']['name'] == 'Energy'
#                 and nutrient['nutrient']['unitName'].upper() == 'KCAL'
#             ):
#                 calories = nutrient.get('amount')
#                 break

#         if calories is not None:
#             print('\n--- Result ---')
#             print(f'Food: {food_details.get("description")}')
#             print(f'Calories: {calories} kcal per 100g')
#             print('--------------')
#         else:
#             print(
#                 'Error: Calorie information (Energy in KCAL) not found for this food.'
#             )

#     except requests.exceptions.RequestException as e:
#         print(f'An error occurred while fetching details: {e}')
#     except json.JSONDecodeError:
#         print('Error: Could not decode JSON response from details API.')


if __name__ == '__main__':
    result = get_usda_data('budasdasdtter')
    print(result)
