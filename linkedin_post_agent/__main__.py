"""
Entry point for the LinkedIn Post Agent A2A server.
"""

import os
import sys
import uvicorn
import asyncio
from dotenv import load_dotenv

from .task_manager import TaskManager
from .agent import root_agent
from common.a2a_server import create_agent_server


# Configure logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


# Load environment variables from .env file
if os.getenv("APP_ENV") != "production":
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
    else:
        logger.warning(
            f".env file not found at {dotenv_path}. Relying on system environment variables."
        )

# Ensure required environment variables are set
required_env_vars = [
    "LINKEDIN_POST_AGENT_A2A_HOST",
    "LINKEDIN_POST_AGENT_A2A_PORT",
    "CLOUDINARY_CLOUD_NAME",
    "CLOUDINARY_API_KEY",
    "CLOUDINARY_API_SECRET",
    "GOOGLE_API_KEY",
]
for var in required_env_vars:
    if not os.getenv(var):
        raise EnvironmentError(
            f"Required environment variable '{var}' is not set. "
            "Please ensure it is provided either in a .env file (development) "
            "or as a system/container environment variable (production)."
        )


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
    host = os.getenv("LINKEDIN_POST_AGENT_A2A_HOST")
    port = int(os.getenv("LINKEDIN_POST_AGENT_A2A_PORT"))

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
