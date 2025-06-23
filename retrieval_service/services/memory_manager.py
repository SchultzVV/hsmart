from langchain.memory import ConversationBufferMemory

def create_memory():
    return ConversationBufferMemory(
        memory_key="chat_history",
        input_key="question",
        return_messages=True
    )
