import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"
MAX_TOKENS = 500

EMBED_MODEL = "text-embedding-3-small"
SCORE_THRESHOLD = 0.25
TOP_K = 3

SYSTEM_PROMPT = ...

