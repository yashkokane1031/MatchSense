"""Export FastAPI OpenAPI schema to frontend/openapi.json offline."""

import json
from pathlib import Path
from backend.api.main import create_app


def export_openapi() -> None:
    """Export FastAPI OpenAPI schema to frontend/openapi.json completely offline."""
    app = create_app()
    schema = app.openapi()
    out_file = Path(__file__).resolve().parent.parent / "frontend" / "openapi.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    print(f"Successfully exported OpenAPI schema to {out_file}")


if __name__ == "__main__":
    export_openapi()
