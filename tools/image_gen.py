from langchain.tools import tool
from openai import OpenAI
from pydantic import BaseModel, Field
from main import set_environment_variables
import os




class GenerateImageInput(BaseModel):
    image_description: str = Field(
        description="A detailed description of the desired image."
    )


@tool("generate_image", args_schema=GenerateImageInput)
def generate_image(image_description: str) -> str:
    """Call to generate an image and make sure to remind the user to ask for a link in order to get it"""
    set_environment_variables()

    CLIENT = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

    response = CLIENT.images.generate(
        model="dall-e-3",
        prompt=image_description,
        size="1024x1024",
        quality="standard",  # standard or hd
        n=1,
    )
    image_url = response.data[0].url
    return image_url