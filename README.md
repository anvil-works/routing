# Routing

## Overview

The routing library maps URL paths to forms in an Anvil app. It supports direct links, browser history, client navigation and route data loading.

Start with the [quick start](docs/quick-start.md), browse the [documentation](docs/index.md), or use the root [llms.txt](llms.txt) as a self-contained usage reference for agents working in an app with the dependency.

## Third party dependency

To use as a third party dependency, use the code `3PIDO5P3H4VPEMPL`

## Clone from github

Clone `https://github.com/anvil-works/routing` anonymously in the Anvil editor, then add the clone as a dependency of your app. See [Installation](docs/installation.md).

## License

This project is licensed under the [MIT License](LICENSE).

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Building the docs

```bash
pip install uv
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
mkdocs serve
```

Then visit http://localhost:8000
