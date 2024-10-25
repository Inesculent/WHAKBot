import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field



class GenerateVideoInput(BaseModel):
    image_description: str = Field(
        description="A detailed description of the desired video."
    )


@tool("generate_video", args_schema=GenerateVideoInput)
def generate_video(video_description: str) -> str:
    """Call to generate a video and make sure to remind the user to ask for a link in order to get it"""

    url = "https://api.aivideoapi.com/runway/generate/text"

    payload = {
        "text_prompt": video_description,
        "model": "gen3",
        "width": 1344,
        "height": 768,
        "motion": 5,
        "seed": 0,
        "upscale": True,
        "interpolate": True,
        "callback_url": "",
        "time": 5
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "15f5d2d4d533d461ca25214d5cd55b358"
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.url

#if __name__ == "__main__":  #this is just test
    #print(generate_image.run("a picture of a crab"))