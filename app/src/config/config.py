import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

# Explicitly load .env from app directory as well as cwd
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
load_dotenv()

# Select which model to use: "gemini" or "gemma" (defaulting to "gemma" if not specified)
ACTIVE_MODEL = os.getenv("ACTIVE_MODEL", "gemma")

# Gemini settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")

# Local Gemma settings (e.g., via Ollama)
GEMMA_MODEL_NAME = os.getenv("GEMMA_MODEL_NAME", "gemma3:4b")
GEMMA_BASE_URL = os.getenv("GEMMA_BASE_URL", "http://localhost:11434")

def get_llm():
    """
    Returns the configured LangChain LLM based on ACTIVE_MODEL.
    """
    current_model = (os.getenv("ACTIVE_MODEL") or ACTIVE_MODEL or "").lower()
    if current_model == "gemini":
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL_NAME, 
            google_api_key=GEMINI_API_KEY,
            temperature=0
        )
    elif current_model == "gemma":
        return ChatOllama(
            model=GEMMA_MODEL_NAME,
            base_url=GEMMA_BASE_URL,
            temperature=0
        )
    else:
        raise ValueError(f"Unsupported or missing ACTIVE_MODEL: '{ACTIVE_MODEL}'. Please set ACTIVE_MODEL to 'gemini' or 'gemma' in .env.")

