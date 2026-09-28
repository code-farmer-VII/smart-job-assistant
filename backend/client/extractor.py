import os
import json
import asyncio
from .client import mcp_client
from .gemini import get_gemini_client
from .parser import parse_file

EXTRACT_PROMPT = """
You are an expert CV and Job Description parser.
Your task is to analyze the following unstructured text and extract structured information from it.

Determine if the text is a CV/Profile or a Job Description.

Based on the information, respond with ONE OR MORE JSON objects representing the MCP tool calls required to save this data.
DO NOT provide any other explanation or text. JUST a valid JSON array of objects.

Format:
[
  {
    "tool": "add_skill",
    "arguments": {
      "name": "Python",
      "level": "Advanced"
    }
  },
  {
    "tool": "add_experience",
    "arguments": {
      "company": "Google",
      "position": "Software Engineer",
      "start_date": "2020-01",
      "end_date": "Present",
      "description": "...",
      "technologies": ["Python", "React"]
    }
  }
]
"""

async def extract_and_save(text_or_path: str) -> str:
    # Check if input is a file path
    if os.path.exists(text_or_path) and os.path.isfile(text_or_path):
        try:
            text = parse_file(text_or_path)
        except Exception as e:
            return f"Failed to parse file: {e}"
    else:
        text = text_or_path

    # 1. Ask Gemini to extract tool calls
    client = get_gemini_client()
    prompt = EXTRACT_PROMPT + "\n\nTEXT:\n" + text
    
    try:
        from google.genai import types
        config = types.GenerateContentConfig(
            system_instruction="You are a data extraction bot. Only output valid JSON arrays.",
            temperature=1,
        )
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=config
        )
        response_text = response.text.strip()
    except Exception as e:
        return f"Failed to generate content from Gemini: {e}"
    
    # Clean markdown formatting if present
    if response_text.startswith("```json"):
        response_text = response_text[7:-3].strip()
    elif response_text.startswith("```"):
        response_text = response_text[3:-3].strip()
        
    try:
        tool_calls = json.loads(response_text)
    except json.JSONDecodeError as e:
        return f"Failed to parse LLM output into JSON: {e}\nOutput was: {response_text}"
        
    if not isinstance(tool_calls, list):
        return "Error: Expected a JSON array of tool calls."
        
    results = []
    # 2. Connect to MCP and execute the tool calls
    async with mcp_client() as session:
        for call in tool_calls:
            tool_name = call.get("tool")
            arguments = call.get("arguments", {})
            
            try:
                mcp_result = await session.call_tool(tool_name, arguments=arguments)
                result_text = "\n".join([c.text for c in mcp_result.content if getattr(c, 'type', '') == 'text' or hasattr(c, 'text')])
                if not result_text:
                    result_text = str(mcp_result)
                results.append(f"[OK] {tool_name} executed successfully")
            except Exception as e:
                results.append(f"[FAIL] Error running {tool_name}: {e}")
                
    if not results:
        return "No relevant data extracted."
        
    return "\n".join(results)

if __name__ == "__main__":
    import sys
    text = sys.argv[1] if len(sys.argv) > 1 else "I worked at Microsoft as a developer using C#."
    result = asyncio.run(extract_and_save(text))
    print("--- Final Response ---")
    print(result)
