import requests
import json

OPENAPI_URL = "http://localhost:8001/openapi.json"

def fetch_openapi():
    response = requests.get(OPENAPI_URL)
    response.raise_for_status()
    return response.json()              # Backend replies with a big JSON, This JSON is your backend’s API dictionary , At this point, AI now knows everything your backend can do.

INTENT_MAP = {
    ("POST", "/leave/"): "apply_leave",
    ("POST", "/personal/employees"): "create_employee",
    ("GET", "/leave/calender"): "get_leave_calendar",
    ("POST", "/admin/roles"): "create_role",
    ("GET", "/employee/employees"): "get_all_employees",
    ("GET", "/leave/pending/leave"): "get_pending_leaves",
    ("GET", "/leave/details") : "get_upcoming_leaves"
}

def get_capability_by_intent(capabilities, intent):
    for cap in capabilities:
        if cap["intent"] == intent:
            return cap
    return None


def extract_all_capabilities(openapi_json, intent_map):
    capabilities = []

    paths = openapi_json.get("paths", {})

    for path, methods in paths.items():
        for method, details in methods.items():
            method_upper = method.upper()

            key = (method_upper, path)
            if key not in intent_map:
                continue  # skip non-LLM APIs

            intent = intent_map[key]

            # Extract schema reference
            request_body = details.get("requestBody")
            if not request_body:
                continue

            content = request_body.get("content", {})
            json_schema = content.get("application/json", {}).get("schema", {})

            if "$ref" not in json_schema:
                continue

            schema_name = json_schema["$ref"].split("/")[-1]

            capabilities.append({
                "intent": intent,
                "method": method_upper,
                "path": path,
                "schema": schema_name,
                "description": details.get("summary", intent.replace("_", " ").title())
            })

    return capabilities


def extract_form_fields_from_schema(openapi_json, schema_name):
    schemas = openapi_json.get("components", {}).get("schemas", {})

    if schema_name not in schemas:
        raise ValueError(f"Schema {schema_name} not found in OpenAPI")

    schema = schemas[schema_name]

    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])

    form_fields = []

    for field_name, field_info in properties.items():
        field_type = field_info.get("type", "string")

        # Handle date format nicely
        if field_type == "string" and field_info.get("format") == "date":
            field_type = "date"

        form_fields.append({
            "name": field_name,
            "type": field_type,
            "required": field_name in required_fields
        })

    return form_fields


# if __name__ == "__main__":
#     openapi = fetch_openapi()

#     capabilities = extract_all_capabilities(openapi, INTENT_MAP)

#     print("\nCAPABILITIES REGISTRY:")
#     import json
#     print(json.dumps(capabilities, indent=2))

#     # OPTIONAL: show forms for each capability
#     print("\nFORMS:")
#     for cap in capabilities:
#         fields = extract_form_fields_from_schema(openapi, cap["schema"])
#         print(f"\nIntent: {cap['intent']}")
#         print(json.dumps(fields, indent=2))
