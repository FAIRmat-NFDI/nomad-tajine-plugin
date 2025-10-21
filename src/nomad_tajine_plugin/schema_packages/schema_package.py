from typing import (
    TYPE_CHECKING,
)

from nomad.datamodel.data import UseCaseElnCategory
from nomad.datamodel.metainfo.basesections import (
    Activity,
    ActivityStep,
    Instrument,
    System,
)
from nomad.metainfo.metainfo import Section, SubSection

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad.config import config

# from nomad.datamodel.data import Schema
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.metainfo import MEnum, Quantity, SchemaPackage

configuration = config.get_plugin_entry_point(
    'nomad_tajine_plugin.schema_packages:schema_package_entry_point'
)

m_package = SchemaPackage()


class Ingredient(System):
    quantity = Quantity(
        type=float,
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
        # unit='minute',        # TODO: add custom units to pint custom unit registry
    )

    semantic_concept = Quantity(
        type=str,  # TODO: discuss with ontology group
    )

    # preparation_notes = Quantity() or SubSection() TODO: discuss
    # TODO: discuss references


class Tool(Instrument):
    type = Quantity(
        type=str, a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity)
    )

    description = Quantity(
        type=str, a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity)
    )


class RecipeStep(ActivityStep):
    duration = Quantity(
        type=float,
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
        unit='minute',
    )

    temperature = Quantity(
        type=float,
        default=20.0,
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
        unit='celsius',
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


class Recipe(Activity):
    m_def = Section(
        label='Cooking Recipe',
        categories=[UseCaseElnCategory],
    )

    name = Quantity(
        type=str, a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity)
    )

    duration = Quantity(
        type=float,
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
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
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
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


m_package.__init_metainfo__()
