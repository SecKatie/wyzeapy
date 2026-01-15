# Wyzeapy justfile
default:
    @just --list

# Generate the API client from the OpenAPI spec
generate:
    rm -rf src/wyzeapy/wyze_api_client
    uv run openapi-python-client generate --path wyze-api-openapi.yaml --output-path /tmp/wyze_client --overwrite
    mv /tmp/wyze_client/wyze_api_client src/wyzeapy/wyze_api_client
    rm -rf /tmp/wyze_client

# Validate the OpenAPI spec
validate:
    uv run openapi-spec-validator wyze-api-openapi.yaml

# Run all tests
test:
    uv run pytest tests/ -v

# Run unit tests only
test-unit:
    uv run pytest tests/ -v -m "not integration"

# Run integration tests only
test-integration:
    uv run pytest tests/ -v -m integration

# Generate documentation from docstrings
docs:
    uv run sphinx-build -b html docs docs/_build

# Clean documentation build directory
clean-docs:
    rm -rf docs/_build

# Rebuild documentation from scratch
docs-clean:
    just clean-docs
    just docs

docs-open: docs
    xdg-open docs/_build/index.html

# Build the package
build:
    rm -rf dist/
    uv build

# Check package metadata before publishing
check: build
    uv run twine check dist/*

# Publish to TestPyPI (requires TEST_PYPI_TOKEN env var)
publish-test: check
    UV_PUBLISH_TOKEN=$TEST_PYPI_TOKEN uv publish --publish-url https://test.pypi.org/legacy/

# Publish to PyPI (requires PYPI_TOKEN env var)
publish: check
    UV_PUBLISH_TOKEN=$PYPI_TOKEN uv publish
