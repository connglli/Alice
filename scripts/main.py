import json
import random
import commands as cmd
import utils
from memory import get_memory, get_supported_memory_backends
import data
import chat
from colorama import Fore, Style
from spinner import Spinner
import time
import speak
from config import Config
from json_parser import fix_and_parse_json
from ai_config import AIConfig
import traceback
import yaml
import argparse
from logger import logger
import logging


cfg = Config()
ai_name = ""


def attempt_to_fix_json_by_finding_outermost_brackets(json_string):
    if cfg.speak_mode and cfg.debug_mode:
      speak.say_text("I have received an invalid JSON response. Trying to fix it now.")
    logger.typewriter_log("Attempting to fix JSON by finding outermost brackets\n")

    try:
        # Use regex to search for JSON objects
        import regex
        json_pattern = regex.compile(r"\{(?:[^{}]|(?R))*\}")
        json_match = json_pattern.search(json_string)

        if json_match:
            # Extract the valid JSON object from the string
            json_string = json_match.group(0)
            logger.typewriter_log(title="Apparently json was fixed.", title_color=Fore.GREEN)
            if cfg.speak_mode and cfg.debug_mode:
               speak.say_text("Apparently json was fixed.")
        else:
            raise ValueError("No valid JSON object found")

    except (json.JSONDecodeError, ValueError) as e:
        if cfg.speak_mode:
            speak.say_text("Didn't work. I will have to ignore this response then.")
        logger.error("Error: Invalid JSON, setting it to empty JSON now.\n")
        json_string = {}

    return json_string


def print_assistant_thoughts(assistant_reply):
    """Prints the assistant's thoughts to the console"""
    global ai_name
    global cfg
    try:
        try:
            # Parse and print Assistant response
            assistant_reply_json = fix_and_parse_json(assistant_reply)
        except json.JSONDecodeError as e:
            logger.error("Error: Invalid JSON in assistant thoughts\n", assistant_reply)
            assistant_reply_json = attempt_to_fix_json_by_finding_outermost_brackets(assistant_reply)
            assistant_reply_json = fix_and_parse_json(assistant_reply_json)

        # Check if assistant_reply_json is a string and attempt to parse it into a JSON object
        if isinstance(assistant_reply_json, str):
            try:
                assistant_reply_json = json.loads(assistant_reply_json)
            except json.JSONDecodeError as e:
                logger.error("Error: Invalid JSON\n", assistant_reply)
                assistant_reply_json = attempt_to_fix_json_by_finding_outermost_brackets(assistant_reply_json)

        assistant_thoughts_reasoning = None
        assistant_thoughts_plan = None
        assistant_thoughts_speak = None
        assistant_thoughts_criticism = None
        assistant_thoughts = assistant_reply_json.get("thoughts", {})
        assistant_thoughts_text = assistant_thoughts.get("text")

        if assistant_thoughts:
            assistant_thoughts_reasoning = assistant_thoughts.get("reasoning")
            assistant_thoughts_plan = assistant_thoughts.get("plan")
            assistant_thoughts_criticism = assistant_thoughts.get("criticism")
            assistant_thoughts_speak = assistant_thoughts.get("speak")

        logger.typewriter_log(f"{ai_name.upper()} THOUGHTS:", Fore.YELLOW, assistant_thoughts_text)
        logger.typewriter_log("REASONING:", Fore.YELLOW, assistant_thoughts_reasoning)

        if assistant_thoughts_plan:
            logger.typewriter_log("PLAN:", Fore.YELLOW, "")
            # If it's a list, join it into a string
            if isinstance(assistant_thoughts_plan, list):
                assistant_thoughts_plan = "\n".join(assistant_thoughts_plan)
            elif isinstance(assistant_thoughts_plan, dict):
                assistant_thoughts_plan = str(assistant_thoughts_plan)

            # Split the input_string using the newline character and dashes
            lines = assistant_thoughts_plan.split('\n')
            for line in lines:
                line = line.lstrip("- ")
                logger.typewriter_log("- ", Fore.GREEN, line.strip())

        logger.typewriter_log("CRITICISM:", Fore.YELLOW, assistant_thoughts_criticism)
        # Speak the assistant's thoughts
        if cfg.speak_mode and assistant_thoughts_speak:
            speak.say_text(assistant_thoughts_speak)

        return assistant_reply_json
    except json.decoder.JSONDecodeError as e:
        logger.error("Error: Invalid JSON\n", assistant_reply)
        if cfg.speak_mode:
            speak.say_text("I have received an invalid JSON response. I cannot ignore this response.")

    # All other errors, return "Error: + error message"
    except Exception as e:
        call_stack = traceback.format_exc()
        logger.error("Error: \n", call_stack)


