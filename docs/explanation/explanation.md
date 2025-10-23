# Explanation

This plugin implements schemas for structuring data for ingredients, recipes,
cooking steps, and an ELN for scaling existing recipes for different number of
servings. Read more about the implementations
[here](../reference/schemas.md#schemas).

## USDA Nutrient Lookup

!!! attention "Attention"
    The nutrient lookup feature is experimental and may not always return accurate results. This depends on the response from the USDA FoodData Central API and how well the entered ingredient name matches items in their database.

The Tajine plugin can connect to the USDA FoodData Central API to fetch
nutritional information for ingredients. Currently it searches through the _SR Legacy_ database, as this has the most uniform description of nutrients. See here for more information on how to setup your Oasis with the API key: [How to install this plugin](../how_to/install_this_plugin.md#adding-the-usda-nutrient-lookup).

When adding a new ingredient entry and saving the entry, the normalizer will run. This normalizer takes the string entered in the `name` field of the ingredient entry and queries the USDA API for matching food items. If a match is found, the nutritional information from the USDA database is automatically populated into the corresponding fields of the ingredient entry.

Depending on the USDA's food category of the matched item, it is classified as 
- `vegan`
- `vegetarian`
- `omnivorous`
- `ambiguous` (for categories like `sweets`, `snacks`, ... that might contain animal products)

The matched foods unique FDC ID and NDB ID are also stored in the ingredient entry for reference. Here you can check and make sure the ingredient's nutrients actually match what you intended to add.

If multiple matches are found, the normalizer takes the **first** entry! This can and should be modified in the future to improve the matching process.

If no matches are found, the ingredient entry remains unchanged and no nutrients are added. 