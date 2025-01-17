import os
from decouple import config
from datetime import date


def set_environment_variables(project_name: str = "") -> None:
    if not project_name:
        project_name = f"Test_{date.today()}"

    os.environ["AWS_ACCESS_KEY_ID"] = "YOUR_KEY_HERE"

    os.environ["AWS_SECRET_ACCESS_KEY"] = "YOUR_KEY_HERE"

    os.environ["CHROMADB_TELEMETRY"] = "false"

    os.environ["AWS_PASSWORD"] = str("YOUR_KEY_HERE")

    os.environ["GOOGLE_API_KEY"] = str('YOUR_KEY_HERE')

    os.environ["ANTHROPIC_API_KEY"] = str(config("YOUR_KEY_HERE",
                                                 default="YOUR_KEY_HERE"))
    os.environ["OPENAI_API_KEY"] = str(config("YOUR_KEY_HERE",
                                              default="YOUR_KEY_HERE"))
    os.environ["LANGCHAIN_API_KEY"] = str(config("YOUR_KEY_HERE",
                                                 default="YOUR_KEY_HERE"))
    os.environ["LANGCHAIN_PROJECT"] = project_name
    os.environ['TAVILY_API_KEY'] = str(
        config("YOUR_KEY_HERE", default="YOUR_KEY_HERE"))
    os.environ['FLUX_API_KEY'] = str(
        config("YOUR_KEY_HERE", default="YOUR_KEY_HERE"))

    print("API KEYS LOADED AND TRACING SET WITH PROJECT NAME", project_name)