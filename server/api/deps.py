from fastapi import Depends
from core.security import verify_api_key
from services.rag import get_qa_chain

QAChain = Depends(get_qa_chain)
ApiKey = Depends(verify_api_key)
