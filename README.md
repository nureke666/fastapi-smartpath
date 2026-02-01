# 🚀 SmartPath MVP - AI Career Navigator

**SmartPath** is an AI-powered platform (powered by Google Gemini 2.0) that generates personalized learning roadmaps for IT professionals. The project analyzes the user's current skills and career goals to create a step-by-step development plan based on real-time market requirements.

> Developed for the **Technology Entrepreneurship** course (Week 10 MVP).

![SmartPath Dashboard](https://img.shields.io/badge/Status-MVP-success)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![AI](https://img.shields.io/badge/AI-Gemini%202.0-8E75B2)

---

## 🔥 Key Features

- **🗺️ AI Roadmap Generation:** Generates a personalized skill tree with estimated timelines based on your goal (e.g., "Senior Python Dev").
- **🎓 Interactive Learning:**
    - **Smart Content:** AI-generated summaries and curated resources (articles, videos) for each module.
    - **Quizzes:** Auto-generated quizzes to validate knowledge. (Pass rate: 70%).
- **🤖 Contextual AI Mentor:** Built-in chat bot that answers questions **in the context** of your current learning module.
- **🎮 Gamification:**
    - **XP System:** Earn XP for completing modules.
    - **Badges:** Unlock achievements (e.g., "Explorer", "High Five").
    - **Profile:** Visual dashboard of your progress.
- **🛡️ Security & Stability:**
    - **Rate Limiting:** Protects AI endpoints from abuse.
    - **JWT Auth:** Secure stateless authentication.

---

## 🛠 Tech Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, Pydantic.
- **AI Engine:** Google Gemini 2.0 Flash (via `google-genai` SDK).
- **Frontend:** Vanilla JS + HTML5 + CSS3 (Google Material Design style). No heavy frameworks.
- **Database:** SQLite (MVP) -> PostgreSQL (Production ready).
- **Package Manager:** [uv](https://github.com/astral-sh/uv) (Modern & Fast replacement for pip).

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone <your-repo-link>
cd smartpath_mvp
```

### 2. Install dependencies
We recommend using `uv` for speed, but standard `pip` works too.

**Using uv:**
```bash
uv sync
```

**Using pip:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install .
```

### 3. Configure Environment
Create a `.env` file in the root directory:

```ini
SECRET_KEY=your_random_secret_string
GEMINI_API_KEY=your_google_gemini_api_key
```
*(Get your free Gemini API key at [aistudio.google.com](https://aistudio.google.com/))*

### 4. Run the Backend
```bash
uv run fastapi dev app/main.py
# OR
fastapi dev app/main.py
```
The API will start at **http://127.0.0.1:8000**

### 5. Run the Frontend
Open a new terminal tab, go to the `frontend` folder and start a simple server:

```bash
cd frontend
python3 -m http.server 8080
```
Then open **http://localhost:8080/landing.html** in your browser.

---

## 🔑 Demo Credentials

You can register a new account, or use these defaults if you seeded the DB:

| Role | Username | Password |
|------|----------|----------|
| **User** | `user@example.com` | `password` |

---

## 📂 Project Structure

```text
smartpath-mvp/
├── app/
│   ├── api/            # API Endpoints (Auth, Roadmap, Chat, Quiz)
│   ├── core/           # Config, Security, Rate Limiting
│   ├── db/             # Database Session & Base
│   ├── models/         # SQLAlchemy Models (User, Career, Module, Chat)
│   ├── schemas/        # Pydantic Schemas (Request/Response validation)
│   ├── services/       # AI Logic (Gemini integration)
│   └── main.py         # App Entry Point
├── frontend/           # Static HTML/CSS/JS files
├── pyproject.toml      # Dependencies
└── README.md           # Documentation
```

---

### Authors
Team SmartPath 🚀
