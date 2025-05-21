from pydantic import BaseModel
from typing import List


class Msg(BaseModel):
    role: str
    content: str


class ChatReq(BaseModel):
    conversation: List[Msg]


class ChatResp(BaseModel):
    answer: str
