from pathlib import Path
import requests
import base64
import os

from langchain.tools import tool
from pydantic import BaseModel, Field

from aws_link import upload_to_aws
from main import set_environment_variables


class GenerateImageInput(BaseModel):
    image_description: str = Field(
        description="A detailed description of the desired image. Must be a SINGLE STRING"
    )


@tool("generate_image_flux", args_schema=GenerateImageInput)
def generate_image_flux(image_description: str) -> str:
    """Input must be a SINGLE string. Call to generate an image and make sure to remind the user to ask for a link in order to get it"""

    set_environment_variables()
    url = "https://api.getimg.ai/v1/flux-schnell/text-to-image"
    t2i_headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {os.getenv('FLUX_API_KEY')}"
    }

    t2i_input_params = {
        "prompt": image_description,
        "output_format": "jpeg",
        "width": 768,
        "height": 768,
    }

    response = requests.post(
        url,
        headers=t2i_headers,
        json=t2i_input_params
    )



    DIR_NAME = "./images/"
    dirpath = Path(DIR_NAME)
    # create parent dir if doesn't exist
    dirpath.mkdir(parents=True, exist_ok=True)

    decoded_image = base64.b64decode(response.json()['image'])

    image_name = 'currentImage.jpeg'
    image_path = dirpath / image_name

    with open(image_path, 'wb') as image_file:
        image_file.write(decoded_image)

    print(f"Image saved to {image_path}")


    return upload_to_aws(image_path.as_posix())




#if __name__ == "__main__":  #this is just test
    #print(generate_image.run("a picture of a crab"))