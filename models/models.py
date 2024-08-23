from pydantic import BaseModel, Json
from typing import Dict, List, Any

class Lines(BaseModel):
    lines: Json[Any]

class SessionData(BaseModel):
    filename: str
