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
