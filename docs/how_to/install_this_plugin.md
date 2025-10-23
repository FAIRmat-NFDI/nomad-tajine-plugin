# Install This Plugin

!!! note "Note"
    The [NOMAD Tajine Example Oasis](https://nomad-lab.eu/prod/v1/tajine/gui/about/information)
    comes with `nomad-tajine-plugin` preinstalled. You can use
    your existing NOMAD account to create and explore recipes on this
    Oasis.

If you would like to install the plugin on your NOMAD Oasis instance, here's the official guide on [**How to install plugins into a NOMAD Oasis**](https://nomad-lab.eu/prod/v1/docs/howto/oasis/configure.html#plugins).

In short, you need to declare the plugin in the `pyproject.toml` file of your Oasis distribution repository. This involves adding the plugin package to the `[project.optional-dependencies]` table under `plugins`:

```toml
[project.optional-dependencies]
plugins = [
  ...
  "nomad-tajine-plugin",
]
```

## Adding the USDA Nutrient Lookup

The Tajine plugin can connect to the USDA FoodData Central API to fetch
nutritional information for ingredients. To enable this feature, you need to first
obtain an API key from the [USDA FoodData Central website](https://fdc.nal.usda.gov/api-key-signup). 

Once you have the API key, you need to configure the plugin to use it. This is done by
adding the API key to the plugin configuration in your Oasis's `nomad.yaml` file:
```yaml
...
plugins:
  entry_points:
    exclude:
      ...
    options:
      nomad_tajine_plugin.schema_packages:schema_tajine_entry_point:
        usda_api_key: YOUR_API_KEY_HERE
...
```

If you do not provide an API key, the nutrients will not be fetched automatically!

!!! note "Note"
    The API key allows you to query the USDA database 1000 times per hour. Exceeding this limit will cause the API key to be temporarily blocked for 1 hour.
