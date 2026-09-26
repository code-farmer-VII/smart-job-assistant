import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def get_gemini_model(tools=None, system_instruction=None):
    """
    Initializes and returns the Gemini model configured with tools.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("GEMINI_API_KEY is not set properly in .env")
        
    genai.configure(api_key=api_key)
    
    # We use gemini-2.5-flash for fast reasoning and function calling
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        tools=tools,
        system_instruction=system_instruction
    )
    return model
