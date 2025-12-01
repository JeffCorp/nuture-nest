from asyncio.runners import Runner
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types

import dotenv
from pathlib import Path

import sys

from tools.email_tool import create_gmail_sender_from_env

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class EscalatorAgent:
    def __init__(self):
        env_path = project_root / "config" / ".env"
        dotenv.load_dotenv(env_path)

        retry_config = types.HttpRetryOptions(
            attempts=5,  # Maximum retry attempts
            exp_base=7,  # Delay multiplier
            initial_delay=1,
            http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
        )

        tools = []
        email_tool = create_gmail_sender_from_env(env_path=env_path)

        if email_tool:
            tools.append(email_tool.send_email)

        self.llm = LlmAgent(
            name="EscalatorAgent",
            model=Gemini(model_name="gemini-2.0-flash-lite", retry_config=retry_config),
            description="""You are an escalator agent. You are responsible for escalating urgent symptoms to the doctor and partner.
            
            **Your ONLY task:**
            Extract the severity information from {severity_score_and_symptoms} (which contains "Severity Score: X" and "Symptoms: ..."), then send an email to both the doctor and partner immediately using the email_tool with:
               - to: comma-separated list of doctor and partner emails (e.g., "doctor@example.com,partner@example.com")
               - subject: "Urgent: High Severity Symptoms Alert for [User Name]"
               - body: A detailed message about the symptoms, severity score, and recommended actions.
               - attachment: leave empty (do not provide this parameter)
                  
           **CRITICAL INSTRUCTIONS:**
           - IGNORE and DO NOT REPEAT any severity information in your response (like "Severity Score: X" or "Symptoms: ...")
           - After calling the email_tool.send_email function, return ONLY the text: "Email sent successfully"
           - Do NOT echo back the severity score or symptoms information
           - Do NOT generate any additional text, explanations, or responses beyond "Email sent successfully"
           - Do NOT respond to the user with severity details
           - Your response must be EXACTLY: "Email sent successfully" and nothing else
          """,
            tools=tools,
            output_key="email_sent_successfully",
        )

    def run(self, user_input: str) -> str:
        runner = Runner(app=self.app, session_service=self.session_service)

        return runner
