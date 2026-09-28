import json
import asyncio
from google import genai
from google.genai import types
from typing import List, Dict, Any

from .client import mcp_client
from .gemini import get_gemini_client
from .prompts import SYSTEM_INSTRUCTION

def _clean_schema(schema: dict, is_properties_dict=False) -> dict:
    if not isinstance(schema, dict):
        return schema
        
    keys_to_remove = {"default", "title", "additionalProperties"}
    cleaned = {}
    
    # Handle Pydantic's anyOf for Optional fields
    if "anyOf" in schema:
        # Just grab the first non-null type from anyOf
        for option in schema["anyOf"]:
            if isinstance(option, dict) and option.get("type") != "null":
                cleaned.update(_clean_schema(option))
                break
                
    for k, v in schema.items():
        if not is_properties_dict and k in keys_to_remove:
            continue
        if k == "anyOf":
            continue
            
        if isinstance(v, dict):
            cleaned[k] = _clean_schema(v, is_properties_dict=(k == "properties"))
        elif isinstance(v, list):
            cleaned[k] = [_clean_schema(i) if isinstance(i, dict) else i for i in v]
        else:
            cleaned[k] = v
            
    return cleaned

def _mcp_tool_to_gemini(mcp_tool) -> types.FunctionDeclaration:
    """
    Converts an MCP tool definition to a Gemini FunctionDeclaration.
    """
    cleaned_schema = _clean_schema(mcp_tool.input_schema)
    return types.FunctionDeclaration(
        name=mcp_tool.name,
        description=mcp_tool.description,
        parameters=cleaned_schema
    )

async def process_user_request(user_input: str) -> str:
    """
    1. Connects to MCP Server.
    2. Fetches available tools.
    3. Sends user input to Gemini with tools.
    4. Iteratively executes tool calls and returns results to Gemini.
    5. Returns Gemini's final response.
    """
    async with mcp_client() as session:
        # 1. Get tools from MCP server
        tools_response = await session.list_tools()
        mcp_tools = tools_response.tools
        
        # 2. Convert to Gemini format
        gemini_functions = [_mcp_tool_to_gemini(t) for t in mcp_tools]
        gemini_tool = types.Tool(function_declarations=gemini_functions)
        
        # 3. Initialize Gemini client
        client = get_gemini_client()
        config = types.GenerateContentConfig(
            tools=[gemini_tool],
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.7
        )
        chat = client.chats.create(model="gemini-3.8-flash", config=config)
        
        print(f"[Orchestrator] Sending request to Gemini...")
        # 4. Send message to Gemini
        response = chat.send_message(user_input)
        
        # 5. Handle function calls iteratively
        while response.function_calls:
            fc = response.function_calls[0]
            tool_name = fc.name
            tool_args = dict(fc.args) if fc.args else {}
                
            print(f"[Orchestrator] Executing MCP Tool: {tool_name} with args {tool_args}")
            
            # Execute via MCP
            try:
                mcp_result = await session.call_tool(tool_name, arguments=tool_args)
                
                result_text = "\n".join([
                    c.text for c in mcp_result.content 
                    if getattr(c, 'type', '') == 'text' or hasattr(c, 'text')
                ])
                if not result_text:
                     result_text = str(mcp_result)
                
                function_response = {"result": result_text}
                print(f"[Orchestrator] Tool success: {result_text}")
                
            except Exception as e:
                print(f"[Orchestrator] Error executing {tool_name}: {e}")
                function_response = {"error": str(e)}
                
            # Send tool result back to Gemini
            part = types.Part.from_function_response(
                name=tool_name,
                response=function_response
            )
            response = chat.send_message(part)
            
        return response.text

if __name__ == "__main__":
    # Simple CLI for testing locally
    import sys
    if len(sys.argv) > 1:
        user_msg = " ".join(sys.argv[1:])
        try:
            result = asyncio.run(process_user_request(user_msg))
            print("\n--- Final Response ---\n")
            print(result)
        except Exception as e:
            import traceback
            traceback.print_exc()
    else:
        print("Usage: python orchestrator.py 'Add a new skill: Python'")
