import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from utils.utils import initialize_chat_history


def initialize_chat():
    """
    Initializes the chat history in Streamlit session state if it doesn't exist.
    """
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = initialize_chat_history()


def display_chat():
    """
    Displays messages stored in the chat history on the Streamlit user interface,
    distinguishing between AI messages and human messages.
    """
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)


def append_message(message):
    """
    Appends a new message to the chat history in Streamlit session state.

    """
    st.session_state.chat_history.append(message)
