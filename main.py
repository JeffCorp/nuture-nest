import asyncio

from google.adk import Runner
from agents.root_agent import root_app, root_session_service
from agents.proactive_coach import ProactiveCoachAgent
from agents.symptom_triage import SymptomTriageAgent
from utils import Utils


class Main:
    def __init__(self):
        self.orchestrator_app = root_app
        self.symptom_triage_agent = SymptomTriageAgent()
        self.proactive_coach_agent = ProactiveCoachAgent()

    def timer_function(self):
        pass

    async def run_async(self):
        while True:
            input_query = input("Enter your query: ")

            if input_query == "exit":
                break
            runner = Runner(
                app=self.orchestrator_app,
                session_service=root_session_service,
            )
            await Utils.run_session(
                runner,
                user_queries=input_query,
                session_name="default",
            )

    def run(self):
        asyncio.run(self.run_async())


if __name__ == "__main__":
    main = Main()
    main.run()
