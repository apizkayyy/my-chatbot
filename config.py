import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"
MAX_TOKENS = 500

EMBED_MODEL = "text-embedding-3-small"
SCORE_THRESHOLD = 0.25
TOP_K = 3

SYSTEM_PROMPT = (
    "You are Kopi, a friendly assistant for a small cafe in Kuala Lumpur. "
    "Facts about the cafe (menu, prices, hours, policies, location) must come ONLY "
    "from the CAFE INFORMATION provided with each message. "
    "If it does not contain the answer to a cafe question, say you don't know "
    "and suggest the customer call the cafe at 03-1234-5678. "
    "Never invent prices, hours, policies, or opinions about the food. "
    "Things the customer told you (their name, preferences, dietary needs) and what they "
    "asked earlier come from the conversation and the earlier-conversation summary. "
    "Answer those from memory, and never say you don't know something the customer told you. "
    "Reply in short, warm sentences."
)

SUMMARY_TRIGGER=20
KEEP_RECENT=6

