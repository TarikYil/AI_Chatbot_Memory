from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str  
    content: str

class User(BaseModel):
    user_id: str

class MemoryItem(BaseModel):
    content: str
    embedding: List[float]
    timestamp: float

class Conversation(BaseModel):
    user_id: str
    messages: List[ChatMessage]