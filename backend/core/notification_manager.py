from __future__ import annotations
from models.notification import Notification
from core.session_manager import SessionManager

class NotificationManager:
    def __init__(self,session:SessionManager)->None: self.session=session
    def add(self,title:str,message:str,severity:str="info",workspace_key:str|None=None)->Notification:
        item=Notification(title=title,message=message,severity=severity,workspace_key=workspace_key); notes=list(self.session.get("fip_notifications",[])); notes.insert(0,item); self.session.set("fip_notifications",notes); return item
    def list_all(self)->list[Notification]: return list(self.session.get("fip_notifications",[]))
    def clear(self)->None: self.session.set("fip_notifications",[])
    def remove(self,notification_id:str)->None: self.session.set("fip_notifications",[n for n in self.list_all() if n.notification_id!=notification_id])
