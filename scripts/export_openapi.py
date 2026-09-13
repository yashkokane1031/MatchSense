"""Export FastAPI OpenAPI schema to frontend/openapi.json offline."""

import json
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

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
