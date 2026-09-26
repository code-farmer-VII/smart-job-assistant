import json
import asyncio
import google.generativeai as genai
from typing import List, Dict, Any
from google.generativeai.types import FunctionDeclaration, Tool

from .client import mcp_client
from .gemini import get_gemini_model
from .prompts import SYSTEM_INSTRUCTION

def _mcp_tool_to_gemini(mcp_tool) -> FunctionDeclaration:
    """
    Converts an MCP tool definition to a Gemini FunctionDeclaration.
    """
    return FunctionDeclaration(
        name=mcp_tool.name,
        description=mcp_tool.description,
        parameters=mcp_tool.inputSchema
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
        gemini_tool = Tool(function_declarations=gemini_functions)
        
        # 3. Initialize Gemini model
        model = get_gemini_model(tools=[gemini_tool], system_instruction=SYSTEM_INSTRUCTION)
        chat = model.start_chat()
        
        print(f"[Orchestrator] Sending request to Gemini...")
        # 4. Send message to Gemini
        response = chat.send_message(user_input)
        
        # 5. Handle function calls iteratively
        # Some complex operations might require multiple tool calls in sequence
        while response.function_call:
            fc = response.function_call
            tool_name = fc.name
            
            # Convert protobuf args to dict safely
            try:
                tool_args = type(fc).to_dict(fc).get("args", {})
            except Exception:
                # Fallback for simpler args
                tool_args = dict(fc.args)
                
            print(f"[Orchestrator] Executing MCP Tool: {tool_name} with args {tool_args}")
            
            # Execute via MCP
            try:
                mcp_result = await session.call_tool(tool_name, arguments=tool_args)
                
                # Format result for Gemini
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
            response = chat.send_message(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=tool_name,
                        response=function_response
                    )
                )
            )
            
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
            print(f"Error: {e}")
    else:
        print("Usage: python orchestrator.py 'Add a new skill: Python'")
