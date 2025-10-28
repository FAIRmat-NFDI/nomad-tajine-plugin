from nomad.config.models.plugins import SchemaPackageEntryPoint
from pydantic import Field


class TajineSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    usda_api_key: str = Field('', description='API key for USDA FoodData Central API')
    ninja_api_key: str = Field('', description='API key for Ninja Recipes API')

    def load(self):
        from nomad_tajine_plugin.schema_packages.schema_package import m_package

        return m_package


schema_tajine_entry_point = TajineSchemaPackageEntryPoint(
    name='TajineSchemaPackage',
    description='Tajine schema package entry point configuration.',
)
