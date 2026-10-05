# Releasing

1. Run Ruff, strict mypy, pytest with coverage and `python -m build`.
2. Build and smoke-test the Windows portable folder on a clean Windows environment.
3. Verify the Git tag matches the final commit and create a GitHub release with wheel, sdist, Windows ZIP and checksums.
4. Publish to PyPI only through an already configured trusted publisher or release credential.

The backend dependency is pinned to `nyaaapi-client` tag `v0.1.0`. Do not change the backend repository from this project.
