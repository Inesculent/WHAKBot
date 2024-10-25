import uuid
from pathlib import Path
import requests
import base64
from PIL import Image
from io import BytesIO


from langchain.tools import tool
from openai import OpenAI
from pydantic import BaseModel, Field


#CLIENT = OpenAI(api_key="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")

api_key = "key-1TsWZR2IduvodtQnD8Fz646mavmu3Id500FTck88qAqu98XVQ4k1IfbF6EuPz7GHWUXbpfvFg2Ea4Zio7UKlMvaIdYVxNDpK"

class GenerateImageInput(BaseModel):
    image_description: str = Field(
        description="A detailed description of the desired image."
    )


@tool("generate_image", args_schema=GenerateImageInput)
def generate_image(image_description: str) -> str:
    """Call to generate an image and make sure to remind the user to ask for a link in order to get it"""

    t2i_url = "https://api.getimg.ai/v1/flux-schnell/text-to-image"
    t2i_headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    model_id = "absolute-reality-v1-6"

    t2i_input_params = {
        "model": model_id,
        "prompt": image_description,
        "output_format": "jpeg",
        "width": 768,
        "height": 768,
        "steps": 24,
        "guidance":7
    }

    response = requests.post(
        t2i_url,
        headers=t2i_headers,
        params=t2i_input_params
    )


    return response.text


#if __name__ == "__main__":  #this is just test
    #print(generate_image.run("a picture of a crab"))