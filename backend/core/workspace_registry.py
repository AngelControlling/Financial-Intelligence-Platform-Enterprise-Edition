from __future__ import annotations
from collections import OrderedDict
from models.workspace import WorkspaceDefinition

class WorkspaceRegistry:
    def __init__(self)->None: self._items:OrderedDict[str,WorkspaceDefinition]=OrderedDict()
    def register(self,workspace:WorkspaceDefinition)->None:
        if workspace.key in self._items: raise ValueError(f"Workspace already registered: {workspace.key}")
        self._items[workspace.key]=workspace
    def get(self,key:str)->WorkspaceDefinition:
        if key not in self._items: raise KeyError(f"Unknown workspace: {key}")
        return self._items[key]
    def enabled(self)->list[WorkspaceDefinition]: return sorted((x for x in self._items.values() if x.enabled),key=lambda x:(x.section,x.order,x.label))
    def grouped(self)->dict[str,list[WorkspaceDefinition]]:
        groups={}
        for w in self.enabled(): groups.setdefault(w.section,[]).append(w)
        return groups
    def keys(self)->tuple[str,...]: return tuple(self._items.keys())
