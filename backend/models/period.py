from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PeriodSelection:
    year: int
    view: str
    month: int | None = None
    quarter: int | None = None
    semester: int | None = None

    @property
    def label(self) -> str:
        if self.view == "Month":
            return f"{self.year}-{self.month:02d}"
        if self.view == "Quarter":
            return f"Q{self.quarter} {self.year}"
        if self.view == "Semester":
            return f"H{self.semester} {self.year}"
        if self.view == "YTD":
            return f"YTD {self.year} through month {self.month}"
        return f"FY {self.year}"
