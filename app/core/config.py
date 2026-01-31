import os
from dotenv import load_dotenv

load_dotenv()

# API GEMINI (оставляем как было)
API_KEY1 = os.getenv("GEMINI_API_KEY_1")
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_change_me")

# AUTH settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# EMAIL settings (Заглушка)
SMTP_USER = "noreply@smartpath.mvp"