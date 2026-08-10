import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Select which model to use: "gemini" or "gemma"
ACTIVE_MODEL = os.getenv("ACTIVE_MODEL")

# Gemini settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")

# Local Gemma settings (e.g., via Ollama)
GEMMA_MODEL_NAME = os.getenv("GEMMA_MODEL_NAME")
GEMMA_BASE_URL = os.getenv("GEMMA_BASE_URL")

def get_llm():
    """
    Returns the configured LangChain LLM based on ACTIVE_MODEL.
    """
    if ACTIVE_MODEL.lower() == "gemini":
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL_NAME, 
            google_api_key=GEMINI_API_KEY,
            temperature=0
        )
    elif ACTIVE_MODEL.lower() == "gemma":
        return ChatOllama(
            model=GEMMA_MODEL_NAME,
            base_url=GEMMA_BASE_URL,
            temperature=0
        )
    else:
        raise ValueError(f"Unsupported ACTIVE_MODEL: {ACTIVE_MODEL}")
