from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import (
    App,
    Axis,
    AxisQuantity,
    Column,
    Dashboard,
    Layout,
    Markers,
    Menu,
    MenuItemHistogram,
    MenuItemTerms,
    MenuItemVisibility,
    SearchQuantities,
    WidgetHistogram,
    WidgetScatterPlot,
)

SCHEMA = 'nomad_tajine_plugin.schema_packages.schema_package.Recipe'

recipe_app_entry_point = AppEntryPoint(
    name='Recipe App',
    description='This is an app for visualizing recipes from the nomad-tajine plugin.',
    app=App(
        label='Recipes',
        path='recipes',
        description='Search recipes, ingredients, and kitchen tools',
        category='Use Cases',
        readme="""This app allows you to search **recipes** within NOMAD.
        The  menu on the left and the shown default columns are specifically 
        designed for exploring recipes and their ingredients. The dashboard 
        directly shows useful interactive statistics about the recipes.
        """,
        search_quantities=SearchQuantities(include=[f'data.*#{SCHEMA}']),
        filters_locked={'section_defs.definition_qualified_name': [SCHEMA]},
        columns=[
            Column(
                quantity=f'data.name#{SCHEMA}',
                label='Name',
                selected=True,
            ),
            Column(
                quantity=f'data.duration#{SCHEMA}',
                label='Duration',
                selected=True,
                unit='minute',
            ),
            Column(
                quantity=f'data.authors#{SCHEMA}',
                label='Authors',
                selected=True,
            ),
            Column(
                quantity=f'data.cuisine#{SCHEMA}',
                label='Cuisine',
                selected=True,
            ),
            Column(
                quantity=f'data.difficulty#{SCHEMA}',
                label='Difficulty',
                selected=True,
            ),
            Column(
                quantity=f'data.calories_per_serving#{SCHEMA}',
                label='Calories per serving',
                selected=True,
                unit='kcal',
            ),
        ],
        menu=Menu(
            title='Recipe filters',
            items=[
                Menu(
                    title='Dietary preferences',
                    items=[
                        # filter by diet
                        MenuItemTerms(
                            quantity=f'data.diet_type#{SCHEMA}',
                            title='Diet',
                            show_input=False,
                        ),
                        # filter by cuisine
                        MenuItemTerms(
                            quantity=f'data.cuisine#{SCHEMA}',
                            title='Cuisine',
                            show_input=True,
                        ),
                        MenuItemTerms(
                            quantity=f'data.difficulty#{SCHEMA}',
                            title='Difficulty',
                            show_input=False,
                        ),
                    ],
                ),
                Menu(
                    title='Macronutrients',
                    size='md',
                    items=[
                        MenuItemHistogram(
                            title='Protein per serving',
                            x={
                                'search_quantity': f'data.protein_per_serving#{SCHEMA}',
                            },
                            n_bins=100,
                            autorange=True,
                        ),
                        MenuItemHistogram(
                            title='Fat per serving',
                            x={
                                'search_quantity': f'data.fat_per_serving#{SCHEMA}',
                            },
                            n_bins=100,
                            autorange=True,
                        ),
                        MenuItemHistogram(
                            title='Carbohydrates per serving',
                            x={
                                'search_quantity': f'data.carbohydrates_per_serving#{SCHEMA}',  # noqa: E501
                            },
                            n_bins=100,
                            autorange=True,
                        ),
                    ],
                ),
                Menu(
                    title='Ingredients',
                    items=[
                        MenuItemTerms(
                            quantity=f'data.ingredients.name#{SCHEMA}',
                            title='Ingredient name',
                            show_input=True,
                            options=8,
                        ),
                    ],
                ),
                Menu(
                    title='Kitchen tools',
                    items=[
                        MenuItemTerms(
                            quantity=f'data.tools.name#{SCHEMA}',
                            title='Tool name',
                            show_input=True,
                        ),
                    ],
                ),
                Menu(
                    title='Author / Recipe',
                    size='md',
                    items=[
                        MenuItemTerms(search_quantity=f'data.authors#{SCHEMA}'),
                        MenuItemHistogram(
                            title='Created on',
                            x={'search_quantity': 'upload_create_time'},
                        ),
                        MenuItemVisibility(title='Visibility'),
                    ],
                ),
            ],
        ),
        dashboard=Dashboard(
            widgets=[
                # --- histograms ---
                WidgetHistogram(
                    title='Duration',
                    x=AxisQuantity(
                        search_quantity=f'data.duration#{SCHEMA}', unit='minute'
                    ),
                    n_bins=100,
                    autorange=True,
                    layout={
                        'md': Layout(w=6, h=3, x=0, y=0, minW=3, minH=3),
                        'lg': Layout(w=6, h=3, x=0, y=0, minW=5, minH=4),
                    },
                ),
                WidgetHistogram(
                    title='Calories',
                    x=AxisQuantity(
                        search_quantity=f'data.calories_per_serving#{SCHEMA}',
                        unit='kcal',
                    ),
                    n_bins=100,
                    autorange=True,
                    layout={
                        'md': Layout(w=6, h=3, x=0, y=3, minW=3, minH=3),
                        'lg': Layout(w=6, h=3, x=0, y=3, minW=5, minH=4),
                    },
                ),
                WidgetScatterPlot(
                    title='Calories vs Duration (by Specifier)',
                    x=Axis(
                        search_quantity=f'data.duration#{SCHEMA}',
                        title='Duration',
                        unit='minute',
                    ),
                    y=Axis(
                        search_quantity=f'data.calories_per_serving#{SCHEMA}',
                        title='Calories',
                        unit='kcal',
                    ),
                    size=100,
                    markers=Markers(
                        color=Axis(
                            search_quantity=f'data.diet_type#{SCHEMA}',
                            title='Diet (specifier)',
                        )
                    ),
                    autorange=True,
                    layout={
                        'md': Layout(w=6, h=6, x=6, y=0, minW=3, minH=3),
                        'lg': Layout(w=6, h=6, x=6, y=0, minW=6, minH=6),
                    },
                ),
                WidgetScatterPlot(
                    title='Calories vs Protein (by Specifier)',
                    x=Axis(
                        search_quantity=f'data.protein_per_serving#{SCHEMA}',
                        title='Protein',
                        unit='g',
                    ),
                    y=Axis(
                        search_quantity=f'data.calories_per_serving#{SCHEMA}',
                        title='Calories',
                        unit='kcal',
                    ),
                    size=100,
                    markers=Markers(
                        color=Axis(
                            search_quantity=f'data.diet_type#{SCHEMA}',
                            title='Diet (specifier)',
                        )
                    ),
                    autorange=True,
                    layout={
                        'md': Layout(w=6, h=6, x=12, y=0, minW=3, minH=3),
                        'lg': Layout(w=6, h=6, x=12, y=0, minW=6, minH=6),
                    },
                ),
                WidgetScatterPlot(
                    title='Protein vs Fat (by Specifier)',
                    x=Axis(
                        search_quantity=f'data.fat_per_serving#{SCHEMA}',
                        title='Fat',
                        unit='g',
                    ),
                    y=Axis(
                        search_quantity=f'data.protein_per_serving#{SCHEMA}',
                        title='Protein',
                        unit='g',
                    ),
                    size=100,
                    markers=Markers(
                        color=Axis(
                            search_quantity=f'data.diet_type#{SCHEMA}',
                            title='Diet (specifier)',
                        )
                    ),
                    autorange=True,
                    layout={
                        'md': Layout(w=6, h=6, x=18, y=0, minW=3, minH=3),
                        'lg': Layout(w=6, h=6, x=18, y=0, minW=6, minH=6),
                    },
                ),
            ],
        ),
    ),
)

# macronutrients: fat, proteins, ..
