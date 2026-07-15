from __future__ import annotations
from typing import Any
import streamlit as st
from config.enterprise_config import CONFIG

class SessionManager:
    DEFAULTS={"fip_current_workspace":CONFIG.default_workspace,"fip_company":CONFIG.default_company,"fip_currency":CONFIG.default_currency,"fip_user_role":CONFIG.default_user_role,"fip_notifications":[],"fip_datasets":{},"fip_capabilities":set(),"fip_initialized":False}
    def initialize(self)->None:
        for key,value in self.DEFAULTS.items():
            if key not in st.session_state: st.session_state[key]=value.copy() if hasattr(value,"copy") else value
        st.session_state["fip_initialized"]=True
    def get(self,key:str,default:Any=None)->Any: return st.session_state.get(key,default)
    def set(self,key:str,value:Any)->None: st.session_state[key]=value
    def delete(self,key:str)->None: st.session_state.pop(key,None)
    def reset(self)->None:
        for key in list(st.session_state.keys()):
            if key.startswith("fip_"): del st.session_state[key]
        self.initialize()
