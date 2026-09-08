---
weight: 10
---
# Contributing

We welcome contributions to the routing library! This document outlines the process for contributing to this project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:

    ```
    git clone https://github.com/YOUR-USERNAME/routing.git
    ```

3. Create a new branch for your feature or fix:

    ```
    git checkout -b fix/<your-fix-name>
    ```

    or for a new feature:

    ```
    git checkout -b feat/<your-feature-name>
    ```

    or for documentation changes:

    ```
    git checkout -b docs/<your-docs-changes-name>
    ```

## Setting up Pre-commit

We use pre-commit hooks to ensure code quality and consistency. To set this up:

1. Install pre-commit:

    ```
    pip install pre-commit
    ```

2. Install the git hooks:

    ```
    pre-commit install
    ```

When you try to commit, these checks will run automatically. If any checks fail, the commit will be prevented and you'll need to fix the issues before committing again.

To run the checks manually:

```bash
pre-commit run --all-files
```

## Contributing to Documentation

We use MkDocs for our documentation. To set up the documentation environment:

1.  Create and activate a virtual environment:

        pip install uv
        uv venv
        source .venv/bin/activate


2.  Install requirements:

    ```
      uv pip install -r requirements.txt
    ```

3.  Documentation files are in the `docs/` directory and written in Markdown format.

4.  To preview your changes locally:

    ```
    mkdocs serve
    ```

    Then visit `http://127.0.0.1:8000` in your browser.

5.  Documentation structure:

        docs/
        ├── index.md          # Main documentation page
        ├── file.md           # Documentation page for file
        ├── folder/
        │   ├── index.md      # Documentation page for folder
        │   └── file.md       # Documentation page for file

6.  Follow these documentation guidelines:

    - Use British English
    - Keep paragraphs concise and focused
    - Include code examples where appropriate
    - Add screenshots for UI-related features
    - Update the navigation in `mkdocs.yml` if adding new pages

7.  Check for broken links and formatting issues before submitting

## Making Changes

1. Make your changes in your feature branch
2. Write or update tests as needed
3. Ensure your code follows the existing style of the project
4. Commit your changes:

    ```
    git commit -m "Description of your changes"
    ```

## Submitting Changes

1. Push your changes to your fork on GitHub:

    ```
    git push origin <your-branch-name>
    ```

2. Open a Pull Request (PR) from your fork to our main repository
3. In your PR description, clearly describe:
    - What changes you've made
    - Why you've made them
    - Any relevant issue numbers

## Pull Request Guidelines

-   PRs should focus on a single feature or fix
-   Keep changes small and focused
-   Update documentation as needed
-   Ensure all tests pass
-   Follow existing code style and conventions
-   All pre-commit checks must pass
-   For documentation changes:
    -   Ensure mkdocs builds successfully
    -   Preview changes locally before submitting
    -   Check for broken links and proper formatting

## Questions or Issues?

If you have questions or run into issues, please:

1. Check existing [issues on GitHub](https://github.com/anvil-works/routing/issues)
2. Create a new issue if needed
3. Ask questions in the PR itself

Thank you for contributing to the routing library!
