from fastapi import FastAPI
from core.config import get_settings
from api.chat import router as chat_router

app = FastAPI(title="FICE Chatbot")
app.include_router(chat_router)


@app.on_event("startup")
def _startup():
    from services.vectorstore import get_vectordb
    from services.llm import get_llm
    get_vectordb()
    get_llm()


if __name__ == "__main__":
    import uvicorn

    s = get_settings()
    uvicorn.run(app, host="0.0.0.0", port=8000)
