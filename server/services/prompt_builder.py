from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from core.prompt import SYSTEM_PROMPT


def get_chat_prompt():
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
        ("system", "{context}"),
        HumanMessagePromptTemplate.from_template("{question}")
    ])
