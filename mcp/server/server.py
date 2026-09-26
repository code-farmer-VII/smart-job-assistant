import os
import sys

# Remove local directory from path temporarily to avoid shadowing the 'mcp' SDK package
_current_dir = sys.path.pop(0)
try:
    from mcp.server.fastmcp import FastMCP
finally:
    sys.path.insert(0, _current_dir)

# Add the mcp directory to path so relative imports work correctly when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.tools import profile, skills, experience, projects, jobs, applications

# Initialize FastMCP Server
# FastMCP uses Python type hints to generate the JSON schema for tools automatically.
mcp = FastMCP("SmartJobAssistant")

# Register Profile Tools
mcp.tool()(profile.get_profile)
mcp.tool()(profile.update_profile)

# Register Skills Tools
mcp.tool()(skills.get_skills)
mcp.tool()(skills.add_skill)

# Register Experience Tools
mcp.tool()(experience.get_experience)
mcp.tool()(experience.add_experience)

# Register Projects Tools
mcp.tool()(projects.get_projects)
mcp.tool()(projects.add_project)

# Register Jobs Tools
mcp.tool()(jobs.get_job)
mcp.tool()(jobs.list_jobs)
mcp.tool()(jobs.add_job)

# Register Applications Tools
mcp.tool()(applications.get_applications)
mcp.tool()(applications.update_application_status)

if __name__ == "__main__":
    # Run using stdin/stdout streams
    mcp.run()
