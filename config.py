import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")

OWM_API_KEY = os.getenv("OWM_API_KEY")

FATSECRET_CLIENT_ID = os.getenv("FATSECRET_CLIENT_ID")
FATSECRET_CLIENT_SECRET = os.getenv("FATSECRET_CLIENT_SECRET")

FATSECRET_SAVE_PATH = os.getenv("FATSECRET_SAVE_PATH")

EXERCISES_CONFIG_PATH = "exercises.yaml"