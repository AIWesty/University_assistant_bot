from sqlalchemy import select, insert
from app.database import faq, engine
import logging

logger = logging.getLogger(__name__)

async def get_all_questions():
    """
    Возвращает список кортежей: [(id, question), ...]
    """
    async with engine.connect() as conn:
        result = await conn.execute(select(faq.c.id, faq.c.question))
        rows = result.mappings().all()
        return [(int(r["id"]), r["question"]) for r in rows]

async def get_answer_by_id(faq_id: int):
    """
    Возвращает текст ответа или None
    """
    async with engine.connect() as conn:
        result = await conn.execute(select(faq.c.answer).where(faq.c.id == faq_id))
        # scalar_one_or_none удобно для получения одного скалярного значения
        answer = result.scalar_one_or_none()
        return answer

async def add_faq(question: str, answer: str):
    """
    Добавляет запись. Возвращает True/False (или можно возвращать id при поддержке RETURNING).
    """
    try:
        async with engine.begin() as conn:
            await conn.execute(insert(faq).values(question=question, answer=answer))
        logger.info("FAQ added: %s", question)
        return True
    except Exception as e:
        logger.exception("Failed to add FAQ: %s", e)
        return False