def construct_prompt():
    """Construct the prompt for the AI to respond to"""
    config = AIConfig.load()
    if config.ai_name:
        logger.typewriter_log(
            f"Welcome back! ",
            Fore.GREEN,
            f"Would you like me to return to being {config.ai_name}?",
            speak_text=True)
        should_continue = utils.clean_input(f"""Continue with the last settings?
Name:  {config.ai_name}
Role:  {config.ai_role}
Goals: {config.ai_goals}
Continue (y/n): """)
        if should_continue.lower() == "n":
            config = AIConfig()

    if not config.ai_name:
        config = prompt_user()
        config.save()

    # TODO: Get rid of this global
    global ai_name
    ai_name = config.ai_name

    full_prompt = config.construct_full_prompt()
    return full_prompt


def prompt_user():
    """Prompt the user for input"""
    ai_name = ""
    # Construct the prompt
    logger.typewriter_log(
        "Welcome to Alice! ",
        Fore.GREEN,
        "Enter the name of your AI and its role below. Entering nothing will load defaults.",
        speak_text=True)

    # Get AI Name from User
    logger.typewriter_log(
        "Name your AI: ",
        Fore.GREEN,
        "For example, 'Entrepreneur-GPT'")
    ai_name = utils.clean_input("AI Name: ")
    if ai_name == "":
        ai_name = "Entrepreneur-GPT"

    logger.typewriter_log(
        f"{ai_name} here!",
        Fore.LIGHTBLUE_EX,
        "I am at your service.",
        speak_text=True)

    # Get AI Role from User
    logger.typewriter_log(
        "Describe your AI's role: ",
        Fore.GREEN,
        "For example, 'an AI designed to autonomously develop and run businesses with the sole goal of increasing your net worth.'")
    ai_role = utils.clean_input(f"{ai_name} is: ")
    if ai_role == "":
        ai_role = "an AI designed to autonomously develop and run businesses with the sole goal of increasing your net worth."

    # Enter up to 5 goals for the AI
    logger.typewriter_log(
        "Enter up to 5 goals for your AI: ",
        Fore.GREEN,
        "For example: \nIncrease net worth, Grow Twitter Account, Develop and manage multiple businesses autonomously'")
    print("Enter nothing to load defaults, enter nothing when finished.", flush=True)
    ai_goals = []
    for i in range(5):
        ai_goal = utils.clean_input(f"{Fore.LIGHTBLUE_EX}Goal{Style.RESET_ALL} {i+1}: ")
        if ai_goal == "":
            break
        ai_goals.append(ai_goal)
    if len(ai_goals) == 0:
        ai_goals = ["Increase net worth", "Grow Twitter Account",
                    "Develop and manage multiple businesses autonomously"]

    config = AIConfig(ai_name, ai_role, ai_goals)
    return config


def parse_arguments():
    """Parses the arguments passed to the script"""
    global cfg

    cfg.set_debug_mode(False)
    cfg.set_continuous_mode(False)
    cfg.set_speak_mode(False)

    parser = argparse.ArgumentParser(description='Process arguments.')
    parser.add_argument('--continuous', action='store_true', help='Enable Continuous Mode')
    parser.add_argument('--speak', action='store_true', help='Enable Speak Mode')
    parser.add_argument('--debug', action='store_true', help='Enable Debug Mode')
    parser.add_argument('--use-memory', '-m', dest="memory_type", help='Defines which Memory backend to use')
    args = parser.parse_args()

    if args.debug:
        logger.typewriter_log("Debug Mode: ", Fore.GREEN, "ENABLED")
        cfg.set_debug_mode(True)

    if args.continuous:
        logger.typewriter_log("Continuous Mode: ", Fore.RED, "ENABLED")
        logger.typewriter_log(
            "WARNING: ",
            Fore.RED,
            "Continuous mode is not recommended. It is potentially dangerous and may cause your AI to run forever or carry out actions you would not usually authorise. Use at your own risk.")
        cfg.set_continuous_mode(True)

    if args.speak:
        logger.typewriter_log("Speak Mode: ", Fore.GREEN, "ENABLED")
        cfg.set_speak_mode(True)

    if args.memory_type:
        supported_memory = get_supported_memory_backends()
        chosen = args.memory_type
        if not chosen in supported_memory:
            logger.typewriter_log("ONLY THE FOLLOWING MEMORY BACKENDS ARE SUPPORTED: ", Fore.RED, f'{supported_memory}')
            logger.typewriter_log(f"Defaulting to: ", Fore.YELLOW, cfg.memory_backend)
        else:
            cfg.memory_backend = chosen


