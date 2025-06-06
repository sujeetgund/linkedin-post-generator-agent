from google.adk.agents import LlmAgent
from ...constants import GEMINI_MODEL
from .prompt import HASHTAG_AGENT_PROMPT


hashtag_agent = LlmAgent(
    name="hashtag_agent",
    description="Hashtag Generator specialized in creating relevant and optimized hashtags for LinkedIn posts.",
    instruction=HASHTAG_AGENT_PROMPT,
    model=GEMINI_MODEL,
)
