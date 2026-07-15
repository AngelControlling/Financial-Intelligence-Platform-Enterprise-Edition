from pathlib import Path


def test_global_agent_is_called_from_enterprise_shell() -> None:
    project_root = Path(__file__).resolve().parents[2]
    shell = (
        project_root / "backend" / "core" / "enterprise_shell.py"
    ).read_text(encoding="utf-8")

    assert "render_global_elevenlabs_agent" in shell
    assert "convai-widget-embed" in (
        project_root / "backend" / "ui" / "elevenlabs_agent.py"
    ).read_text(encoding="utf-8")
