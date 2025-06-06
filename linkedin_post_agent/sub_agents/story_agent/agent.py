from google.adk.agents import LlmAgent
from ...constants import GEMINI_MODEL
from .prompt import STORY_AGENT_PROMPT


story_agent = LlmAgent(
    name="story_agent",
    description="Generates a compelling first-person behind story for a LinkedIn post.",
    model=GEMINI_MODEL,
    instruction=STORY_AGENT_PROMPT,
)
