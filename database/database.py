from langchain_community.utilities import SQLDatabase


def init_database():
    """
    Initializes a connection to a SQLite database located at 'data/northwind.db' and returns an instance of SQLDatabase for interacting with the database.
    """
    db_uri = "sqlite:///data/northwind.db"
    return SQLDatabase.from_uri(db_uri)