def main():
    global cfg, ai_name

    parse_arguments()
    logger.set_level(logging.DEBUG if cfg.debug_mode else logging.INFO)

    prompt = construct_prompt()
    if cfg.debug_mode:
        logger.typewriter_log("SYSTEM: ", Fore.YELLOW, prompt)

    # Initialize variables
    full_message_history = []

    # Make a constant

    # Initialize memory and make sure it is empty.
    # this is particularly important for indexing and referencing pinecone memory
    long_term_memory = get_memory(cfg, init=True)
    print('Using memory of type: ' + long_term_memory.__class__.__name__)

    # Connect and initialize our AI
    with Spinner("Connecting to AI assistant..."):
        try:
            assistant_reply = chat.conn(prompt)
        except Exception as e:
            assistant_reply_json = e
        else:
            assistant_reply_json = fix_and_parse_json(assistant_reply)
            if not isinstance(assistant_reply_json, dict):
                assistant_reply_json = {
                    "thoughts": {
                        "text": assistant_reply_json
                    }
                }
    if isinstance(assistant_reply_json, Exception):
        logger.typewriter_log("AI CONNECTION FAILED: ", Fore.RED, str(assistant_reply_json))
        chat.close()
        exit(1)
    else:
        logger.typewriter_log("AI CONNECTED: ", Fore.YELLOW, 
                            assistant_reply_json.get("thoughts", {}).get("text", ""))

    user_input = "Determine which command in COMMANDS list to use first, and respond using the format specified before."
    cmd_result = None
    nr_next_actions = 0

    # Interaction Loop
    while True:
        # Send message to AI, get response
        with Spinner("Thinking... "):
            assistant_reply = chat.chat(user_input, full_message_history, long_term_memory)

        # Print Assistant thoughts
        print_assistant_thoughts(assistant_reply)

        # Get command name and arguments
        try:
            command_name, arguments = cmd.get_command(attempt_to_fix_json_by_finding_outermost_brackets(assistant_reply))
            if cfg.speak_mode:
                speak.say_text(f"I want to execute {command_name}")
        except Exception as e:
            logger.error("Error: \n", str(e))

        if not cfg.continuous_mode and nr_next_actions == 0:
            ### GET USER AUTHORIZATION TO EXECUTE COMMAND ###
            # Get key press: Prompt the user to press enter to continue or escape
            # to exit
            user_input = ""
            logger.typewriter_log(
                "NEXT ACTION: ",
                Fore.CYAN,
                f"COMMAND = {Fore.CYAN}{command_name}{Style.RESET_ALL}  ARGUMENTS = {Fore.CYAN}{arguments}{Style.RESET_ALL}")
            print(
                f"Enter 'y' to authorise command, 'y -N' to run N continuous commands, 'n' to exit program, or enter feedback for {ai_name}...",
                flush=True)
            while True:
                console_input = utils.clean_input(Fore.MAGENTA + "Input: " + Style.RESET_ALL)
                if console_input.lower().rstrip() == "y":
                    user_input = "GENERATE NEXT COMMAND JSON"
                    break
                elif console_input.lower().startswith("y -"):
                    try:
                        nr_next_actions = abs(int(console_input.split(" ")[1]))
                        user_input = "GENERATE NEXT COMMAND JSON"
                    except ValueError:
                        print("Invalid input format. Please enter 'y -n' where n is the number of continuous tasks.")
                        continue
                    break
                elif console_input.lower() == "n":
                    user_input = "EXIT"
                    break
                else:
                    user_input = console_input
                    command_name = "human_feedback"
                    break

            if user_input == "GENERATE NEXT COMMAND JSON":
                logger.typewriter_log(
                    "-=-=-=-=-=-=-= COMMAND AUTHORISED BY USER -=-=-=-=-=-=-=",
                    Fore.MAGENTA,
                    "")
            elif user_input == "EXIT":
                print("Exiting...", flush=True)
                break
        else:
            # Print command
            logger.typewriter_log(
                "NEXT ACTION: ",
                Fore.CYAN,
                f"COMMAND = {Fore.CYAN}{command_name}{Style.RESET_ALL}  ARGUMENTS = {Fore.CYAN}{arguments}{Style.RESET_ALL}")

        # Execute command
        if command_name is not None and command_name.lower().startswith( "error" ):
            cmd_result = f"Command \"{command_name}\" threw the following error: " + arguments
        elif command_name == "human_feedback":
            cmd_result = f"Human feedback: {user_input}"
        else:
            cmd_result = f"Command \"{command_name}\" returned: {cmd.execute_command(command_name, arguments)}"
            if nr_next_actions > 0:
                nr_next_actions -= 1

        long_term_memory.add(f"Assistant Reply: {assistant_reply} \n" \
                             f"Command Result: {cmd_result} \n" \
                             f"Human Feedback: {user_input} ")

        # Check if there's a result from the command append it to the message history
        if cmd_result is not None:
            full_message_history.append(chat.create_chat_message("system", cmd_result))
            logger.typewriter_log("SYSTEM: ", Fore.YELLOW, cmd_result)
        else:
            full_message_history.append(
                chat.create_chat_message(
                    "system", "Unable to execute command"))
            logger.typewriter_log("SYSTEM: ", Fore.YELLOW, "Unable to execute command")

    chat.close()


if __name__ == '__main__':
    main()
