# 🚀 SmartPath MVP - AI Career Navigator

**SmartPath** is an AI-powered platform (powered by Google Gemini 2.0) that generates personalized learning roadmaps for IT professionals. The project analyzes the user's current skills and career goals to create a step-by-step development plan based on real-time market requirements.

> Developed for the **Technology Entrepreneurship** course (Week 10 MVP).

![SmartPath Dashboard](https://img.shields.io/badge/Status-MVP-success)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![AI](https://img.shields.io/badge/AI-Gemini%202.0-8E75B2)

---

## 🔥 Key Features

- **🔐 JWT Authentication:** Secure login system using HttpOnly Cookies.
- **🤖 AI Onboarding:** Smart questionnaire to assess user level and career goals.
- **🗺️ Roadmap Generation:** AI creates a personalized skill tree with estimated timelines.
- **💬 AI Career Coach:** Built-in chat bot that answers career questions in context.
- **📊 Market Tracker:** Salary and vacancy analytics dashboard (Demo).
- **🎨 Cyberpunk UI:** Modern dark-mode interface built with TailwindCSS.

---

## 🛠 Tech Stack

- **Language:** Python 3.12
- **Package Manager:** [uv](https://github.com/astral-sh/uv) (Modern & Fast replacement for pip)
- **Framework:** FastAPI
- **AI Engine:** Google Gemini SDK (`google-genai`)
- **Templating:** Jinja2 (SSR - Server Side Rendering)
- **Styling:** TailwindCSS (CDN)
- **Security:** Passlib (Bcrypt), Python-Jose (JWT)

---

## 🚀 How to Run

We use `uv` for dependency management as it is significantly faster and more reliable than standard pip.

### 1. Clone the repository
```bash
git clone <your-repo-link>
cd smartpath_mvp
```

### 2. Install dependencies (using uv)
Instead of creating a venv manually, `uv` handles everything:

```bash
uv sync
```
*This command will create a virtual environment and install all libraries locked in `uv.lock` / `pyproject.toml`.*

### 3. Configure API Key
Open `app/core/config.py` and insert your Google Gemini API Key:

```python
# app/core/config.py
API_KEY_GEMINI = "YOUR_GEMINI_KEY_HERE"
```

### 4. Run the Server
Use `uv run` to start the application:

```bash
uv run fastapi dev app/main.py
```

The server will start at: **http://127.0.0.1:8000**

---

## 🔑 Demo Credentials

To test the MVP functionalities, use the pre-configured admin account:

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin` | `admin` |

*(You can also register a new user flow via the Onboarding process, but the admin account is recommended for quick demo).*

---

## 📂 Project Structure (Clean Architecture)

The project follows Clean Architecture principles for maintainability and scalability:

```text
smartpath-mvp/
├── app/
│   ├── core/           # Configuration & Security (JWT, Hashing)
│   ├── db/             # Mock Database (In-memory storage)
│   ├── routers/        # API Endpoints (Auth, Navigation, Chat)
│   ├── services/       # Business Logic (Gemini AI integration)
│   └── main.py         # Application Entry Point
├── templates/          # HTML Templates (Login, Dashboard, Roadmap)
├── pyproject.toml      # Project dependencies
├── uv.lock             # Dependency lock file (for uv)
└── README.md           # Documentation
```

---

## 🔮 Future Roadmap

- [x] MVP: Roadmap Generation & Basic UI
- [x] MVP: Google Gemini 2.0 Integration
- [ ] Integration with real Job Market APIs (LinkedIn/HeadHunter)
- [ ] PostgreSQL Database implementation (replacing Mock DB)
- [ ] Stripe Payment integration for Pro plans

---

### Authors
Team SmartPath 🚀
```

```