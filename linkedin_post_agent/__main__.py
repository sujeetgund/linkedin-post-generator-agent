"""
Entry point for the LinkedIn Post Agent A2A server.
"""

import os
import sys
import uvicorn
import asyncio
from dotenv import load_dotenv
import logging

from .task_manager import TaskManager
from .agent import root_agent
from common.a2a_server import create_agent_server


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


# Load environment variables from .env file
# dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
# load_status = load_dotenv(dotenv_path, override=True)


# Global variable for the task manager instance
task_manager: TaskManager | None = None


async def main():
    global task_manager

    # Initialize the root agent and its exit stack
    agent_instance = root_agent
    logger.info(f"Initializing {agent_instance.name} A2A server...")

    # Create the task manager with the agent instance
    task_manager = TaskManager(agent=agent_instance)

    # Set up the host and port for the A2A server
    host = os.getenv("LINKEDIN_POST_AGENT_A2A_HOST", "127.0.0.1")
    port = int(os.getenv("LINKEDIN_POST_AGENT_A2A_PORT", 8003))

    # Create the FastAPI application for the agent server
    app = create_agent_server(
        name="LinkedIn Post Generator",
        description="Agent for generating LinkedIn posts and images",
        task_manager=task_manager,
    )

    # Configure and run the Uvicorn server
    config = uvicorn.Config(app=app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    logger.debug(f"Starting server at {host}:{port}")
    logger.info(f"Server is running at http://{host}:{port}")

    # Serve the application
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)
