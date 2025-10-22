# Tutorial


## Install this plugin

### 1. Add it as a submodule to yournomad-tajine-distro
   ```bash
   git submodule add https://github.com/FAIRmat-NFDI/nomad-tajine-plugin.git packages/nomad-tajine-plugin>
   ```
### 2. Modify the `pyproject.toml` of your nomad-tajine-distro

To ensure `uv` recognizes the local plugins (a local copy of your plugin repository available in `packages/` directory), we need to make some modifications in the `pyproject.toml`.  These include adding the plugin package to `[project.dependencies]` and `[tool.uv.sources]` tables. The packages listed under `[tool.uv.sources]` are loaded by `uv` using the local code directory made available under `packages/` with the previous step. This list will contain all the plugins that we need to actively develop in this environment.

If a new plugin is **not** listed under `[project.dependencies]`, we need to first add it as a dependency. After adding the dependencies, update the `[tool.uv.sources]` section in your `pyproject.toml` file to reflect the new plugins.

There are two ways of adding to these two lists:

   a) You can use `uv add` which adds the dependency and the source in `pyproject.toml` and sets up the environment.  Adding multiple plugins should be done in a single command:
   ```bash
   uv add packages/nomad-tajine-plugin
   ```
   b) You can modify the `pyproject.toml` file manually:

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

!!! attention
    You can also use `uv` to install a specific branch of the plugin without adding a submodule locally.
    ```bash
    uv add https://github.com/FAIRmat-NFDI/nomad-measurements.git --branch <specific-branch-name>
    ```
    This command will not include the plugin in the `packages/` folder, and hence this plugin will not be editable.


## Create recipe entries

It is similar to using other built-in ELN temlates. You simply need to choose the **Recipe** as your template: You could follow this concise steps:

In the GUI: PUBLISH → Uploads → CREAT A NEW UPLOAD → CREATE FROM SCHEMA → Built-in schema → Recipe (entry type provided by the plugin).

Fill the main fields: Title, Cuisine, Servings, Prep/Cook time.

Choose ingredients from already existing entries or simply add them in using the designated fields (name, amount, unit) and Cooking steps (ordered steps).

Save the entry and (optionally) add it to a Dataset/Collection.

!!! note
Additional entry types (e.g., Ingredient, CookingStep, RecipeCollection) can be created and linked, depending on how you structure your data.


## Search Recipes

The easiest is to use NOMAD Tajine App. You can find it under EXPLORE menu.

Feel free to use the already existing dashboard or modify it to your search criteria. 

## Contribute to this plugin

The link to the GitHub repository: https://github.com/FAIRmat-NFDI/nomad-tajine-plugin

Similar to many other open-source projects, here are the concise main steps you may want to take  
Fork the repository → create an issue → create a feature branch → commit changes → open a PR.

Keep changes minimal and documented; reference issues where possible.

## Contribute to the plugin's docs

The steps are the same as briefly mentioned above.

Noteworthy is that the docs are Markdown and deployed using **MkDocs**.

After you modified or added to the docs, preview them locally, before PR:

Install the MkDocs using uv: 

```bash
uv run pip install requirements_docs.txt
```
and then preview them for sanity check:

```bash
uv run mkdocs serve
```