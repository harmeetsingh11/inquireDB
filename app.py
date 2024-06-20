import streamlit as st
from main import initialize_system, invoke_agent


def display_text_with_images(text):
    """Dummy function to simulate displaying text with images. Implement as needed."""
    st.markdown(text)


def reset_conversation():
    """Reset the conversation state in Streamlit."""
    st.session_state.messages = []
    st.session_state.agent_executor = initialize_system()


# Initialize chat history and agent executor in Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_executor" not in st.session_state:
    st.session_state.agent_executor = initialize_system()

# Streamlit page configuration
st.set_page_config(page_title="inquireDB")

st.title("Welcome to inquireDB!")

col1, col2 = st.columns([3, 1])
with col2:
    st.button("Reset Chat", on_click=reset_conversation)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            display_text_with_images(message["content"])
        else:
            st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Please ask your question:"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = invoke_agent(st.session_state.agent_executor, prompt)

    # Extract and format the 'output' value from response
    if "An error occurred" in response:
        st.error(response)
    else:
        output = response.strip()
        formatted_output = output.replace("\n\n", "\n")

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            display_text_with_images(formatted_output)
        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": formatted_output}
        )
