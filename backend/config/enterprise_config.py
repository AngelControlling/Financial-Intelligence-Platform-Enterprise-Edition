from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class EnterpriseConfig:
    product_name: str = "FIP Enterprise"
    product_subtitle: str = "Financial Intelligence Platform"
    edition: str = "Enterprise Edition"
    version: str = "2.2.0"
    default_workspace: str = "home"
    default_company: str = "Enterprise Freight Demo"
    default_currency: str = "USD"
    default_user_role: str = "Controller"
    layout: str = "wide"
    sidebar_state: str = "expanded"
CONFIG = EnterpriseConfig()
