from ui.enterprise_theme import ENTERPRISE_CSS


def test_enterprise_css_contains_design_tokens() -> None:
    assert "--fip-primary" in ENTERPRISE_CSS
    assert ".fip-shell-header" in ENTERPRISE_CSS
    assert ".fip-workspace-banner" in ENTERPRISE_CSS
