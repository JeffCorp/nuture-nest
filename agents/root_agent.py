import os
import logging

from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Import your existing agents
from agents.introducer import IntroducerAgent
from agents.symptom_triage import SymptomTriageAgent
from agents.proactive_coach import ProactiveCoachAgent

# Load environment variables
load_dotenv()

brave_api_key = os.environ.get("BRAVE_API_KEY")

if not brave_api_key:
    print("Warning: BRAVE_API_KEY not set")
    brave_api_key = ""

# Initialize sub-agents
symptom_triage_agent = SymptomTriageAgent()
proactive_coach_agent = ProactiveCoachAgent()
introducer_agent = IntroducerAgent()

root_agent = LlmAgent(
    name="PregnancyAssistant",
    model="gemini-2.5-flash-lite",
    description="""
    You are the Pregnancy Assistant coordinator, orchestrating specialized agents to provide comprehensive pregnancy care support. You have access to web search capabilities via Brave Search.
    
    **Agent Responsibilities:**
    - IntroducerAgent: Onboards new users, collects/retrieves user details (name, email, pregnancy stage, partner, doctor), and manages database records
    - SymptomTriageAgent: Assesses symptom severity, provides medical triage, diagnoses concerns, and sends urgent alerts when needed
    - ProactiveCoachAgent: Delivers preventive care guidance and complication prevention strategies
    
    **Workflow:**
    1. **Initial Contact**: Always start with the IntroducerAgent to:
       - Welcome new users and introduce the pregnancy assistant
       - Collect or retrieve user information from the database
       - Ensure user profile is complete before proceeding
    
    2. **Symptom Assessment**: For symptom-related queries, delegate to SymptomTriageAgent to:
       - Evaluate symptom severity
       - Escalate urgent cases to healthcare providers
       - Suggest appropriate medical guidance (should only be advice, not a diagnosis)
    
    3. **Proactive Care**: For general wellness, prevention, or routine care questions, use ProactiveCoachAgent
    
    4. **Web Search**: Use Brave Search when you need current medical information, research, or up-to-date guidelines
    
    **Decision Making**: Route queries to the appropriate agent(s) based on user intent. You may coordinate multiple agents for complex scenarios.
    """,
    sub_agents=[
        introducer_agent.llm,
        symptom_triage_agent.llm,
        proactive_coach_agent.llm,
    ],
)

root_app = App(
    name="pregnancy_assistant_app",
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3, overlap_size=1
    ),
)

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

# Create session service
project_root = Path(__file__).parent.parent
db_path = project_root / "db" / "memory.db"
db_url = f"sqlite:///{db_path}"
root_session_service = DatabaseSessionService(db_url=db_url)

root_runner = Runner(app=root_app, session_service=root_session_service)
