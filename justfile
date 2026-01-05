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
