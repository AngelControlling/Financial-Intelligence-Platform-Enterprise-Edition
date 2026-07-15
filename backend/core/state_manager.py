from __future__ import annotations
from models.dataset import DatasetDescriptor
from core.session_manager import SessionManager

class StateManager:
    def __init__(self,session:SessionManager)->None: self.session=session
    @property
    def current_workspace(self)->str: return self.session.get("fip_current_workspace","home")
    def set_current_workspace(self,key:str)->None: self.session.set("fip_current_workspace",key)
    @property
    def company(self)->str: return self.session.get("fip_company","")
    def set_company(self,company:str)->None: self.session.set("fip_company",company)
    @property
    def currency(self)->str: return self.session.get("fip_currency","USD")
    def set_currency(self,currency:str)->None: self.session.set("fip_currency",currency)
    def register_dataset(self,descriptor:DatasetDescriptor)->None:
        datasets=dict(self.session.get("fip_datasets",{})); datasets[descriptor.dataset_type]=descriptor; self.session.set("fip_datasets",datasets)
    def get_dataset(self,dataset_type:str)->DatasetDescriptor|None: return self.session.get("fip_datasets",{}).get(dataset_type)
    def dataset_status(self,dataset_type:str)->str:
        dataset=self.get_dataset(dataset_type); return dataset.status if dataset else "missing"
    def set_capabilities(self,capabilities:set[str])->None: self.session.set("fip_capabilities",set(capabilities))
    def has_capability(self,capability:str)->bool: return capability in self.session.get("fip_capabilities",set())
