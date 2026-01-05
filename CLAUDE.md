# Wyzeapy Project Instructions

## Project Overview
Wyzeapy is a Python wrapper for the Wyze smart home API. It provides async interfaces for controlling Wyze devices (cameras, lights, locks, thermostats, etc.).

## Project Structure
- `src/wyzeapy/` - Original library code
- `src/wyzeapy_v2/` - Refactored v2 library (current development focus)
- `src/wyzeapy_v2/wyze_api_client/` - Auto-generated API client from OpenAPI spec
- `wyze-api-openapi.yaml` - OpenAPI specification for the Wyze API

## Development Commands (justfile)
- `just generate` - Regenerate API client for v1 (`src/wyzeapy/wyze_api_client`)
- `just generate-v2` - Regenerate API client for v2 (`src/wyzeapy_v2/wyze_api_client`)
- `just validate` - Validate the OpenAPI spec
- `just test` - Run all tests
- `just test-unit` - Run unit tests only
- `just test-integration` - Run integration tests only

## Type Checking
Use `ty` (from astral-sh) for type checking:
```bash
uv run ty check ./src/wyzeapy_v2
```

## Generated Code Notes
The `wyze_api_client` directory is auto-generated from `wyze-api-openapi.yaml` using `openapi-python-client`.

**Important:** When fixing type errors in generated code:
1. Prefer modifying the OpenAPI spec (`wyze-api-openapi.yaml`) over editing generated code directly
2. After modifying the spec, regenerate the client with `just generate-v2`
3. The Wyze API passes `access_token` in request bodies, not via Bearer auth headers
4. Endpoints that use body-based auth should NOT have `security` requirements in the OpenAPI spec (this causes the generator to require `AuthenticatedClient` instead of `Client`)

## API Authentication Pattern
The Wyze API uses a non-standard auth pattern:
- Login endpoints use header-based API keys (`keyid`, `apikey`)
- Most other endpoints pass `access_token` in the JSON request body (part of `CommonRequestParams`)
- Lock API uses signature-based auth with Ford app keys

## Key Files for Type Fixes
When fixing type errors, these files commonly need attention:
- `src/wyzeapy_v2/wyzeapy.py` - Main client class
- `src/wyzeapy_v2/devices.py` - Device wrappers
- `src/wyzeapy_v2/wyze_api_client/types.py` - Contains `Unset` type
- Handle `Unset` type by checking `isinstance(value, Unset)` before use