from fastapi import APIRouter, HTTPException
from typing import List, Tuple
from langchain.chains import ConversationalRetrievalChain

from schemas import ChatReq, ChatResp
from api.deps import QAChain, ApiKey

router = APIRouter()


@router.post("/chat", response_model=ChatResp, dependencies=[ApiKey])
async def chat_endpoint(
        req: ChatReq,
        qa_chain: ConversationalRetrievalChain = QAChain
):
    if not req.conversation:
        raise HTTPException(400, "Empty dialog")

    user_question = req.conversation[-1].content.strip()
    history: List[Tuple[str, str]] = []

    last_user_msg = None
    for msg in req.conversation[:-1]:
        if msg.role == "user":
            last_user_msg = msg.content
        elif msg.role != "user" and last_user_msg:
            history.append ((last_user_msg, msg.content))
            last_user_msg = None

    result = qa_chain.invoke({
        "input": user_question,
        "chat_history": history,
    })
    return ChatResp(answer=result["answer"])

