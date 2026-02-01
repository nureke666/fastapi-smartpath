# app/schemas/quiz.py
from pydantic import BaseModel
from typing import List

# То, что видит юзер (вопрос + варианты)
class QuestionPublic(BaseModel):
    id: int
    text: str
    options: List[str] # Pydantic сам распарсит JSON строку в список, если мы поможем

# То, что юзер отправляет (ID вопроса + его ответ)
class AnswerSubmit(BaseModel):
    question_id: int
    selected_option_index: int