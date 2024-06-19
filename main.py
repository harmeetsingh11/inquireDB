import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, inspect
from langchain.chains import create_sql_query_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables from .env file
load_dotenv()

# Set the GROQ API key from the .env file
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Initialize the ChatGroq model
llm = ChatGroq(model="llama3-8b-8192")

# Create a connection to the northwind.db database
# engine = create_engine('sqlite:///Databases/northwind.db')

# Print the dialect
# print(engine.dialect.name)

# Get usable table names
# inspector = inspect(engine)
# table_names = inspector.get_table_names()
# print(table_names)

# Initialize the SQLDatabase utility
db = SQLDatabase.from_uri("sqlite:///Databases/northwind.db")

# Print the dialect
# print(db.dialect)

table_names = db.get_usable_table_names()
# print(table_names)

""" chain = create_sql_query_chain(llm, db)

# Invoke the chain with a question
response = chain.invoke({"question": "List the product names, supplier names, and total quantities ordered for each product. Only include products that have been ordered more than 50 times, and sort the results by the total quantity ordered in descending order."})

print(response) """

# db.run(sql_query)


# Create a connection to the northwind.db database
engine = create_engine("sqlite:///Databases/northwind.db")
inspector = inspect(engine)

# Fetch the table columns using SQLAlchemy directly
table_columns = {}
for table_name in table_names:
    columns = inspector.get_columns(table_name)
    column_names = [column["name"] for column in columns]
    table_columns[table_name] = column_names
# print(table_columns)

# Format table and column information for the prompt
table_info = "\n".join(
    [f"{table}: {', '.join(columns)}" for table, columns in table_columns.items()]
)
# print(table_info)

# Define the system prompt
system = """You are a {dialect} expert. Given an input question, create a syntactically correct {dialect} query to run.
Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per {dialect}. You can order the results to return the most informative data in the database.
Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
Pay attention to use date('now') function to get the current date, if the question involves "today".

Only use the following tables:
{table_info}

Write an initial draft of the query. Then double check the {dialect} query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins

Use format:

First draft: <<FIRST_DRAFT_QUERY>>
Final answer: <<FINAL_ANSWER_QUERY>>

Only output the SQL query without additional context, so that it can be run directly.
"""

prompt = ChatPromptTemplate.from_messages(
    [("system", system), ("human", "{input}")]
).partial(dialect=db.dialect, table_info=table_info, top_k=5)


# Function to parse the final answer from the output
def parse_final_answer(output: str) -> str:
    if "Final answer: " in output:
        return output.split("Final answer: ")[1].strip()
    elif "Final answer:" in output:
        return output.split("Final answer:")[1].strip()
    else:
        return "Error: Final answer not found in output."


# Create the SQL query chain
chain = create_sql_query_chain(llm, db, prompt=prompt) | parse_final_answer

# Example question
question = "List the product names, supplier names, and total quantities ordered for each product. Only include products that have been ordered more than 50 times, and sort the results by the total quantity ordered in descending order."

# Invoke the chain with the question
query = chain.invoke({"question": question})

# Print the query
print(query)
