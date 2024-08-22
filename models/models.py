from pydantic import BaseModel, Json
from typing import Dict, List

class Lines(BaseModel):
    lines: Json[List[Dict[str, float]]]

class SessionData(BaseModel):
    filename: str
