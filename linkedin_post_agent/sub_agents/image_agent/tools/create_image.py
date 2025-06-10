from dotenv import load_dotenv

load_dotenv()
from google import genai
from google.genai import types
from google.adk.tools import ToolContext
from ....constants import IMAGE_GENERATION_MODEL
import logging


# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(), logging.FileHandler("create_image.log")],
)
logger = logging.getLogger(__name__)


client = genai.Client()


async def create_image(prompt: str, tool_context: ToolContext):
    """Generates an image based on the provided prompt using Google Gemini Vision API.

    Args:
        prompt (str): The text prompt to generate an image from.

    Returns:
        dict: A dictionary containing the status of the image generation, the generated image data, and any relevant messages.
    """
    logger.info(f"--- Tool: create_image ---")

    # Validate the prompt
    cleaned_prompt = prompt.strip()
    if not cleaned_prompt:
        return {
            "status": "error",
            "message": "Prompt is empty. Please provide a valid prompt for image generation.",
        }

    try:
        # Send the request to generate an image using the Gemini Image Generation API
        response = client.models.generate_content(
            model=IMAGE_GENERATION_MODEL,
            contents=f"Generate image for the following prompt: {cleaned_prompt}",
            config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"]),
        )

        # Check if the response contains candidates
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                logger.info("Inline data found in the image part.")

                # Extract the image data and MIME type from the inline data
                image_data = part.inline_data.data
                image_mime_type = part.inline_data.mime_type

                # Save the image as an artifact
                artifact = types.Part(
                    inline_data=types.Blob(data=image_data, mime_type=image_mime_type)
                )
                artifact_version = await tool_context.save_artifact(
                    filename="linkedin_post_image.png", artifact=artifact
                )

                # Log the successful image generation
                logger.info(
                    f"Image saved with artifact version: {artifact_version}",
                    f"Generated image part with MIME type: {image_mime_type}",
                )

                # Return the success response with the artifact version and cleaned prompt
                return {
                    "status": "success",
                    "message": "Image generated successfully.",
                    "artifact_version": artifact_version,
                    "prompt_used": cleaned_prompt,
                }

        # If no inline data is found, log an error
        logger.error("No inline data found in the image part of the response.")
        return {
            "status": "error",
            "message": "No image data found in the response. Please try again with a different prompt.",
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred while generating the image: {str(e)}",
        }
