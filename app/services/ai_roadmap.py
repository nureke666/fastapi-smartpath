# app/services/ai_roadmap.py
import json
import google.generativeai as genai
from app.core.config import settings


class AIService:
    def __init__(self):
        # Настраиваем Gemini при запуске
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            print("WARNING: GEMINI_API_KEY is missing in config.py")

    def generate_roadmap(self, role: str, experience: str, goal: str, hours: int):
        """
        Генерирует JSON-структуру роадмапа через Gemini API.
        """
        # Промпт - это инструкция для ИИ. Чем точнее, тем лучше результат.
        prompt = f"""
        Act as a senior IT mentor. Create a custom learning roadmap for a user.

        User Profile:
        - Wants to become: "{role}"
        - Current experience: "{experience}"
        - Main Goal: "{goal}"
        - Available time: {hours} hours/week

        Task:
        Create a roadmap with exactly 5 sequential steps (nodes).
        For each node, generate one quiz question to test the knowledge.

        You must return ONLY valid JSON. Do not write markdown blocks (```json).

        Required JSON Structure:
        {{
            "title": "A catchy title for this roadmap",
            "description": "A short motivating description based on user goal",
            "nodes": [
                {{
                    "title": "Topic Name",
                    "desc": "What to learn and why (2 sentences)",
                    "quiz": {{
                        "text": "A multiple-choice question",
                        "options": ["Option A", "Option B", "Option C"],
                        "correct": 0
                    }}
                }}
            ]
        }}
        """

        try:
            # Отправляем запрос
            response = self.model.generate_content(prompt)
            raw_text = response.text

            # Чистим ответ: Gemini любит оборачивать JSON в ```json ... ```
            cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()

            # Превращаем строку в Python словарь
            data = json.loads(cleaned_text)
            return data

        except Exception as e:
            print(f"Error generating AI roadmap: {e}")
            # Возвращаем запасной вариант, если API упал или вернул кривой JSON
            return self._get_fallback_data(role)

    def _get_fallback_data(self, role):
        return {
            "title": f"Path to {role} (Offline Mode)",
            "description": "AI service is currently unavailable. This is a default template.",
            "nodes": [
                {
                    "title": "Basics",
                    "desc": "Start with the fundamentals.",
                    "quiz": {
                        "text": "Is this a fallback?",
                        "options": ["Yes", "No", "Maybe"],
                        "correct": 0
                    }
                }
            ]
        }


ai_service = AIService()