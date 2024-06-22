def initialize_chat_history():
    from langchain_core.messages import AIMessage

    # Initialize chat history with a welcome message from AIMessage
    return [
        AIMessage(
            content="Hello! I'm InquireDB, an AI SQL Agent. Ask me anything about your database."
        ),
    ]
