from typing import (
    TYPE_CHECKING,
)

from nomad.datamodel.metainfo.basesections import (
    ActivityStep,
    BaseSection,
    Entity,
    EntityReference,
    Instrument,
)
from nomad.metainfo.metainfo import Section, SubSection
from nomad.units import ureg

from nomad_tajine_plugin.utils import create_archive

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad.config import config
from nomad.datamodel.data import Schema, UseCaseElnCategory
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.metainfo import MEnum, Quantity, SchemaPackage

configuration = config.get_plugin_entry_point(
    'nomad_tajine_plugin.schema_packages:schema_tajine_entry_point'
)

m_package = SchemaPackage()


def format_lab_id(lab_id: str):
    return lab_id.lower().replace(' ', '_').replace(',', '')


class Ingredient(Entity, Schema):
    """
    An ingredient used in cooking recipes.
    """

    m_def = Section(
        label='Ingredient Type',
        categories=[UseCaseElnCategory],
    )

    density = Quantity(
        type=float,
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
        unit='kg/L',
    )

    weight_per_piece = Quantity(
        type=float,
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
        unit='kg',
    )

    diet_type = Quantity(
        type=MEnum(
            'ANIMAL_PRODUCT',
            'VEGETARIAN',
            'VEGAN',
            'AMBIGUOUS',
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
    )

    calories_per_100_g = Quantity(
        type=float,
        unit='kcal',
        description='Nutrients per 100 g for this ingredient type imported from USDA.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='kcal'
        ),
    )

    fat_per_100_g = Quantity(
        type=float,
        unit='g',
        description='Nutrients per 100 g for this ingredient type imported from USDA.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='g'
        ),
    )

    protein_per_100_g = Quantity(
        type=float,
        unit='g',
        description='Nutrients per 100 g for this ingredient type imported from USDA.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='g'
        ),
    )

    carbohydrates_per_100_g = Quantity(
        type=float,
        unit='g',
        description='Nutrients per 100 g for this ingredient type imported from USDA.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='g'
        ),
    )

    fdc_id = Quantity(
        type=int,
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )

    ndb_id = Quantity(
        type=int,
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )

    def normalize(self, archive, logger: 'BoundLogger'):
        if not self.lab_id:
            self.lab_id = format_lab_id(self.name)
        else:
            self.lab_id = format_lab_id(self.lab_id)

        super().normalize(archive, logger)


