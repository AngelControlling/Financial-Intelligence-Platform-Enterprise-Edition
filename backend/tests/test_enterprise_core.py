from core.workspace_registry import WorkspaceRegistry
from models.workspace import WorkspaceDefinition

def _renderer()->None: return None

def test_registry_registers_workspace()->None:
    registry=WorkspaceRegistry(); registry.register(WorkspaceDefinition("home","Home","H",_renderer)); assert registry.get("home").label=="Home"

def test_registry_rejects_duplicates()->None:
    registry=WorkspaceRegistry(); item=WorkspaceDefinition("home","Home","H",_renderer); registry.register(item)
    try: registry.register(item)
    except ValueError: return
    raise AssertionError("Duplicate workspace was not rejected")
