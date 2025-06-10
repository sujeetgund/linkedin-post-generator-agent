"""
Standardize Agent to Agent (A2A) server implemnetation following Google ADK standards.
This module provides a FastAPI server implementation for handling A2A communications.
"""

import os
import json
import inspect
from typing import Dict, Any, Optional

from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """
    Model for the request body of an agent-to-agent communication.
    """

    message: str = Field(..., description="The message to be sent to the agent.")
    context: Dict[str, Any] = Field(
        default_factory=dict, description="Contextual information for the agent."
    )
    session_id: Optional[str] = Field(
        None, description="Optional session identifier for tracking the conversation."
    )


class AgentResponse(BaseModel):
    """
    Model for the response body of an agent-to-agent communication.
    """

    message: str = Field(..., description="The response message from the agent.")
    session_id: Optional[str] = Field(
        None, description="Optional session identifier for tracking the conversation."
    )
    status: str = Field(default="success", description="Status of the response.")
    data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional data returned by the agent",
    )


# Helper function to create server
def create_agent_server(name: str, description: str, task_manager: Any) -> FastAPI:
    # Create a FastAPI application instance
    app = FastAPI(title=f"{name} Agent", description=description)

    # Define the path to the agent's card information
    module_path = inspect.getmodule(inspect.stack()[1][0]).__file__
    well_known_path = os.path.join(os.path.dirname(module_path), ".well-known")
    agent_json_path = os.path.join(well_known_path, "agent.json")

    # run endpoint to process tasks
    @app.post("/run", response_model=AgentResponse)
    async def run(request: AgentRequest = Body(...)) -> AgentResponse:
        try:
            result = await task_manager.process_task(
                request.message, request.context, request.session_id
            )
            return AgentResponse(
                message=result.get("message", "Task completed successfully."),
                session_id=result.get("session_id", None),
                status=result.get("status", "success"),
                data=result.get("data", {}),
            )
        except Exception as e:
            return AgentResponse(
                message=f"Error processing task: {str(e)}",
                session_id=request.session_id,
                status="error",
                data={"error_type": type(e).__name__, "error_message": str(e)},
            )

    # agent_card endpoint to retrieve agent information
    @app.get("/.well-known/agent.json", response_model=Dict[str, Any])
    async def get_agent_card():
        """
        Endpoint to retrieve the agent's card information.
        """
        with open(agent_json_path, "r") as f:
            agent_card = json.load(f)
            return JSONResponse(content=agent_card)

    return app
