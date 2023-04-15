import poe
from config import Config

_poe = None

_CHAT_GPT = "chinchilla"  # Famous worldwide. Powered by gpt-3.5-turbo.
_CLAUDE_INSTANT = "a2"    # Good at creative writing and tends to give longer and more in-depth answers. Compared to the previously available Claude, Claude-instant is faster and significantly better at non-English languages.
_SAGE = "beaver"          # Good in languages other than English, and also in programming-related tasks. Powered by gpt-3.5-turbo.
_DRAGONFLY = "nutria"     # Gives shorter responses, and excels at following instructions when given examples in the input. Powered by text-davinci-003.


def _check_poe():
    global _poe
    if _poe is None:
        cfg = Config()
        _poe = poe.Client(cfg.poe_p_b_cookie_token, proxy=cfg.proxy_url)


def new_bot():
    _check_poe()
    return _CHAT_GPT  # TODO: Support other chatbots


def send_message(message, chatbot) -> str:
    _check_poe()
    for response in _poe.send_message(chatbot, message):  # noqa: B007
        pass
    return response["text"]


def send_message_once(
    message,
    is_few_shot_message=False,
    is_code_related_task=False
) -> str:
    _check_poe()
    if is_few_shot_message:
        chatbot = _DRAGONFLY
    elif is_code_related_task:
        chatbot = _SAGE
    else:
        chatbot = _CLAUDE_INSTANT
    for response in _poe.send_message(chatbot, message, with_chat_break=True):  # noqa: B007
        pass
    return response["text"]


def close_bot(chatbot):
    _check_poe()
    _poe.send_chat_break(chatbot)
