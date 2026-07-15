from __future__ import annotations
from core.router import Router
from core.workspace_registry import WorkspaceRegistry

class WorkspaceManager:
    def __init__(self,registry:WorkspaceRegistry,router:Router)->None: self.registry=registry; self.router=router
    def render(self)->None: self.router.render()
