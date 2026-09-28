import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_openrouter_client():
    """
    Initializes and returns the OpenAI client configured for OpenRouter.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set properly in .env")
        
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
