from google.adk.agents import LlmAgent
from .constants import GEMINI_MODEL
from .prompt import LINKEDIN_POST_AGENT_PROMPT

from .sub_agents.story_agent import story_agent
from .sub_agents.hashtag_agent import hashtag_agent
from .sub_agents.post_agent import post_agent
from .sub_agents.image_agent import image_agent


linkedin_post_agent = LlmAgent(
    name="linkedin_post_agent",
    description="A manager agent that orchestrates the LinkedIn post generation process.",
    model=GEMINI_MODEL,
    instruction=LINKEDIN_POST_AGENT_PROMPT,
    sub_agents=[story_agent, hashtag_agent, post_agent, image_agent],
)

root_agent = linkedin_post_agent
