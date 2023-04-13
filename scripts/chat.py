import new_bing as nbing


_role_desc = None
_chatbot = None


def create_chat_message(role, content):
    """
    Create a chat message with the given role and content.

    Args:
    role (str): The role of the message sender, e.g., "system", "user", or "assistant".
    content (str): The content of the message.

    Returns:
    dict: A dictionary containing the role and content of the message.
    """
    return {"role": role, "content": content}


def conn(role_desc):
    """
    Connect to the AI and initialize it as a specific role by role descriptions

    Args:
    role_desc (str): A prompt describing what the AI should act

    Returns:
    dict: Our chat format with the AI
    """
    global _chatbot
    assert _chatbot is None, "Chat AI is already connected"
    _role_desc = role_desc
    _chatbot = nbing.new_bot()
    return nbing.ask_question(_role_desc, _chatbot)


def chat(user_input, full_message_history, permanent_memory):
    """
    Interact with the AI, sending user input, message history, and permanent memory.

    Args:
    user_input (str): The input from the user.
    full_message_history (list): The list of all messages sent between the user and the AI.
    permanent_memory (Obj): The memory object containing the permanent memory.
    
    Returns:
    str: The AI's response.
    """
    global _chatbot

    if len(full_message_history) > 0:
        question = f"{full_message_history[-1]['content']}\n\n" \
                   f"{_role_desc}\n\n" \
                   f"Based on the above information, {user_input}"
        relevant_memory = permanent_memory.get_relevant(str(full_message_history[-5:]), 10)
    else:
        question = user_input
        relevant_memory = []

    # TODO: leverage relevant memory, construct context

    # Chat with New Bing assistant to get the reply
    assistant_reply = nbing.ask_question(question, _chatbot)

    # Update full message history
    full_message_history.append(
        create_chat_message(
            "user", user_input))
    full_message_history.append(
        create_chat_message(
            "assistant", assistant_reply))

    return assistant_reply


def close():
    global _chatbot
    assert _chatbot is not None, "Chat AI is not yet connected"
    nbing.close_bot(_chatbot)
