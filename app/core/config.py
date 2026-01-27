import os
from dotenv import load_dotenv
load_dotenv()

# API GEMINI
API_KEY1 = os.getenv("GEMINI_API_KEY_1")
API_KEY2 = os.getenv("GEMINI_API_KEY_2")
API_KEY3 = os.getenv("GEMINI_API_KEY_3")

# SECRET KEY
SECRET_KEY = os.getenv("SECRET_KEY")

# AUTH settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
