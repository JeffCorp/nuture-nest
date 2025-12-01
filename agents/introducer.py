from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types

from google.adk.runners import Runner

from tools.introducer import IntroducerTools


class IntroducerAgent:
    def __init__(self):
        retry_config = types.HttpRetryOptions(
            attempts=5,  # Maximum retry attempts
            exp_base=7,  # Delay multiplier
            initial_delay=1,
            http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
        )

        introducer_tools = IntroducerTools()

        self.llm = LlmAgent(
            name="IntroducerAgent",
            model=Gemini(model_name="gemini-2.0-flash-lite", retry_config=retry_config),
            description="""
              You are a introducer agent
              - introduce the user to the pregnancy assistant
              - ask the user for their email
              - check if the user is in the database with the authenticate_user tool
              - ask the user for their verification code
              - verify the user with the verify_user tool
              
              if the user is not in the database, ask the user for their name since we already have their email
              - ask the user for their name
              - ask the user for their pregnancy details
              - ask the user for their partner's details
              - ask for their doctor's details
              - save the user details with the save_user_details tool

              else if the user is in the database, return the user details with the get_user_details tool
            """,
            tools=[
                introducer_tools.save_user_details,
                introducer_tools.get_user_details,
                introducer_tools.authenticate_user,
                introducer_tools.verify_user,
            ],
        )

    def run(self, user_input: str) -> str:
        runner = Runner(app=self.app, session_service=self.session_service)

        return runner
