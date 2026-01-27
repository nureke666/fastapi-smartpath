import json
from google import genai
from google.genai import types
from app.core.config import API_KEY2

client = genai.Client(api_key=API_KEY2)


def generate_roadmap_ai(role: str, experience: str, time_avail: str):
    prompt = f"""
    Ты ментор. Пользователь: Роль="{role}", Опыт="{experience}", Время="{time_avail}".
    Создай JSON Roadmap (5-6 шагов).
    Верни массив объектов:
    [
      {{"step": "Название шага", "description": "Суть (1 предл)", "time": "Срок"}}
    ]
    ВЕРНИ ТОЛЬКО JSON. Без ```json.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7)
        )
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"AI Error: {e}")
        return [
            {"step": "AI Error", "description": "Service overloaded", "time": "0m"},
            {"step": "Python Basics", "description": "Fallback step", "time": "1 week"}
        ]