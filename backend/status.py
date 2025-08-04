from typing import TypedDict

class Status(TypedDict):
    error: str
    data: dict
    message: str
    code: int

def create_status() -> Status:
    return {
        "error":"", 
        "data":{},
        "message":"",
        "code":0
    }
