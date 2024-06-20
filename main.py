import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.memory import ConversationBufferMemory


def load_environment():
    """Load environment variables from .env file."""
    load_dotenv()
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


def initialize_database(db_uri):
    """Initialize the SQL database."""
    db = SQLDatabase.from_uri(db_uri)
    db.get_usable_table_names()
    return db


def initialize_chat_model(model_name, temperature=0, verbose=True, max_tokens=1024):
    """Initialize the ChatGroq model."""
    return ChatGroq(
        model=model_name,
        temperature=temperature,
        verbose=verbose,
        max_tokens=max_tokens,
    )


def create_agent(
    llm, db, agent_type="zero-shot-react-description", verbose=True, top_k=5
):
    memory = ConversationBufferMemory(memory_key="history", input_key="input")
    """Create the SQL agent executor."""
    return create_sql_agent(
        llm,
        db=db,
        agent_type=agent_type,
        verbose=verbose,
        top_k=top_k,
        handle_parsing_errors=True,
        agent_executor_kwargs={"memory": memory},
        input_variables=["input", "agent_scratchpad", "history"],
    )


def invoke_agent(agent_executor, input_query):
    """Invoke the agent executor with a given query."""
    try:
        response = agent_executor.invoke({"input": input_query})
        return response.get("output", "")
    except Exception as e:
        return f"An error occurred: {e}"


def initialize_system():
    """Initialize the entire system: environment, database, model, and agent."""
    load_environment()

    # Initialize the database
    db_uri = "sqlite:///Databases/northwind.db"
    db = initialize_database(db_uri)

    # Initialize the chat model
    model_name = "llama3-8b-8192"
    llm = initialize_chat_model(model_name)

    # Create the agent executor
    agent_executor = create_agent(llm, db)
    return agent_executor
