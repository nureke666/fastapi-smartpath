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

    def generate_roadmap(self, role: str, current_stack: str, goal: str, hours: int, learning_style: str, focus: str, constraints: str):
        prompt = f"""
        Act as a Senior IT Mentor and Curriculum Designer. Create a comprehensive, custom learning roadmap for a user.

        User Profile:
        - Role: "{role}"
        - Current Tech Stack/Skills: "{current_stack}" (Skip what they already know)
        - Goal: "{goal}"
        - Available Time: {hours} hours/week
        - Learning Style: "{learning_style}" (Video-heavy, Documentation-first, Project-based, Mixed)
        - Focus: "{focus}" (portfolio/interview/job-ready)  # if not provided, infer and add to assumptions
        - Constraints: "{constraints}" (free-only, low-spec laptop, no cloud, Linux/Windows-only, etc.)  # optional

        Task:
        1) Analyze the gap between Current Skills and Goal.
        2) Estimate total duration:
           - Provide total_estimated_hours.
           - total_weeks MUST equal ceil(total_estimated_hours / hours_per_week).
        3) Break down into logical modules (usually 4–8, but can be fewer/more if justified).
        4) Emphasize deep understanding and PRACTICAL application.

        Hard Requirements:
        - Return ONLY valid JSON (strict). No markdown, no backticks, no commentary.
        - Use double quotes for all keys/strings.
        - No trailing commas.
        - total_estimated_hours MUST equal sum(modules[].estimated_hours).
        - Each module MUST include: module_id, depends_on, topic, goal, estimated_hours, resources (3), practice_task, checkpoint, quiz (5).
        - Resources MUST be diverse: at least 1 official/docs, at least 1 video/course, at least 1 hands-on/tutorial/repo.
        - Each resource MUST include: title, type, url, search_query, level, why_this, time_estimate_hours.
        - practice_task MUST include: title, description, deliverables, acceptance_criteria, stretch_goals.
        - checkpoint MUST include: what_to_show, how_to_self_check, rubric.
        - Quiz MUST contain 5 MCQs:
          - 2 conceptual, 2 scenario/debugging, 1 trade-off/architecture
          - Each has: question, options[4], correct_index, explanation (include why wrong options are wrong).

        JSON Schema:
        {{
          "roadmap_meta": {{
            "title": "Roadmap Name",
            "description": "Overview...",
            "difficulty": "Beginner/Intermediate/Advanced",
            "hours_per_week": {hours},
            "total_estimated_hours": 0,
            "total_weeks": 0,
            "focus": "portfolio/interview/job-ready",
            "constraints": ["..."],
            "assumptions": ["..."],
            "missing_info": ["..."],
            "milestones": [
              {{
                "name": "Milestone name",
                "modules": ["M1","M2"],
                "outcome": "What the user can do after this milestone",
                "deliverable": "What to show (repo/demo/etc.)"
              }}
            ],
            "environment": {{
              "os": "Linux/Windows/macOS",
              "tools": ["IDE", "Git", "Docker", "..."],
              "setup_steps": ["..."]
            }}
          }},
          "modules": [
            {{
              "module_id": "M1",
              "depends_on": [],
              "topic": "Topic Name",
              "goal": "Specific learning outcome",
              "estimated_hours": 10,
              "resources": [
                {{
                  "title": "Resource Name",
                  "type": "official/docs/video/course/tutorial/repo",
                  "url": "https://...",
                  "search_query": "exact query to find this or a close substitute",
                  "level": "beginner/intermediate/advanced",
                  "why_this": "1 sentence justification",
                  "time_estimate_hours": 2
                }}
              ],
              "practice_task": {{
                "title": "Mini-Project Name",
                "description": "Detailed build instructions",
                "deliverables": ["..."],
                "acceptance_criteria": ["..."],
                "stretch_goals": ["..."]
              }},
              "checkpoint": {{
                "what_to_show": "What proof should exist",
                "how_to_self_check": "How to verify",
                "rubric": ["criteria 1", "criteria 2", "criteria 3"]
              }},
              "quiz": [
                {{
                  "question": "Concept check?",
                  "options": ["A", "B", "C", "D"],
                  "correct_index": 0,
                  "explanation": "Why correct is correct AND why others are wrong."
                }}
              ]
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