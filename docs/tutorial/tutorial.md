# Tutorial

## Install this plugin

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

## Create recipe entries manually

It is similar to using other built-in ELN templates. You simply need to choose the **Recipe** as your **Built-in schema**.

You can follow these concise steps:

1. In the GUI: **PUBLISH** → **Uploads** → **CREATE A NEW UPLOAD** → **CREATE FROM SCHEMA** → select **Built-in schema** → **Recipe** (entry type provided by the plugin).

2. Fill the main fields: Name, Cuisine, Number of servings, etc.

3. Choose ingredients from already existing entries or simply add them in using the designated fields (name, amount, unit) and Cooking steps (ordered steps).


## Search recipes

The easiest is to use NOMAD Tajine App. You can find it in the **EXPLORE** menu under **USE CASES** category.

Feel free to use the already existing dashboard or modify it to your search criteria.

## Contribute to this plugin

The plugin is available on our GitHub [here](https://github.com/FAIRmat-NFDI/nomad-tajine-plugin). You can clone it on your local
and test your changes.

Similar to many other open-source projects, here are the concise main steps you may want to take:
Fork the repository → create an issue → create a feature branch → commit changes → open a PR.

Keep changes minimal and documented; reference existing issues where possible.

## Contribute to the plugin's docs

The steps are the same as briefly mentioned above.

Noteworthy is that the docs are Markdown and deployed using **MkDocs**.

After you modified or added to the docs, preview them locally for a final sanity check:

```bash
uv run mkdocs serve
```