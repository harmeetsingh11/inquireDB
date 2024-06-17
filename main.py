import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, inspect
from langchain.chains import create_sql_query_chain

# Load environment variables from .env file
load_dotenv()

# Set the GROQ API key from the .env file
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Initialize the ChatGroq model
llm = ChatGroq(model="llama3-8b-8192")

# Create a connection to the northwind.db database
engine = create_engine('sqlite:///Databases/northwind.db')

# Print the dialect
print(engine.dialect.name)

# Get usable table names
inspector = inspect(engine)
table_names = inspector.get_table_names()
print(table_names)

# Initialize the SQLDatabase utility
db = SQLDatabase.from_uri('sqlite:///Databases/northwind.db')

chain = create_sql_query_chain(llm, db)

# Invoke the chain with a question
response = chain.invoke({"question": "List the product names, supplier names, and total quantities ordered for each product. Only include products that have been ordered more than 50 times, and sort the results by the total quantity ordered in descending order."})

print(response)

# db.run(sql_query)