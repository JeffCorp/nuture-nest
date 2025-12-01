import os
import sys
import asyncio
from pathlib import Path
import dotenv
from google.adk.models.google_llm import Gemini
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from google.genai import types

from google.adk.apps.app import App, EventsCompactionConfig
from mcp import StdioServerParameters

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from tools.triage import TriageTool


class ProactiveCoachAgent:
    def __init__(self) -> None:
        env_path = project_root / "config" / ".env"
        dotenv.load_dotenv(env_path)

        retry_config = types.HttpRetryOptions(
            attempts=5,  # Maximum retry attempts
            exp_base=7,  # Delay multiplier
            initial_delay=1,
            http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
        )
        tools_list = []

        try:
            brave_api_key = os.environ.get("BRAVE_API_KEY")
            brave_mcp_tool = MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command="npx",
                        args=["-y", "@brave/brave-search-mcp-server"],
                        env={
                            "BRAVE_API_KEY": brave_api_key,
                            "BRAVE_MCP_TRANSPORT": "stdio",
                        },
                    ),
                    timeout=30,  # Increase timeout
                ),
            )
            tools_list.append(brave_mcp_tool)
            print("✓ MCP tool (Brave Search) initialized successfully")
        except Exception as e:
            print(f"⚠ Warning: Could not initialize MCP tool (Brave Search): {e}")
            print("The agent will work without web search capabilities.")
            # Continue without MCP tool

        self.llm = LlmAgent(
            name="ProactiveCoachAgent",
            model=Gemini(model_name="gemini-2.0-flash", retry_config=retry_config),
            description="""
            You are a proactive coach. You are responsible for providing proactive care and prevention of complications for pregnant women.
            
            You have access to web search capabilities via brave_search tool. You can use this tool to get the latest medical information and guidelines as per the user's symptoms and pregnancy stage.
            """,
            tools=tools_list if tools_list else None,
        )

        self.session_service = InMemorySessionService()

    def run(self, user_input: str) -> str:
        runner = InMemoryRunner(app=self.app, session_service=self.session_service)

        return runner


if __name__ == "__main__":
    agent = ProactiveCoachAgent()
    runner = agent.run("Hi, I'm 28 weeks pregnant and I have a headache and a fever")
    asyncio.run(runner.run_async())
