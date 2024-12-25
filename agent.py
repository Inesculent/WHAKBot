import subprocess
import sys

import boto3
from langchain_core.messages import AIMessage
from main import set_environment_variables
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools.tavily_search import TavilySearchResults
from typing import Annotated, TypedDict
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import AnyMessage, add_messages
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import tools_condition
from sqlconnector import open_connection, insert_data, close_connection
import os
import importlib
from tool_loader import load_tool_from_json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import signal



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  #Allow React app origin
    allow_credentials=True,
    allow_methods=["*"],  #Allow all HTTP methods
    allow_headers=["*"],  #Allow all headers
)

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: MessagesState, config: RunnableConfig):

        while True:

            state = {**state}
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                    not result.content
                    or isinstance(result.content, list)
                    and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}

# Function to dynamically load tools from a txt (Replaced with json loader)
def load_tools_from_txt(filepath, tools):

    with open(filepath, 'r') as file:
        for line in file:
            module_name, function_name = line.strip().split(':')
            try:
                #Get the module and function
                module = importlib.import_module(module_name)
                function = getattr(module, function_name)
                #Append the function to the tools
                tools.append(function)
            except (ModuleNotFoundError, AttributeError) as e:
                # Print error but continue to the next tool
                print(f"Error: Could not load {module_name}:{function_name}. {e}")
    return tools



#Set environment variables
set_environment_variables()

SCRIPT_AGENT_NAME = "script_agent"
TAVILY_TOOL = TavilySearchResults(max_results=10, tavily_api_key=os.environ['TAVILY_API_KEY'])

#Define the tools
tools = []
tools_json = 'tools.json'
#Load the primary tools
tools = load_tool_from_json(tools_json, tools)

#Load the generated tools
tools_json = 'generated_tools.json'
tools = load_tool_from_json(tools_json, tools)
tools.append(TAVILY_TOOL)
tool_node = ToolNode(tools)

#Set up a basic prompt
primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """"
You are a helpful and loyal agent with access to many tools.

If you are asked to create a tool, first consider if the tool already exists. If the tool exists, then refuse to create a new one.
Otherwise, use create_tool. Once the tool returns successfully, append the tool to yourself.

If you need to pull information from a different conversation session, use the SQL_RAG tool. Otherwise, please use the current memory.
The SQL_RAG tool can also be useful in scenarios where a question appears without much context. Assume that the context might've been provided in a different conversation first,
before defaulting to a custom response.

If you are asked to generate an image, use the generate_image tool. If you use this tool, be sure to only output the url generated by it and nothing else. If this image fails, attempt
to use the image_gen_flux tool.

If you are asked how to do something, or information on something use your TAVILY_SEARCH_TOOL to search for urls related to the topic, please summarize the contents instead of returning the raw output.
        """
,
        ),
        ("placeholder", "{messages}"),
    ]
)


#Set up the agent
llm = ChatOpenAI(model="gpt-4o-mini", temperature=1, api_key = os.environ["OPENAI_API_KEY"])
model = primary_assistant_prompt | llm.bind_tools(tools)


workflow = StateGraph(MessagesState)

# Define the two nodes we will cycle between
workflow.add_node("agent", Assistant(model))
workflow.add_node("tools", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.add_edge(START, "agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    tools_condition,
)
workflow.add_edge("tools", "agent")

agent = workflow.compile()
printed_messages = set()


#This is for user uploaded data. Current unsupported through requests, but the code is provided here.
#uploads = st.file_uploader("Upload file")

#if uploads is not None:

    #s3 = boto3.client('s3')
    #bucket = 'rag-pdf-storage'
    #filename = str(uploads.name)
    #st.write(filename)
    #s3.upload_fileobj(Fileobj = uploads, Bucket = bucket, Key = filename)

    #st.write("Successfully uploaded file " + uploads.name + "!")




# Accept user input
class MessageRequest(BaseModel):
    message: str

messages = []
on = False

@app.post("/chatbot")
async def chatbot(prompt: MessageRequest):

    try:

        user_message = prompt.message
        messages.append({"role": "user", "content": user_message})

        #Invoke the model
        final_state = agent.invoke({"messages": messages})

        #Extract the assistant's response from final_state
        assistant_response = final_state.get("messages")


        if assistant_response:
            #Get the latest AI message
            if isinstance(assistant_response, list):
                assistant_response = assistant_response[-1]  # Get the last message

            # Check if the response is an AIMessage
            if isinstance(assistant_response, AIMessage):
                msg_repr = assistant_response.content  # Access the content of the AIMessage
                # Append only the content to the session state
                messages.append({"role": "assistant", "content": msg_repr})
            else:
                msg_repr = "No valid AI message found."
        else:
            msg_repr = "No messages received."

        #Check the toggle to see if we connect to database
        if on:
            conn = open_connection()
            user_input = messages[-2]["content"]
            assistant_response = messages[-1]["content"]
            insert_data(conn, user_input, assistant_response)
            close_connection(conn)

            return {"response": msg_repr + "\nSuccessfully appended to database!"}


        return {"response": msg_repr}



    except Exception as e:
        return(f"Error invoking the model: {e}")


#To reload the application after appending
@app.post("/reload")
async def reload_server():
    # Start a new subprocess for Uvicorn to reload the application
    subprocess.Popen(["uvicorn", "agent:app", "--host", "127.0.0.1", "--port", "8000"])

    # Attempt to terminate the current process to release the port
    os.kill(os.getpid(), signal.SIGTERM)

    return {"status": "reloading"}