import os
from dotenv import load_dotenv


def load_config():
    """
    Loads environment variables from a .env file using dotenv module.
    Sets the 'GROQ_API_KEY' environment variable based on the value
    fetched from the .env file.
    """
    load_dotenv()
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
