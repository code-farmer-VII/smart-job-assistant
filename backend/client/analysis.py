import json
import asyncio
from .client import mcp_client
from .gemini import get_gemini_client

ANALYSIS_PROMPT = """
You are an expert tech recruiter and career coach.
Analyze the following Job Description against the user's Profile, Skills, Experience, and Projects.

Provide the analysis strictly in this structure:

Job Analysis

Skills found:
[List the skills the user has that match the job requirements]

Potential gaps:
[List the job requirements that the user appears to be missing or lacks experience in]

Relevant projects:
[List the user's projects that are most relevant to this job and why]

Suggested preparation:
[List 3-5 specific, actionable preparation steps for an interview for this job]

Here is the context data retrieved from the user's profile:
{data}
"""

async def analyze_job(job_id: str) -> str:
    """
    Retrieves all necessary information via MCP and asks Gemini to analyze the job.
    """
    async with mcp_client() as session:
        # Retrieve aggregated data using the specific MCP tool
        try:
            mcp_result = await session.call_tool("get_job_analysis_context", arguments={"job_id": job_id})
            
            # Extract content from result
            data_text = "\n".join([c.text for c in mcp_result.content if getattr(c, 'type', '') == 'text' or hasattr(c, 'text')])
            if not data_text:
                data_text = str(mcp_result)
                
            # Quick check if it returned an error (like Job not found)
            if "error" in data_text.lower() and "not found" in data_text.lower():
                return f"Error: Job {job_id} not found."
                
        except Exception as e:
            return f"Failed to retrieve context from MCP server: {e}"
            
        prompt = ANALYSIS_PROMPT.format(data=data_text)
        
        # Initialize Gemini client
        client = get_gemini_client()
        
        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction="You are a career and technical interview expert.",
                temperature=1,
            )
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            return f"Failed to generate analysis using Gemini: {e}"

if __name__ == "__main__":
    import sys
    job_id = sys.argv[1] if len(sys.argv) > 1 else "job-001"
    
    print(f"Analyzing job: {job_id}...\n")
    result = asyncio.run(analyze_job(job_id))
    print(result)
