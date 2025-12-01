from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters


class TriageToolset(McpToolset):
    def __init__(self):
        self.triage_tool = TriageTool()
        self.mcp_triage_server = McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@brave/brave-search-mcp-server",
                        "--transport",
                        "http",
                    ],
                    env={"BRAVE_API_KEY": "BSAQyVTZEc_aZaeyoQb3i9Vb1HhfWsV"},
                ),
            ),
        )


class TriageTool:
    @staticmethod
    def get_triage_tool(user_input: str):
        return user_input

    @staticmethod
    def search_triage_tool():
        mcp_triage_server = McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@brave/brave-search-mcp-server",
                        "--transport",
                        "http",
                    ],
                    env={
                        "BRAVE_API_KEY": "BSAQyVTZEc_aZaeyoQb3i9Vb1HhfWsV",
                        "BRAVE_MCP_TRANSPORT": "stdio",  # Force stdio transport
                    },
                ),
                timeout=30,  # Increase timeout to 30 seconds
            ),
        )
        return mcp_triage_server
