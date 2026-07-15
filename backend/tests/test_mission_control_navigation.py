from pathlib import Path


def test_mission_control_uses_executive_tabs() -> None:
    project_root = Path(__file__).resolve().parents[2]
    source = (
        project_root
        / "backend"
        / "workspaces"
        / "mission_control_native.py"
    ).read_text(encoding="utf-8")

    expected_tabs = [
        "Executive Overview",
        "Financial Performance",
        "Drivers & Root Cause",
        "Opportunities & Simulation",
        "Risk & Actions",
        "Executive Report",
    ]

    for tab in expected_tabs:
        assert tab in source

    assert "st.tabs" in source
