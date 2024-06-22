import streamlit as st
from config.config import load_config
from database.database import init_database
from chain.sql_chain import get_response
from handlers.chat_handler import initialize_chat, display_chat, append_message
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables and configurations
load_config()

# Initialize chat history
initialize_chat()

# Set Streamlit page configuration
st.set_page_config(page_title="InquireDB", page_icon=":speech_balloon:")

# Display the title
st.title("Welcome to InquireDB! 💬")

# Initialize database
db = init_database()
st.session_state.db = db

# Display chat messages
display_chat()

# Handle user input
user_query = st.chat_input("Please ask your question...")
if user_query is not None and user_query.strip() != "":
    user_message = HumanMessage(content=user_query)
    append_message(user_message)

    # Display the user's message in the Streamlit chat interface under "Human"
    with st.chat_message("Human"):
        st.markdown(user_query)

    # Retrieve and display the AI's response to the user's query
    with st.chat_message("AI"):
        response = get_response(
            user_query, st.session_state.db, st.session_state.chat_history
        )
        st.markdown(response)

    ai_message = AIMessage(content=response)
    append_message(ai_message)
