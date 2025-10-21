from nomad.config.models.plugins import ExampleUploadEntryPoint

tajine_example_upload_entry_point = ExampleUploadEntryPoint(
    title='Tajine Example',
    category='Examples',
    description='An example of a Tajine recipe.',
    resources=["example_uploads/example/ingredients.archive.yaml"],
)
