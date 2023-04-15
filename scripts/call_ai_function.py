import quora_poe as poe
from config import Config

cfg = Config()


# This is a magic function that can do anything with no-code. See
# https://github.com/Torantulino/AI-Functions for more info.
def call_ai_function(function, args, description):
    """Call an AI function"""
    # For each arg, if any are None, convert to "None":
    args = [str(arg) if arg is not None else "None" for arg in args]
    # parse args to comma seperated string
    args = ", ".join(args)
    message = f"""You are now the following python function:

```
# {description}
{function}
```

Only respond with your `return` value, without any exceptions. Any additional text, explanations, or apologies outside `return` value will not be accepted."""

    response = poe.send_message_once(message, is_code_related_task=True)

    return response
