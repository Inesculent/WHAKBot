import requests
from langchain.tools import tool
from pydantic import BaseModel, Field
from gtts import gTTS
from aws_link import upload_to_aws


class TTS(BaseModel):
    query: str = Field(
        description="The tool to convert to text-to-speech using TTS. Input must be a single string"
    )


@tool("tts", args_schema=TTS)
def tts(query: str) -> str:
    """Input to this tool must be a SINGLE STRING"""

    # = web_search_link(query)
    #print("Saved!")

    audio = gTTS(text=query, lang="en", slow=False)
    print("Saved!")

    audio.save('audio.mp3')

    return upload_to_aws("audio.mp3")



