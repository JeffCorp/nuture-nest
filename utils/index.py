from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

USER_ID = "user_1"
SESSION_ID = "default"


class Utils:
    @staticmethod
    async def run_session(
        runner_instance: Runner,
        user_queries: list[str] | str = None,
        session_name: str = "default123",
        user_id: str = "user_1",
    ) -> None:
        print(f"\n ### Session: {session_name}")

        # Create or get the session before using it
        try:
            session = await runner_instance.session_service.get_session(
                app_name=runner_instance.app_name,
                user_id=user_id,
                session_id=session_name,
            )

            if not session:
                session = await runner_instance.session_service.create_session(
                    app_name=runner_instance.app_name,
                    user_id=user_id,
                    session_id=session_name,
                )
                print(f"Session created: {session}")
            else:
                print(f"Session found: {session}")
        except Exception:
            print(f"Session not found: {session}")

        # Process queries if provided
        if user_queries:
            # Convert single query to list for uniform processing
            if type(user_queries) == str:
                user_queries = [user_queries]

            # Process each query in the list sequentially
            for query in user_queries:
                print(f"\nUser > {query}")

                # Convert the query string to the ADK Content format
                query = types.Content(role="user", parts=[types.Part(text=query)])

                # Stream the agent's response asynchronously
                async for event in runner_instance.run_async(
                    user_id=user_id, session_id=session_name, new_message=query
                ):
                    # Track which agent is responding
                    agent_name = (
                        event.author
                        if hasattr(event, "author") and event.author
                        else "Unknown"
                    )

                    # Check if the event contains valid content
                    if event.content and event.content.parts:
                        # Filter out empty or "None" responses before printing
                        if (
                            event.content.parts[0].text != "None"
                            and event.content.parts[0].text
                        ):
                            print(f"[{agent_name}] > {event.content.parts[0].text}")
                    # Also log agent invocations even without content
                    elif agent_name and agent_name != "user":
                        print(f"[{agent_name}] - Agent invoked")
        else:
            print("No queries!")


print("✅ Helper functions defined.")
