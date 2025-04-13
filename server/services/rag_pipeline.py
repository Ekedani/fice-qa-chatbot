from typing import List

from langchain_core.prompts import PromptTemplate
from openai import AsyncOpenAI
from config.settings import DEEPSEEK_API_URL, DEEPSEEK_API_KEY

from models.chat_models import Message

client = AsyncOpenAI(
    base_url=DEEPSEEK_API_URL,
    api_key=DEEPSEEK_API_KEY,
)


# TODO: Replace mock function to simulate context retrieval with vector database
def get_context(question: str) -> str:
    return """
    Факультет інформатики та обчислювальної техніки (ФІОТ) — один із провідних факультетів Національного 
    технічного університету України «Київський політехнічний інститут імені Ігоря Сікорського» (КПІ). 
    ФІОТ готує фахівців у галузях інженерії програмного забезпечення, комп’ютерної інженерії та
    інформаційних систем і технологій. Студенти факультету мають доступ до сучасних лабораторій, 
    беруть участь у наукових проєктах і співпрацюють з провідними ІТ-компаніями, що сприяє їхньому
    професійному розвитку та успішному працевлаштуванню.
    """


SYSTEM_TEMPLATE = """
Ти - асистент Факультету інформатики та обчислювальної техніки КПІ.
Твоє завдання - відповідати на запитання студентів, абітурієнтів та викладачів про факультет та університет.
Використовуй тільки загальновідому інформацію та інформацію з наданого контексту. 
Якщо інформації недостатньо, чесно скажи, що не знаєш відповіді, і запропонуй звернутися до офіційних джерел.
Відповідай коротко та по суті. Якщо це можливо - надавай посилання на використані джерела. 
Використовуй мову запитання для відповідей, проте надавай перевагу українській мові.

Контекст:
{context}
"""


async def get_answer(conversation: List[Message]) -> str:
    question = conversation[-1].content
    context = get_context(question)

    system_message = Message(
        role="system",
        content=PromptTemplate.from_template(SYSTEM_TEMPLATE).format(context=context)
    )
    messages = [
        {"role": system_message.role, "content": system_message.content},
        *[{"role": msg.role, "content": msg.content} for msg in conversation]
    ]

    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.3,
        max_tokens=128
    )

    return response.choices[0].message.content
