import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType

# Load environment variables from .env file
load_dotenv()

# Set the GROQ API key from the .env file
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# check that the database has been instantiated correctly
db = SQLDatabase.from_uri("sqlite:///Databases/northwind.db")

db.get_usable_table_names()

# Initialize the ChatGroq model
llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0,
    verbose=True,
    max_tokens=1024,
)

agent_executor = create_sql_agent(
    llm, db=db, agent_type="zero-shot-react-description", verbose=True
)

agent_executor.invoke({"input": "List names of all the employees who lives in USA"})
