from google.adk.agents import LlmAgent
from ...constants import GEMINI_MODEL
from .prompt import IMAGE_AGENT_PROMPT
from .tools.create_image import create_image


image_agent = LlmAgent(
    name="image_agent",
    description="Image Generator specialized in crafting prompts and creating images that enhance LinkedIn posts.",
    model=GEMINI_MODEL,
    instruction=IMAGE_AGENT_PROMPT,
    tools=[create_image],
)
