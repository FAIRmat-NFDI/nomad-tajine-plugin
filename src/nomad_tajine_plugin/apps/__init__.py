from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import (
    App,
    Axis,
    AxisQuantity,
    Column,
    Dashboard,
    Layout,
    Menu,
    MenuItemHistogram,
    MenuItemTerms,
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
                quantity=f'data.nutrition_value#{SCHEMA}',
                label='Calories',
                selected=True,
                unit='kcal',
            ),
        ],
        menu=Menu(
            title='Recipe filters',
            items=[
                # filter by how many toools or ingredients
                # filter for ingredients
                # menu=Menu(
                #     title='Ingredients',
                #     items=[
                #         # filter by diet
                #         MenuItemTerms(
                #             quantity=f'data.ingredients#{SCHEMA}',
                #             title='Ingredients',
                #             show_input=True,
                #         ),
                #     ],
                # ),
                Menu(
                    title='Dietary restrictions',
                    items=[
                        # filter by diet
                        MenuItemTerms(
                            quantity=f'data.diet#{SCHEMA}',
                            title='Diet',
                            show_input=True,
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
                            show_input=True,
                        ),
                    ],
                ),
                Menu(
                    title='Author / Recipe',
                    size='md',
                    items=[
                        MenuItemTerms(search_quantity=f'data.authors#{SCHEMA}'),
                        MenuItemHistogram(x={'search_quantity': 'upload_create_time'}),
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
                        'md': Layout(w=6, h=4, x=0, y=0, minW=3, minH=3),
                        'lg': Layout(w=6, h=5, x=0, y=0, minW=5, minH=4),
                    },
                ),
                WidgetHistogram(
                    title='Calories',
                    x=AxisQuantity(
                        search_quantity=f'data.nutrition_value#{SCHEMA}', unit='kcal'
                    ),
                    n_bins=100,
                    autorange=True,
                    layout={
                        'md': Layout(w=6, h=4, x=6, y=0, minW=3, minH=3),
                        'lg': Layout(w=6, h=5, x=6, y=0, minW=5, minH=4),
                    },
                ),
                WidgetScatterPlot(
                    title='Duration vs Nutrition value (by Specifier)',
                    x=Axis(
                        search_quantity=f'data.duration#{SCHEMA}',
                        title='Duration',
                        unit='minute',
                    ),
                    y=Axis(
                        search_quantity=f'data.nutrition_value#{SCHEMA}',
                        title='Calories',
                        unit='kcal',
                    ),
                    size=100,
                    autorange=True,
                    layout={
                        'md': Layout(w=6, h=4, x=12, y=0, minW=3, minH=3),
                        'lg': Layout(w=6, h=5, x=12, y=0, minW=6, minH=6),
                    },
                ),
            ],
        ),
    ),
)

# macronutrients: fat, proteins, ..
