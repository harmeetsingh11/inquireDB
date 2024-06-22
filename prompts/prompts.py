from langchain_core.prompts import ChatPromptTemplate

"""
The get_sql_prompt_template() function specifically prepares a template for prompting the user to write SQL queries based on user's question, given conversation history and schema details. This template is passed to get_sql_chain()
"""


def get_sql_prompt_template():
    template = """
    Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
    
    <SCHEMA>{schema}</SCHEMA>
    
    Conversation History: {chat_history}
    
    Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.
    
    For example:
    Question: List all the Product Names which have been discontinued.
    SQL Query: SELECT ProductName FROM Products WHERE Discontinued = 1;
    Question: How many Employees are there?
    SQL Query: SELECT COUNT(*) FROM Employees;
    
    Your turn:
    
    Question: {question}
    SQL Query:
    """
    return ChatPromptTemplate.from_template(template)


"""
The get_response_prompt_template() function prepares a template for generating prompts where the user is expected to provide natural language responses to SQL queries. This template is then passed to get_response chain function
"""


def get_response_prompt_template():
    template = """
    Based on the table schema below, question, sql query, and sql response, write a natural language response without any header or introductory text. 
    <SCHEMA>{schema}</SCHEMA>

    For example: 
    
    User question: How many orders are shipped to USA?
    SQL Query: SELECT COUNT(*) FROM Orders WHERE ShipCountry = 'USA' OR ShipCountry = 'United States';
    SQL Response: According to our database, there are 2328 orders that have been shipped to the United States of America.
    User question: How many Employees are there?
    SQL Query: SELECT COUNT(*) FROM Employees;
    SQL Response: According to our database, there are 9 employees in total.

    your turn:

    Conversation History: {chat_history}
    SQL Query: <SQL>{query}</SQL>
    User question: {question}
    SQL Response: {response}"""
    return ChatPromptTemplate.from_template(template)
