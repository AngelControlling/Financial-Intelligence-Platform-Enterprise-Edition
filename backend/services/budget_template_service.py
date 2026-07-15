from __future__ import annotations

from pathlib import Path


class BudgetTemplateService:
    """Locates the official template across safe deployment paths."""

    TEMPLATE_NAME = "FIP_Budget_Template_v1.xlsx"

    def __init__(
        self,
        project_root: str | Path | None = None,
    ) -> None:
        self.project_root = Path(
            project_root
            or Path(__file__).resolve().parents[2]
        )

    @property
    def candidate_paths(self) -> tuple[Path, ...]:
        backend_root = Path(__file__).resolve().parents[1]

        return (
            self.project_root
            / "templates"
            / self.TEMPLATE_NAME,
            backend_root
            / "assets"
            / "templates"
            / self.TEMPLATE_NAME,
            Path.cwd()
            / "templates"
            / self.TEMPLATE_NAME,
            Path.cwd()
            / "backend"
            / "assets"
            / "templates"
            / self.TEMPLATE_NAME,
        )

    @property
    def template_path(self) -> Path:
        for candidate in self.candidate_paths:
            if candidate.exists():
                return candidate

        searched = "\n".join(
            str(path)
            for path in self.candidate_paths
        )

        raise FileNotFoundError(
            "Budget template not found. "
            "Searched paths:\n"
            + searched
        )

    def read_bytes(self) -> bytes:
        return self.template_path.read_bytes()
