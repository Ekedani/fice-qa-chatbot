import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

from models.chat_models import ChatRequest, ChatResponse
from services.rag_pipeline import get_answer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Chatbot API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handles all unhandled exceptions and returns a structured JSON error response.

    Args:
        request (Request): The incoming HTTP request.
        exc (Exception): The exception that was raised.

    Returns:
        JSONResponse: JSON object with error details and a 500 status code.
    """
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "details": str(exc)}
    )


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    """Processes the conversation history through the RAG pipeline and returns the answer.

    The endpoint expects a JSON payload with a conversation array. Example:

        {
           "conversation": [
              {"role": "user", "content": "Hi, what is FICE?"},
              {"role": "assistant", "content": "FICE is one of the Igor Sikorsky Kyiv Polytechnic Institute's structural entities..."},
              {"role": "user", "content": "Tell me more about it."}
           ]
        }

    Args:
        chat_request (ChatRequest): The request body containing the conversation history.

    Returns:
        ChatResponse: A response model containing the generated answer.

    Raises:
        HTTPException: If an error occurs in the RAG pipeline.
    """
    try:
        answer = get_answer(chat_request.conversation)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"RAG pipeline error: {str(exc)}")

    return ChatResponse(answer=answer)


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
