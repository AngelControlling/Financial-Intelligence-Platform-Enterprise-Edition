from __future__ import annotations

import json
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"


def main() -> int:
    errors: list[str] = []

    for path in BACKEND.rglob("*.py"):
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            errors.append(f"Syntax: {path.relative_to(ROOT)}: {exc}")

    forbidden = {
        "reportlab": [],
        "background_gradient": [],
    }
    for path in BACKEND.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for token in forbidden:
            if token in text:
                forbidden[token].append(str(path.relative_to(ROOT)))

    for token, paths in forbidden.items():
        if paths:
            errors.append(f"Forbidden dependency/reference '{token}': {paths}")

    active_path = ROOT / "storage" / "data_lake" / "active_versions.json"
    if not active_path.exists():
        errors.append("Missing active_versions.json")
    else:
        active = json.loads(active_path.read_text(encoding="utf-8"))
        for dataset_type in ("actuals", "budget", "working_capital"):
            if not active.get(dataset_type):
                errors.append(f"No active version for {dataset_type}")

    required = [
        BACKEND / "enterprise_v2.py",
        BACKEND / "workspaces" / "mission_control_native.py",
        BACKEND / "ui" / "executive_report_launcher.py",
        ROOT / "templates" / "FIP_Budget_Template_v1.xlsx",
    ]
    for path in required:
        if not path.exists():
            errors.append(f"Missing required file: {path.relative_to(ROOT)}")

    if errors:
        print("V2 VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("V2 VALIDATION PASSED")
    print("- Python syntax: OK")
    print("- Active Actuals/Budget/Working Capital: OK")
    print("- ReportLab/Matplotlib gradient references: NONE")
    print("- Required presentation files: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
