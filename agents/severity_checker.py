from asyncio.runners import Runner
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types

import dotenv
from pathlib import Path

import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SeverityCheckerAgent:
    def __init__(self):
        env_path = project_root / "config" / ".env"
        dotenv.load_dotenv(env_path)

        retry_config = types.HttpRetryOptions(
            attempts=5,  # Maximum retry attempts
            exp_base=7,  # Delay multiplier
            initial_delay=1,
            http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
        )

        self.llm = LlmAgent(
            name="SeverityCheckerAgent",
            model=Gemini(model_name="gemini-2.0-flash-lite", retry_config=retry_config),
            description="""
            You are a severity checker agent. Your ONLY responsibility is to evaluate symptom severity and return the results to the parent agent (SymptomTriageAgent).
            
            **Your Task:**
            1. Analyze the symptoms provided by the user
            2. Categorize symptoms and assign a severity score for each category
            3. Calculate an overall severity score (1-6 scale):
               - Low severity: 1-2
               - Medium severity: 3-4
               - High severity: 5-6
            
            **CRITICAL - Response Format:**
            You MUST provide your final response in this exact format. This is your ONLY output - do not add any other text or explanations:
            
            Severity Score: [number between 1-6]
            Symptoms: [list of symptoms analyzed]
            
            **Important:**
            - Do NOT send emails or take any actions beyond severity assessment
            - Do NOT provide medical advice or diagnosis
            - Your response will be used by the SymptomTriageAgent to determine next steps
            - Always return the severity score and symptoms in the format above
            """,
            output_key="severity_score_and_symptoms",
            sub_agents=[],
            tools=[],
        )

    def run(self, user_input: str) -> str:
        runner = Runner(app=self.app, session_service=self.session_service)

        return runner
