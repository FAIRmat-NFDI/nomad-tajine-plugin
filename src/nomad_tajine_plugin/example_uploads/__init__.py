from nomad.config.models.plugins import ExampleUploadEntryPoint

tajine_example_upload_entry_point = ExampleUploadEntryPoint(
    title='Tajine Example',
    category='Use Cases',
    description='A simple example for a recipe for a Moroccan chicken tagine.',
    resources=['example_uploads/example/tajine.archive.yaml'],
)
