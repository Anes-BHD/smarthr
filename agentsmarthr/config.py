from dotenv import load_dotenv
import os


load_dotenv()

SMARTHR_BACKEND_URL = os.getenv("SMARTHR_BACKEND_URL", "http://127.0.0.1:8001")
SMARTHR_BACKEND_TOKEN = os.getenv("SMARTHR_BACKEND_TOKEN", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
ENABLE_LLM_ROUTER = os.getenv("ENABLE_LLM_ROUTER", "true").lower() == "true"
SMARTHR_AGENT_TOKEN = os.getenv("SMARTHR_AGENT_TOKEN", "super-secret-token")
