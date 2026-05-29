"""OpenAPI schema helpers for Swagger UI compatibility."""

from typing import Any


def patch_binary_file_uploads(openapi_schema: dict[str, Any]) -> dict[str, Any]:
    """
    FastAPI 3.1 schemas use contentMediaType for files; Swagger UI needs format: binary
    to render the file picker (Choose File) instead of a plain string array.
    """
    schemas = openapi_schema.get("components", {}).get("schemas", {})
    for schema in schemas.values():
        if not isinstance(schema, dict):
            continue
        for prop in schema.get("properties", {}).values():
            if not isinstance(prop, dict):
                continue
            if prop.get("type") == "array":
                items = prop.get("items")
                if isinstance(items, dict) and items.get("type") == "string":
                    if "contentMediaType" in items or items.get("format") != "binary":
                        items["format"] = "binary"
                        items.pop("contentMediaType", None)
            elif prop.get("type") == "string" and "contentMediaType" in prop:
                prop["format"] = "binary"
                prop.pop("contentMediaType", None)
    return openapi_schema
