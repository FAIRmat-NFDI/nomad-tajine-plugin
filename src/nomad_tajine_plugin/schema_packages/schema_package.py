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

# TODO: if we want to have individual values for macronutrients (fats, proteins, ...),
# we could reactivate this.
# class NutrientAmount(BaseSection):
#     m_def = Section(label='Nutrient Amount')

#     nutrient_id = Quantity(type=str)
#     label = Quantity(type=str)
#     unit = Quantity(type=str)
#     amount = Quantity(type=float)


def format_lab_id(lab_id: str):
    return lab_id.replace(' ', '_').lower()


class Ingredient(Entity, Schema):
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

    total_nutrients_per_100g = Quantity(
        type=float,
        unit='kcal/g',
        description='Nutrients per 100 g for this ingredient type imported from USDA.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='kcal/g'
        ),
    )

    def normalize(self, archive, logger: 'BoundLogger'):
        if not self.lab_id:
            self.lab_id = format_lab_id(self.name)
        else:
            self.lab_id = format_lab_id(self.lab_id)

        super().normalize(archive, logger)


class IngredientAmount(EntityReference):
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

    total_nutrients = Quantity(
        type=float,
        unit='kcal',
        description='Total nutrients of this ingredient.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='kcal',
            # properties= {'editable': False},
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

    def normalize(self, archive, logger: 'BoundLogger'):  # noqa: PLR0912
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

            try:
                self.total_nutrients = (
                    self.mass * self.reference.total_nutrients_per_100g / 100
                )

            except Exception as e:
                logger.error(
                    'Failed to calculate total nutrients for ingredient.',
                    exc_info=True,
                    error=e,
                )


class Tool(Instrument, Schema):
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
    temperature = Quantity(
        type=float,
        default=20.0,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='celsius'
        ),
        unit='celsius',
    )


class Recipe(BaseSection, Schema):
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

    diet = Quantity(
        type=MEnum(
            'non-vegetarian',
            'vegetarian',
            'vegan',
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
    )  # TODO: add more options / complexity

    total_nutrients = Quantity(
        type=float,
        unit='kcal',
        description='Total nutrients of this ingredient.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='kcal',
            # properties= {'editable': False},
        ),
    )

    nutrients_per_serving = Quantity(
        type=float,
        unit='kcal',
        description='Summed nutrients per serving.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='kcal',
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

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
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

                    # Sum nutrition values
                    new_total_nutrients = sum(
                        existing.total_nutrients, ingredient.total_nutrients
                    )

                    # Create a new ingredient with summed values
                    ingredient_summed = IngredientAmount(
                        name=existing.name,
                        quantity=new_quantity,
                        unit=existing.unit,
                        mass=None,  # optionally recalc
                        lab_id=existing.lab_id,
                        reference=existing.reference,
                        total_nutrients=new_total_nutrients,
                    )

                    # Replace old ingredient with new summed one
                    all_ingredients = [
                        ing if ing.name != ingredient.name else ingredient_summed
                        for ing in all_ingredients
                    ]

            for tool in step.tools:
                # Check if ingredient with the same name exists
                existing = next((tl for tl in all_tools if tl.name == tool.name), None)

                if existing is None:
                    all_tools.append(tool)

        self.ingredients.extend(
            IngredientAmount.m_from_dict(ingredient.m_to_dict())
            for ingredient in all_ingredients
        )
        self.tools.extend(Tool.m_from_dict(tool.m_to_dict()) for tool in all_tools)

        self.total_nutrients = sum(
            (ingredient.total_nutrients or 0.0)
            for ingredient in (self.ingredients or [])
        )
        if self.number_of_servings:
            self.nutrients_per_serving = self.total_nutrients / self.number_of_servings

        try:
            self.total_duration = sum(
                (step.duration or 0.0) for step in (self.steps or [])
            )
        except Exception as e:
            logger.warning('recipe_duration_sum_failed', error=str(e))


m_package.__init_metainfo__()
