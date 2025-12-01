from google.adk import Runner
from google.adk.agents import LlmAgent


class FirstAidAgent:
    def __init__(self):
        self.llm = LlmAgent(
            name="FirstAidAgent",
            model="gemini-2.0-flash-lite",
            description="""You are a first aid agent. You are responsible for providing first aid guidance to the user.
            
            **Workflow:**
            1. Get information from the escalator agent 
            2. Give the user a sense of calm and urgency to help them stay relaxed while preparing for the emergency.
            """,
            output_key="first_aid_guidance",
        )

    def run(self, user_input: str) -> str:
        runner = Runner(app=self.app, session_service=self.session_service)

        return runner
