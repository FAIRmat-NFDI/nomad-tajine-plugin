# Example tajine recipe

This is a simple example for a recipe for a Moroccan chicken tagine. It demonstrates the use of the `nomad-tajine` schema to store recipes containing multiple steps. Each step defines ingredients and kitchen tools.

Consult the [`nomad-tajine` documentation](https://fairmat-nfdi.github.io/nomad-tajine-plugin/) to learn more about the recipe schemas.

This example uploads contains one file (`tajine.archive.yaml`) that uses the `Recipe` class from the `nomad-tajine` schema. When uploaded to NOMAD, several entries for for the `Ingredient` classes will be created. Information about calory content and macronutrients will be looked up automatically using the [U.S. Department of Agriculture (USDA) Food API](https://fdc.nal.usda.gov/api-guide).
