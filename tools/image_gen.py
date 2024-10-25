from langchain.tools import tool
from openai import OpenAI
from pydantic import BaseModel, Field

CLIENT = OpenAI(api_key="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")


class GenerateImageInput(BaseModel):
    image_description: str = Field(
        description="A detailed description of the desired image."
    )


@tool("generate_image", args_schema=GenerateImageInput)
def generate_image(image_description: str) -> str:
    """Call to generate an image and make sure to remind the user to ask for a link in order to get it"""

    response = CLIENT.images.generate(
        model="dall-e-3",
        prompt=image_description,
        size="1024x1024",
        quality="standard",  # standard or hd
        n=1,
    )
    image_url = response.data[0].url
    return image_url