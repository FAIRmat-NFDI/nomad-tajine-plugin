def test_importing_app():
    # this will raise an exception if pydantic model validation fails for th app
    from nomad_tajine_plugin.apps import recipe_app_entry_point

    assert recipe_app_entry_point.app.label == 'Recipes'
    assert recipe_app_entry_point.app.path == 'recipes'
