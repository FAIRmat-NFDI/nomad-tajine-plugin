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
    return lab_id.replace(' ', '_').lower()


class IngredientType(Entity, Schema):
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

    def normalize(self, archive, logger: 'BoundLogger'):
        if not self.lab_id:
            self.lab_id = format_lab_id(self.name)
        else:
            self.lab_id = format_lab_id(self.lab_id)

        super().normalize(archive, logger)


class Ingredient(EntityReference):
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

    quantity_si = Quantity(
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
        type=IngredientType,
        description='A reference to a ingredient type entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='ingredient type reference',
        ),
    )

    # preparation_notes = Quantity() or SubSection() TODO: discuss
    # TODO: discuss references

    def convert_volume(self, unit_volume):
        if self.reference.density:
            self.quantity_si = (
                ureg.Quantity(unit_volume, 'milliliter')
                * self.quantity
                * self.reference.density
            )
        else:
            self.quantity_si = None

    def convert_piece(self):
        if self.reference.weight_per_piece:
            self.quantity_si = self.reference.weight_per_piece * self.quantity
        else:
            self.quantity_si = None

    def normalize(self, archive, logger: 'BoundLogger'):  # noqa: PLR0912
        if not self.lab_id:
            self.lab_id = format_lab_id(self.name)
        else:
            self.lab_id = format_lab_id(self.lab_id)

        super().normalize(archive, logger)

        if not self.reference:
            logger.debug('IngredientType entry not found. Creating a new one.')
            try:
                ingredient_type = IngredientType(
                    name=self.name,
                    lab_id=self.lab_id,
                )
                self.reference = create_archive(
                    ingredient_type,
                    archive,
                    f'{self.lab_id}.archive.json',
                    overwrite=False,
                )
            except Exception as e:
                logger.error(
                    'Failed to create IngredientType entry.', exc_info=True, error=e
                )

        if self.reference:
            unit = self.unit.replace(' ', '_')  # type: ignore
            match unit:
                # the values for teaspoon, tablespoon and cup come from
                # https://en.wikipedia.org/wiki/Cooking_weights_and_measures, which
                # in turn compiles them from '1896 Boston Cooking-School Cook Book'
                case 'gram':
                    self.quantity_si = self.quantity
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
                            self.quantity_si = (
                                (ureg(unit).to(ureg.milliliter))
                                * self.quantity
                                * self.reference.density
                            )
                        except Exception as e:
                            logger.warn(f'Not able to convert common unit to [g], {e}')
                    else:
                        self.quantity_si = None


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
        section_def=Ingredient,
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

    nutrition_value = Quantity(
        type=float,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit='kcal',
        ),
        unit='kcal',
    )

    diet = Quantity(
        type=MEnum(
            'non-vegetarian',
            'vegetarian',
            'vegan',
        ),
        a_eln=ELNAnnotation(component=ELNComponentEnum.EnumEditQuantity),
    )  # TODO: add more options / complexity

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
        section_def=Ingredient,
        description='',
        repeats=True,
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

        # Collect and clone all ingredients and tools from steps
        self.ingredients.extend(
            Ingredient.m_from_dict(ingredient.m_to_dict())
            for step in self.steps
            for ingredient in step.ingredients
        )
        self.tools.extend(
            Tool.m_from_dict(tool.m_to_dict())
            for step in self.steps
            for tool in step.tools
        )


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
