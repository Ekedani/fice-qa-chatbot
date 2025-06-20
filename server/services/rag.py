from datetime import datetime

from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.globals import set_debug
from langchain_core.prompts import PromptTemplate

from core.prompt import SYSTEM_PROMPT
from services.llm import get_llm
from services.vectorstore import get_vectordb

set_debug(True)

def get_qa_chain():
    llm = get_llm()
    vectordb = get_vectordb()
    retriever = vectordb.as_retriever(
        search_type="mmr",
        search_kwargs={
            "fetch_k": 50,
            "k": 5,
            "lambda_mult": 0.3,
            "score_threshold": 0.2
        }
    )

    history_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Ти асистент, який переформульовує останнє питання, враховуючи "
         "попередній діалог, щоб краще шукати у базі знань."),
        ("user", "{chat_history}"),
        ("user", "{input}")
    ])

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, history_prompt
    )

    answer_prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "{input}")
    ]).partial(date=datetime.now().strftime("%d.%m.%Y"))

    doc_chain = create_stuff_documents_chain(llm,
                                             answer_prompt,
                                             document_prompt=PromptTemplate.from_template(
                                                 "Source: {source}. Content:\n{page_content}"))
    rag_chain = create_retrieval_chain(history_aware_retriever, doc_chain)

    return rag_chain
