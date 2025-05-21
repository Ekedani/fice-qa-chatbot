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

    for i in range(0, len(req.conversation) - 1, 2):
        if req.conversation[i].role == "user" and req.conversation[i + 1].role != "user":
            history.append((req.conversation[i].content, req.conversation[i + 1].content))

    result = qa_chain.invoke({
        "input": user_question,
        "chat_history": history,
    })
    return ChatResp(answer=result["answer"])

