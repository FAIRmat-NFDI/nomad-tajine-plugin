# Tutorial

## Install this plugin

If you are using the **nomad-tajine-distro** Oasis, this plugin comes preinstalled.  

If you would like to install the plugin on another NOMAD Oasis instance, please follow the official guide on [**How to install plugins into a NOMAD Oasis**](https://nomad-lab.eu/prod/v1/docs/howto/oasis/configure.html#plugins).

In short, to ensure that this plugin is available in your NOMAD Oasis, you need to declare it in the `pyproject.toml` file of your Oasis. This involves adding the plugin package to the `[project.dependencies]` table.

There are two ways to do this:

**a)** Use `uv add`, which automatically adds the dependency and source entries to `pyproject.toml` and sets up the environment.  

```bash
uv add packages/nomad-tajine-plugin
```
**b)** Modify the `pyproject.toml` file manually:
```toml
[project]
dependencies = [
  ...
  "nomad-tajine-plugin",
]

[tool.uv.sources]
...
nomad-tajine-plugin = { workspace = true }
```

## Create recipe entries manually

It is similar to using other built-in ELN templates. You simply need to choose the **Recipe** as your **Built-in schema**.

You can follow this concise steps:

1. In the GUI: **PUBLISH** → **Uploads** → **CREATE A NEW UPLOAD** → **CREATE FROM SCHEMA** → select **Built-in schema** → **Recipe** (entry type provided by the plugin).

2. Fill the main fields: Name, Cuisine, Number of servings, etc.

3. Choose ingredients from already existing entries or simply add them in using the designated fields (name, amount, unit) and Cooking steps (ordered steps).


## Search recipes

The easiest is to use NOMAD Tajine App. You can find it in the **EXPLORE** menu under **USE CASES** category.

Feel free to use the already existing dashboard or modify it to your search criteria. 

## Contribute to this plugin

The link to the GitHub repository: https://github.com/FAIRmat-NFDI/nomad-tajine-plugin

Similar to many other open-source projects, here are the concise main steps you may want to take  
Fork the repository → create an issue → create a feature branch → commit changes → open a PR.

Keep changes minimal and documented; reference issues where possible.

## Contribute to the plugin's docs

The steps are the same as briefly mentioned above.

Noteworthy is that the docs are Markdown and deployed using **MkDocs**.

After you modified or added to the docs, preview them locally for a final sanity check:

```bash
uv run mkdocs serve
```