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


class IngredientType(Entity):
    pass


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
        type=MEnum('tea spoon', 'piece'),
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

    def normalize(self, archive, logger: 'BoundLogger'):
        if not self.lab_id:
            self.lab_id = self.name

        super().normalize(archive, logger)


# class IngredientTypeReference():
#     pass


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
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='minute'
        ),
        unit='minute',
    )

    temperature = Quantity(
        type=float,
        default=20.0,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity, defaultDisplayUnit='celsius'
        ),
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


m_package.__init_metainfo__()
