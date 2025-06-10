"""
Task Manager for LinkedIn A2A Agent
This module defines the TaskManager class for handling agent-to-agent (A2A) tasks
"""

import os
import logging
import tempfile
import uuid
from typing import Dict, Any, Optional

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types as adk_types


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define name for the app
A2A_APP_NAME = "linkedin_a2a_app"


# Task manager class for handling A2A tasks
class TaskManager:
    def __init__(self, agent: Agent):
        logger.info(f"Initializing TaskManager for Agent: {agent.name}")

        self.agent = agent

        # Initialize session and artifact services
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()

        # Create a runner for the agent
        self.runner = Runner(
            agent=self.agent,
            app_name=A2A_APP_NAME,
            session_service=self.session_service,
            artifact_service=self.artifact_service,
        )

    async def process_task(
        self, message: str, context: Dict[str, Any], session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a task with the given message and context.
        This method retrieves or creates a session, runs the agent with the provided message,
        and returns the results including any new messages, image artifacts, raw events,
        tool calls, and tool responses.

        Args:
            message (str): The message to process.
            context (Dict[str, Any]): Context for the task, which may include user_id.
            session_id (Optional[str], optional): The session ID to use for this task.
            If not provided, a new session ID will be created.

        Returns:
            Dict[str, Any]: A dictionary containing the results of the task processing,
            including new_message, image_artifacts, raw_events, tool_calls, tool_responses,
            and session_id.
        """
        # Get the user_id
        user_id = context.get("user_id", "default_user")

        # Create or get the session
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Creating new session ID: {session_id}")

        session = await self.session_service.get_session(
            app_name=A2A_APP_NAME, user_id=user_id, session_id=session_id
        )

        if not session:
            session = await self.session_service.create_session(
                app_name=A2A_APP_NAME, user_id=user_id, session_id=session_id, state={}
            )
            logger.info(f"Created new session with ID: {session_id}")

        # Create user message
        request_content = adk_types.Content(
            parts=[adk_types.Part(text=message)], role="user"
        )

        # Run the agent
        events = self.runner.run_async(
            user_id=user_id, session_id=session_id, new_message=request_content
        )

        # Process the events
        new_message = "(No response)"
        image_artifacts = {}
        raw_events = []
        tool_calls = []
        tool_responses = []

        try:
            async for event in events:
                raw_events.append(event.model_dump(exclude_none=True))

                # Get the new message from the event
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            new_message = part.text

                # Get function call details if available
                calls = event.get_function_calls()
                if calls:
                    for call in calls:
                        logger.info(
                            f"Function call detected: {call.name} with args {call.args}"
                        )
                        tool_calls.append(
                            {"call_id": call.id, "name": call.name, "args": call.args}
                        )

                # Get function response if available
                responses = event.get_function_responses()
                if responses:
                    for response in responses:
                        logger.info(
                            f"Function response received: {response.name} with result {response.response}"
                        )
                        tool_responses.append(
                            {
                                "response_id": response.id,
                                "name": response.name,
                                "result": response.response,
                            }
                        )

                # Get artifacts changes
                if event.actions and event.actions.artifact_delta:
                    logger.info(
                        f"Artifact changes detected: {event.actions.artifact_delta}"
                    )
                    artifact_changes = event.actions.artifact_delta
                    for items in artifact_changes.items():
                        image_artifacts[items[0]] = items[1]
            logger.info(f"Task processed with new message: {new_message}")

            # Return the results
            return {
                "message": new_message,
                "session_id": session_id,
                "status": "success",
                "data": {
                    "image_artifacts": image_artifacts,
                    "raw_events": raw_events,
                    "tool_calls": tool_calls,
                    "tool_responses": tool_responses,
                },
            }
        except Exception as e:
            logger.error(f"Error processing task: {e}")
            return {
                "message": str(e),
                "status": "error",
                "data": {},
            }
