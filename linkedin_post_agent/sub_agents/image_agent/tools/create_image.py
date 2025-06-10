import os
import cloudinary
import cloudinary.uploader
from io import BytesIO
from dotenv import load_dotenv


# Initialize logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


# Load environment variables from .env file if not in production
if os.getenv("APP_ENV") != "production":
    dotenv_path = os.path.join(os.path.dirname(__file__), "../../../.env")
    # Only load dotenv if the file exists
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
    else:
        logger.warning(
            f".env file not found at {dotenv_path}. Relying on system environment variables."
        )

if (
    not os.getenv("CLOUDINARY_CLOUD_NAME")
    or not os.getenv("CLOUDINARY_API_KEY")
    or not os.getenv("CLOUDINARY_API_SECRET")
):
    raise EnvironmentError(
        "Cloudinary environment variables are not set. "
        "Please ensure they are provided either in a .env file (development) "
        "or as system/container environment variables (production)."
    )


from google import genai
from google.genai import types
from google.adk.tools import ToolContext

from ....constants import IMAGE_GENERATION_MODEL


# Initialize the Google Gemini client
client = genai.Client()

# Configure Cloudinary with environment variables
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,  # Always use HTTPS
)


# Function to upload image from bytes to Cloudinary
def upload_image_to_cloudinary(
    image_data: bytes, public_id: str, folder: str = "linkedin_post_agent"
):
    """Uploads an image to Cloudinary from bytes.

    Args:
        image_data (bytes): The image data in bytes format to be uploaded.
        public_id (str): The public ID for the image in Cloudinary.
        folder (str, optional): The folder in Cloudinary where the image will be stored. Defaults to "linkedin_post_agent".

    Returns:
        dict: A dictionary containing the status of the upload, the URL of the uploaded image, and any relevant messages.
    """
    try:
        image_stream = BytesIO(image_data)
        image_stream.name = public_id

        response = cloudinary.uploader.upload(
            image_stream,
            public_id=public_id,
            folder=folder,
            resource_type="image",
        )
        return {
            "status": "success",
            "message": "Image uploaded successfully.",
            "data": {
                "url": response.get("secure_url"),
                "public_id": response.get("public_id"),
                "format": response.get("format"),
                "version": response.get("version"),
            },
        }
    except Exception as e:
        logger.error(f"Error uploading image to Cloudinary: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to upload image to Cloudinary: {str(e)}",
            "data": {},
        }


# Function to create an image based on a prompt using Google Gemini Vision API
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

                # Save to the cloud using Cloudinary
                upload_response = upload_image_to_cloudinary(
                    image_data=image_data,
                    public_id="linkedin_post_image",
                )

                # If upload was successful, save the image URL in state
                if upload_response["status"] == "success":
                    logger.info(
                        f"Image uploaded successfully: {upload_response['data']['url']}"
                    )
                    tool_context.state["linkedin_post_image_url"] = upload_response[
                        "data"
                    ]["url"]

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
                    "data": {
                        "artifact_version": artifact_version,
                        "image_url": upload_response["data"]["url"],
                        "image_public_id": upload_response["data"]["public_id"],
                        "image_format": upload_response["data"]["format"],
                        "image_version": upload_response["data"]["version"],
                    },
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
