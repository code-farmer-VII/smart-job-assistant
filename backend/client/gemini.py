import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def get_gemini_client():
    """
    Initializes and returns the official Gemini Client.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set properly in .env")
        
    return genai.Client(api_key=api_key)
