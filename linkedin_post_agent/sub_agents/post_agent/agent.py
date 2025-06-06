from google.adk.agents import LlmAgent
from ...constants import GEMINI_MODEL
from .prompt import POST_AGENT_PROMPT


post_agent = LlmAgent(
    name="post_agent",
    description="Post Generator specialized in generating engaging and professional LinkedIn posts.",
    instruction=POST_AGENT_PROMPT,
    model=GEMINI_MODEL,
)
