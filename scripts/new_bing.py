import asyncio

import EdgeGPT
from config import Config


def new_bot():
    cfg = Config()
    return EdgeGPT.Chatbot(cfg.new_bing_cookies_path, proxy=cfg.proxy_url)


def ask_question(question, chatbot, conversation_style=EdgeGPT.ConversationStyle.creative) -> str:
    response = asyncio.run(chatbot.ask(question, conversation_style=conversation_style))
    try:
        return response["item"]["messages"][1]["text"]
    except KeyError:
        return response["item"]["messages"][1]["hiddenText"]
    except IndexError:
        return "New Bing did not respond anything"


def ask_question_once(question, conversation_style=EdgeGPT.ConversationStyle.creative) -> str:
    chatbot = new_bot()
    response = ask_question(question, chatbot, conversation_style=conversation_style)
    close_bot(chatbot)
    return response


def ask_messages(messages, conversation_style=EdgeGPT.ConversationStyle.creative) -> str:
    question = ""
    for msg in messages:
        question += f"<|start|>{msg['role']}\n{msg['content']}<|end|>\n"
    chatbot = new_bot()
    response = ask_question(question, chatbot, conversation_style=conversation_style)
    close_bot(chatbot)
    return response


def close_bot(chatbot):
    asyncio.run(chatbot.close())
