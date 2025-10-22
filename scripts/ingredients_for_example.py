from pathlib import Path

import yaml

# Output folder: relative to this script
OUT_DIR = (
    Path(__file__).parent.parent
    / 'src/nomad_tajine_plugin/example_uploads/example/ingredients'
)
print(OUT_DIR)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Ingredient data: name → {density (g/L), kcal, fat, protein, carbs}
INGREDIENTS = {
    'All-purpose Flour': {
        'density': 590,
        'kcal': 364,
        'fat': 1,
        'protein': 10,
        'carbs': 76,
        'diet_type': 'VEGETARIAN',
    },
    'Bone-in Skin-on Chicken Thighs': {
        'density': 1050,
        'kcal': 209,
        'fat': 11,
        'protein': 26,
        'carbs': 0,
        'diet_type': 'ANIMAL_PRODUCT',
    },
    'Carrots': {
        'density': 640,
        'kcal': 41,
        'fat': 0.2,
        'protein': 0.9,
        'carbs': 10,
        'diet_type': 'VEGAN',
    },
    'Cayenne Pepper': {
        'density': 510,
        'kcal': 318,
        'fat': 17,
        'protein': 12,
        'carbs': 56,
        'diet_type': 'VEGAN',
    },
    'Chicken Broth': {
        'density': 1010,
        'kcal': 5,
        'fat': 0,
        'protein': 1,
        'carbs': 0.3,
        'diet_type': 'ANIMAL_PRODUCT',
    },
    'Fresh Cilantro Leaves': {
        'density': 110,
        'kcal': 23,
        'fat': 0.5,
        'protein': 2.1,
        'carbs': 3.7,
        'diet_type': 'VEGAN',
    },
    'Garlic': {
        'density': 640,
        'kcal': 149,
        'fat': 0.5,
        'protein': 6.4,
        'carbs': 33,
        'diet_type': 'VEGAN',
    },
    'Greek Cracked Green Olives': {
        'density': 920,
        'kcal': 145,
        'fat': 15,
        'protein': 1,
        'carbs': 4,
        'diet_type': 'VEGAN',
    },
    'Ground Black Pepper': {
        'density': 560,
        'kcal': 251,
        'fat': 3,
        'protein': 10,
        'carbs': 64,
        'diet_type': 'VEGAN',
    },
    'Ground Cinnamon': {
        'density': 560,
        'kcal': 247,
        'fat': 1,
        'protein': 4,
        'carbs': 81,
        'diet_type': 'VEGAN',
    },
    'Ground Coriander': {
        'density': 500,
        'kcal': 298,
        'fat': 13,
        'protein': 12,
        'carbs': 55,
        'diet_type': 'VEGAN',
    },
    'Ground Cumin': {
        'density': 450,
        'kcal': 375,
        'fat': 22,
        'protein': 18,
        'carbs': 44,
        'diet_type': 'VEGAN',
    },
    'Ground Ginger': {
        'density': 470,
        'kcal': 335,
        'fat': 6,
        'protein': 8,
        'carbs': 71,
        'diet_type': 'VEGAN',
    },
    'Honey': {
        'density': 1420,
        'kcal': 304,
        'fat': 0,
        'protein': 0.3,
        'carbs': 82,
        'diet_type': 'VEGETARIAN',
    },
    'Large Yellow Onion': {
        'density': 630,
        'kcal': 40,
        'fat': 0.1,
        'protein': 1.1,
        'carbs': 9,
        'diet_type': 'VEGAN',
    },
    'Lemon': {
        'density': 980,
        'kcal': 29,
        'fat': 0.3,
        'protein': 1.1,
        'carbs': 9,
        'diet_type': 'VEGAN',
    },
    'Olive Oil': {
        'density': 910,
        'kcal': 884,
        'fat': 100,
        'protein': 0,
        'carbs': 0,
        'diet_type': 'VEGAN',
    },
    'Paprika': {
        'density': 560,
        'kcal': 282,
        'fat': 13,
        'protein': 14,
        'carbs': 54,
        'diet_type': 'VEGAN',
    },
    'Salt': {
        'density': 1200,
        'kcal': 0,
        'fat': 0,
        'protein': 0,
        'carbs': 0,
        'diet_type': 'VEGAN',
    },
}


def slugify(name: str) -> str:
    """Convert a name like 'All-purpose Flour' → 'all-purpose_flour'."""
    return name.lower().replace(' ', '_').replace(',', '')


for name, vals in INGREDIENTS.items():
    filename = OUT_DIR / f'{slugify(name)}.archive.yaml'

    data = {
        'data': {
            'm_def': 'nomad_tajine_plugin.schema_packages.schema_package.Ingredient',
            'name': name,
            'diet_type': vals['diet_type'],
            'density': vals['density'],
            'calories_per_100_g': vals['kcal'],
            'fat_per_100_g': vals['fat'],
            'protein_per_100_g': vals['protein'],
            'carbohydrates_per_100_g': vals['carbs'],
        }
    }

    with filename.open('w', encoding='utf-8') as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)

    print(f'✅ Created {filename.name}')

print('\nAll ingredient .archive.yaml files generated successfully.')