class IngredientAmount(EntityReference):
    """
    Represents the amount of an ingredient in a recipe.
    """

    name = Quantity(
        type=str, a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity)
    )

    quantity = Quantity(
        type=float,
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
        # unit='minute',        # TODO: add custom units to pint custom unit registry
    )

    unit = Quantity(
        type=MEnum(
            'gram',
            'milliliter',
            'piece',
            'teaspoon',
            'tablespoon',
            'fluid ounce',
            'cup',
            'pint',
            'quart',
            'gallon',
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
    )

    mass = Quantity(
        type=float,
        unit='gram',
    )  # in [g], calculate from quantity, unit and density etc

    lab_id = Quantity(
        type=str,
        description="""An ID string that is unique at least for the lab that produced
            this data.""",
        a_eln=dict(component='StringEditQuantity', label='ingredient ID'),
    )

    reference = Quantity(
        type=Ingredient,
        description='A reference to a ingredient type entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='ingredient type reference',
        ),
    )

    diet_type = Quantity(
        type=MEnum(
            'ANIMAL_PRODUCT',
            'VEGETARIAN',
            'VEGAN',
            'AMBIGUOUS',
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
    )

    calories = Quantity(
        type=float,
        unit='kcal',
        description='Total calories of this ingredient.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='kcal',
            # properties= {'editable': False},
        ),
    )

    fat = Quantity(
        type=float,
        unit='g',
        description='Total fat of this ingredient.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='g'
        ),
    )

    protein = Quantity(
        type=float,
        unit='g',
        description='Total proteins of this ingredient.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='g'
        ),
    )

    carbohydrates = Quantity(
        type=float,
        unit='g',
        description='Total carbohydrates of this ingredient.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='g'
        ),
    )

    # preparation_notes = Quantity() or SubSection() TODO: discuss
    # TODO: discuss references

    def convert_volume(self, unit_volume):
        if self.reference.density:
            self.mass = (
                ureg.Quantity(unit_volume, 'milliliter')
                * self.quantity
                * self.reference.density
            )
        else:
            self.mass = None

    def convert_piece(self):
        if self.reference.weight_per_piece:
            self.mass = self.reference.weight_per_piece * self.quantity
        else:
            self.mass = None

    def calculate_nutrients(self, logger):
        for nutrient in ('calories', 'fat', 'protein', 'carbohydrates'):
            try:
                per_100_g_attr = f'{nutrient}_per_100_g'
                value_per_100_g = getattr(self.reference, per_100_g_attr)
                value = (self.mass * value_per_100_g / ureg.Quantity(100, 'gram')).to(
                    value_per_100_g.units
                )
                setattr(self, nutrient, value)
            except TypeError:
                logger.warn(
                    f'Failed to calculate {nutrient} for ingredient {self.name}',
                    exc_info=True,
                )

    def normalize(self, archive, logger: 'BoundLogger'):  # noqa: PLR0912
        """
        For the given ingredient name or ID, fetches the corresponding Ingredient entry.
        If not found, creates a new Ingredient entry. Converts the quantity to SI units
        based on the unit and ingredient properties like density or weight per piece.
        """
        if not self.lab_id:
            self.lab_id = format_lab_id(self.name)
        else:
            self.lab_id = format_lab_id(self.lab_id)

        super().normalize(archive, logger)

        if not self.reference:
            logger.debug('Ingredient entry not found. Creating a new one.')
            try:
                ingredient = Ingredient(
                    name=self.name,
                    lab_id=self.lab_id,
                )
                self.reference = create_archive(
                    ingredient,
                    archive,
                    f'{self.lab_id}.archive.json',
                    overwrite=False,
                )
            except Exception as e:
                logger.error(
                    'Failed to create Ingredient entry.', exc_info=True, error=e
                )

        if self.reference:
            unit = self.unit.replace(' ', '_')  # type: ignore
            match unit:
                # the values for teaspoon, tablespoon and cup come from
                # https://en.wikipedia.org/wiki/Cooking_weights_and_measures, which
                # in turn compiles them from '1896 Boston Cooking-School Cook Book'
                case 'gram':
                    self.mass = self.quantity
                case 'piece':
                    self.convert_piece()
                case 'teaspoon':
                    self.convert_volume(14.79)
                case 'tablespoon':
                    self.convert_volume(3.552)
                case 'cup':
                    self.convert_volume(236.588)
                case _:
                    if self.reference.density:
                        try:
                            self.mass = (
                                (ureg(unit).to(ureg.milliliter))
                                * self.quantity
                                * self.reference.density
                            )
                        except Exception as e:
                            logger.warn(f'Not able to convert common unit to [g], {e}')
                    else:
                        self.mass = None

            self.diet_type = self.reference.diet_type

            self.calculate_nutrients(logger)


class Tool(Instrument, Schema):
    """
    A kitchen tool or utensil used in cooking.
    """

    type = Quantity(
        type=str, a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity)
    )

    description = Quantity(
        type=str, a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity)
    )

    def normalize(self, archive, logger: 'BoundLogger'):
        if not self.lab_id:
            self.lab_id = format_lab_id(self.name)
        else:
            self.lab_id = format_lab_id(self.lab_id)

        super().normalize(archive, logger)


class RecipeStep(ActivityStep):
    """
    A single step in a cooking recipe.
    """

    duration = Quantity(
        type=float,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='minute'
        ),
        unit='minute',
    )

    tools = SubSection(
        section_def=Tool,
        description='',
        repeats=True,
    )

    ingredients = SubSection(
        section_def=IngredientAmount,
        description='',
        repeats=True,
    )

    instruction = Quantity(
        type=str, a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity)
    )


class HeatingCoolingStep(RecipeStep):
    """
    A recipe step that involves heating or cooling to a specific temperature.
    """

    temperature = Quantity(
        type=float,
        default=20.0,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='celsius'
        ),
        unit='celsius',
    )


