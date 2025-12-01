import sys
import asyncio
import os
from pathlib import Path

from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters

from agents.first_aid import FirstAidAgent
from agents.severity_checker import SeverityCheckerAgent
from tools import email_tool
from tools.triage import TriageTool
from tools.introducer import IntroducerTools

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import MCPToolset, agent_tool, load_memory, preload_memory
from google.genai import types

from agents.escalator import EscalatorAgent

from google.adk.runners import InMemoryRunner


import dotenv

from utils import Utils
from mcp_tools.calendar_tool import CalendarTool

# Initialize email tool from environment variables
# Credentials should be in config/.env as GMAIL_EMAIL and GMAIL_APP_PASSWORD
from tools.email_tool import create_gmail_sender_from_env


class SymptomTriageAgent:
    def __init__(self):
        # Load .env from config folder
        env_path = project_root / "config" / ".env"
        dotenv.load_dotenv(env_path)

        retry_config = types.HttpRetryOptions(
            attempts=5,  # Maximum retry attempts
            exp_base=7,  # Delay multiplier
            initial_delay=1,
            http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
        )

        severity_checker_agent = SeverityCheckerAgent()
        escalator_agent = EscalatorAgent()
        introducer_tools = IntroducerTools()
        first_aid_agent = FirstAidAgent()

        tools_list = []

        # Add introducer tools to get user details
        tools_list.append(introducer_tools.get_user_details)

        email_tool = create_gmail_sender_from_env()

        # Add email tool if available
        if email_tool:
            tools_list.append(email_tool.send_email)

        # Try to add MCP tool for web search (optional)
        try:
            brave_api_key = os.environ.get(
                "BRAVE_API_KEY", "BSAQyVTZEc_aZaeyoQb3i9Vb1HhfWsV"
            )
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

        self.communication_agent = SequentialAgent(
            name="CommunicationAgent",
            # model=Gemini(model_name="gemini-2.5-flash-lite", retry_config=retry_config),
            description="""
            You are a communication agent. You are responsible for using the SeverityCheckerAgent to evaluate symptom severity and the EscalatorAgent to escalate urgent cases to healthcare providers and partner and providing medical guidance (not diagnosis) for pregnant women.
          
          
            **Workflow:**
            1. **Severity Assessment**: 
               - Delegate to the SeverityCheckerAgent to evaluate symptom severity
               - The SeverityCheckerAgent will return: "Severity Score: [1-6]" and "Symptoms: [list]"
               - Extract the severity score from the agent's response (look for "Severity Score: [number]")
               - Keep this severity information INTERNAL - do NOT share it with the user
            
            2. **For Severe Symptoms (score > 4)**:
               - Delegate to the EscalatorAgent to escalate urgent cases to healthcare providers
               - Pass the severity information to EscalatorAgent (it will use it to send the email)
               - The EscalatorAgent will send an email and return "Email sent successfully"
               - IGNORE the EscalatorAgent's response when crafting your message to the user
               
            3. **Provide First Aid Guidance**:
            - Delegate to the FirstAidAgent tool to provide first aid guidance to the user.
            - The FirstAidAgent will return the first aid guidance.
                  
          """,
            sub_agents=[
                severity_checker_agent.llm,
                escalator_agent.llm,
                first_aid_agent.llm,
            ],
        )

        # tools_list.append(agent_tool.AgentTool(first_aid_agent.llm))

        self.llm = LlmAgent(
            model=Gemini(model_name="gemini-2.5-flash-lite", retry_config=retry_config),
            name="SymptomTriageAgent",
            instruction="""
            You are a symptom triage agent. You are responsible for triaging symptoms and providing medical guidance (not diagnosis) for pregnant women.
            
            ** Agent Responsibilities:**
            - You are responsible for triaging symptoms and providing medical guidance (not diagnosis) for pregnant women.
            - You are responsible for escalating urgent cases to healthcare providers and partner.
            - You are responsible for providing first aid guidance to the user.
            
            **Tools:**
            - You have access to the following tools:
              - brave_search: to get the latest medical information and guidelines as per the user's symptoms and pregnancy stage.
              - email_tool: to send emails to the doctor and/or partner.
              - first_aid_agent: to provide first aid guidance to the user.
              
            **Workflow:**
            1. **Search for Medical Information**:
            - Use brave search to get the latest medical information and guidelines as per the user's symptoms and pregnancy stage.
            
            2. **Communicate with the User**:
            - Delegate the SeverityCheckerAgent to evaluate symptom severity and the EscalatorAgent to escalate urgent cases to healthcare providers and partner.
            - The SeverityCheckerAgent will return the severity score and symptoms.
            - The EscalatorAgent will send an email and return "Email sent successfully".
            - The CommunicationAgent will communicate with the user and provide medical guidance (not diagnosis) for pregnant women and escalate urgent cases to healthcare providers and partner.
            - The CommunicationAgent will return the response to the SymptomTriageAgent.
    
            
            **Important:** 
            - Keep user instructions simple and concise.
            - Not more than 50 words.
            
            """,
            sub_agents=[self.communication_agent],
            tools=tools_list if tools_list else None,
        )

        # Create a SQLite database for session storage
        db_path = project_root / "db" / "memory.db"
        db_url = f"sqlite:///{db_path}"
        self.session_service = DatabaseSessionService(db_url=db_url)
        self.memory_service = InMemoryMemoryService()

    def run(self, user_input: str) -> str:
        runner = Runner(app=self.llm.app, session_service=self.session_service)

        return runner


if __name__ == "__main__":
    agent = SymptomTriageAgent()

    session_service = InMemorySessionService()

    # session = session_service.create_session(
    #     app_name="triage_app", user_id="user_1", session_id="default"
    # )
    # asyncio.run(session)

    # Step 3: Create the Runner
    runner = Runner(app=agent.llm.app, session_service=agent.session_service)

    runner_instance = Utils.run_session(
        runner,
        user_queries="Hi, I'm 28 weeks pregnant and I have a headache and a fever",
    )

    asyncio.run(runner_instance)
