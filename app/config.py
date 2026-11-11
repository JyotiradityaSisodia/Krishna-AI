
import os

APP_NAME = "Krishna"

# Brain backend selection
BRAIN_BACKEND = os.getenv("BRAIN_BACKEND", "llamacpp")

# Ollama settings
OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/chat"
)
MODEL_NAME = os.getenv("MODEL_NAME", "phi3:mini")

# General settings
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/krishna.db")
BACKEND_TIMEOUT = 20
DESKTOP_TIMEOUT = 30

# Email settings
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "true").lower() == "true"
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))

# Food ordering
FOOD_PLATFORM = os.getenv("FOOD_PLATFORM", "swiggy")
PLAYWRIGHT_CHROME_PROFILE = os.getenv(
    "PLAYWRIGHT_CHROME_PROFILE",
    r"D:\krishna\data\playwright_food"
)