class Recipe(BaseSection, Schema):
    """
    A schema representing a cooking recipe with ingredients, tools, and steps.
    """

    m_def = Section(
        label='Cooking Recipe',
        categories=[UseCaseElnCategory],
    )

    name = Quantity(
        type=str, a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity)
    )

    duration = Quantity(
        type=float,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='minute'
        ),
        unit='minute',
    )

    authors = Quantity(
        type=str, a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity)
    )

    difficulty = Quantity(
        type=MEnum(
            'easy',
            'medium',
            'hard',
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
    )

    number_of_servings = Quantity(
        type=int, a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity)
    )

    summary = Quantity(
        type=str, a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity)
    )

    cuisine = Quantity(
        type=str, a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity)
    )

    diet_type = Quantity(
        type=MEnum(
            'ANIMAL_PRODUCT',
            'VEGETARIAN',
            'VEGAN',
            'AMBIGUOUS',
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
    )

    calories = Quantity(
        type=float,
        unit='kcal',
        description='Total calories of this ingredient.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='kcal',
            # properties= {'editable': False},
        ),
    )

    fat = Quantity(
        type=float,
        unit='g',
        description='Total fat of this recipe.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='g'
        ),
    )

    protein = Quantity(
        type=float,
        unit='g',
        description='Total proteins of this recipe.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='g'
        ),
    )

    carbohydrates = Quantity(
        type=float,
        unit='g',
        description='Total carbohydrates of this recipe.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='g'
        ),
    )

    calories_per_serving = Quantity(
        type=float,
        unit='kcal',
        description='Calories per serving.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='kcal',
            # properties= {'editable': False},
        ),
    )

    fat_per_serving = Quantity(
        type=float,
        unit='g',
        description='Fats per serving.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='g',
            # properties= {'editable': False},
        ),
    )

    protein_per_serving = Quantity(
        type=float,
        unit='g',
        description='Proteins per serving.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='g',
            # properties= {'editable': False},
        ),
    )

    carbohydrates_per_serving = Quantity(
        type=float,
        unit='g',
        description='Carbohydrates per serving.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='g',
            # properties= {'editable': False},
        ),
    )

    duration = Quantity(
        type=float,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='minute',
            # properties= {'editable': False},
        ),
        unit='minute',
    )

    tools = SubSection(
        section_def=Tool,
        description='',
        repeats=True,
    )

    steps = SubSection(
        section_def=RecipeStep,
        description='',
        repeats=True,
    )

    ingredients = SubSection(
        section_def=IngredientAmount,
        description='',
        repeats=True,
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:  # noqa: PLR0912
        """
        Collects all ingredients and tools from steps and adds them to the recipe's
        ingredients and tools lists.
        """
        super().normalize(archive, logger)

        all_ingredients = []
        all_tools = []

        for step in self.steps:
            for ingredient in step.ingredients:
                # Check if ingredient with the same name exists
                existing = next(
                    (ing for ing in all_ingredients if ing.name == ingredient.name),
                    None,
                )

                if existing is None:
                    all_ingredients.append(ingredient)
                else:
                    # Sum quantities
                    new_quantity = (existing.quantity or 0) + (ingredient.quantity or 0)

                    # Sum nutrient values safely
                    nutrients = {}
                    for nutrient in ('calories', 'fat', 'protein', 'carbohydrates'):
                        nutrients[nutrient] = (getattr(existing, nutrient, 0) or 0) + (
                            getattr(ingredient, nutrient, 0) or 0
                        )

                    # Create a new ingredient with summed values
                    ingredient_summed = IngredientAmount(
                        name=existing.name,
                        quantity=new_quantity,
                        unit=existing.unit,
                        mass=None,  # optionally recalc
                        lab_id=existing.lab_id,
                        reference=existing.reference,
                        **nutrients,
                    )

                    # Replace old ingredient with new summed one
                    all_ingredients = [
                        ing if ing.name != ingredient.name else ingredient_summed
                        for ing in all_ingredients
                    ]

            for tool in step.tools:
                existing = next((tl for tl in all_tools if tl.name == tool.name), None)
                if existing is None:
                    all_tools.append(tool)

        self.ingredients.extend(
            IngredientAmount.m_from_dict(ingredient.m_to_dict())
            for ingredient in all_ingredients
        )
        self.tools.extend(Tool.m_from_dict(tool.m_to_dict()) for tool in all_tools)

        # --- Compute total nutrients ---
        for nutrient in ('calories', 'fat', 'protein', 'carbohydrates'):
            setattr(
                self,
                nutrient,
                sum(
                    (getattr(ingredient, nutrient, 0.0) or 0.0)
                    for ingredient in (self.ingredients or [])
                ),
            )

        # --- Compute nutrients per serving ---
        if self.number_of_servings:
            for nutrient in ('calories', 'fat', 'protein', 'carbohydrates'):
                per_serving_attr = f'{nutrient}_per_serving'
                total_value = getattr(self, nutrient, 0.0)
                setattr(self, per_serving_attr, total_value / self.number_of_servings)

        # --- Compute total duration ---
        try:
            self.duration = sum((step.duration or 0.0) for step in (self.steps or []))
        except Exception as e:
            logger.warning('recipe_duration_sum_failed', error=str(e))

        ingredient_diets = [
            (ingredient.diet_type or 'AMBIGUOUS')
            for ingredient in (self.ingredients or [])
        ]

        # --- Find the diet type ---
        if not ingredient_diets:
            self.diet_type = 'AMBIGUOUS'
        elif 'ANIMAL_PRODUCT' in ingredient_diets:
            self.diet_type = 'ANIMAL_PRODUCT'
        elif all(d == 'VEGAN' for d in ingredient_diets):
            self.diet_type = 'VEGAN'
        elif 'VEGETARIAN' in ingredient_diets:
            self.diet_type = 'VEGETARIAN'
        else:
            self.diet_type = 'AMBIGUOUS'


class RecipeScaler(BaseSection, Schema):
    """
    A schema that references an existing recipe and creates a scaled version
    based on desired number of servings.
    """

    m_def = Section(
        label='Recipe Scaler',
        description='Scale a recipe for different serving sizes',
    )

    original_recipe = Quantity(
        type=Recipe,
        description='Reference to the original recipe to be scaled',
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
    )

    desired_servings = Quantity(
        type=int,
        description='Number of servings desired for the scaled recipe',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )

    scaled_recipe = Quantity(
        type=Recipe,
        description='The resulting scaled recipe',
    )

    def scale_recipe(
        self,
        recipe: Recipe,
        scaling_factor: float,
        archive: 'EntryArchive',
        logger: 'BoundLogger',
    ) -> None:
        """
        Scales the given recipe by the specified scaling factor and creates
        a new archived entry for the scaled recipe.
        """
        if scaling_factor == 1.0:
            logger.warning('Scaling factor is 1.0, no scaling applied.')
            return
        scaled_recipe = Recipe().m_from_dict(recipe.m_to_dict(with_root_def=True))
        scaled_recipe.name += f' (scaled x{scaling_factor:.2f})'
        scaled_recipe.number_of_servings *= scaling_factor

        # reset ingredients and tools, that will be populated from steps
        scaled_recipe.tools = []
        scaled_recipe.ingredients = []

        # Scale ingredients in steps
        for step in scaled_recipe.steps:
            for ingredient in step.ingredients:
                ingredient.quantity *= scaling_factor
                if ingredient.quantity_si:
                    ingredient.quantity_si *= scaling_factor

        file_name = (
            (f'{recipe.name} scaled x{scaling_factor:.2f}.archive.json')
            .replace(' ', '_')
            .lower()
        )
        self.scaled_recipe = create_archive(
            scaled_recipe, archive=archive, file_name=file_name, overwrite=True
        )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        Uses the referenced original recipe entry and specified desired servings to
        create a scaled recipe entry.
        """
        super().normalize(archive, logger)

        self.scaled_recipe = None
        if self.original_recipe and self.desired_servings:
            try:
                scaling_factor = (
                    self.desired_servings / self.original_recipe.number_of_servings
                )
                self.scale_recipe(self.original_recipe, scaling_factor, archive, logger)
            except Exception as e:
                logger.error('Error while scaling recipe.', exc_info=True, error=e)


m_package.__init_metainfo__()
