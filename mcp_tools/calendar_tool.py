from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters


class CalendarTool(McpToolset):
    def __init__(self):
        self.mcp_calendar_server = McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",  # Run MCP server via npx
                    args=[
                        "-y",  # Argument for npx to auto-confirm install
                        "@modelcontextprotocol/server-everything",
                    ],
                    tool_filter=["getTinyImage"],
                ),
                timeout=30,
            )
        )

    def get_calendar_events(self, start_date: str, end_date: str) -> list[dict]:
        return [
            {
                "title": "Meeting with John",
                "start_date": "2025-11-17",
                "end_date": "2025-11-17",
            }
        ]


if __name__ == "__main__":
    calendar_tool = CalendarTool()
    print(
        calendar_tool.get_calendar_events(
            start_date="2025-11-17", end_date="2025-11-17"
        )
    )
