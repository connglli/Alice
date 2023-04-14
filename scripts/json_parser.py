from __future__ import annotations

import json
from typing import Any, Dict

from call_ai_function import call_ai_function
from config import Config
from json_utils import correct_json
from logger import logger

cfg = Config()

JSON_SCHEMA = """
{
    "command": {
        "name": "command name",
        "args": {
            "arg name": "value"
        }
    },
    "thoughts": {
        "text": "thought",
        "reasoning": "reasoning",
        "plan": "- short bulleted\n- list that conveys\n- long-term plan",
        "criticism": "constructive self-criticism",
        "speak": "thoughts summary to say to user"
    }
}
"""


def fix_and_parse_json(json_str: str, try_to_fix_with_ai: bool = True):
    json_str = json_str.strip()
    try:
        json_obj = attempt_to_fix_and_parse_json(json_str)
    except json.JSONDecodeError:
        logger.error("Error: Invalid JSON in assistant thoughts\n", json_str)
        json_str = attempt_to_fix_json_str_by_finding_outermost_brackets(json_str)
        json_obj = attempt_to_fix_and_parse_json(json_str)

    # Check if json_obj is a string and attempt to parse it into a JSON object
    if isinstance(json_obj, str):
        try:
            json_obj = json.loads(json_obj)
        except json.JSONDecodeError:
            logger.error("Error: Invalid JSON\n", json_obj)
            json_obj = attempt_to_fix_json_str_by_finding_outermost_brackets(json_obj)
            json_obj = attempt_to_fix_and_parse_json(json_str)

    return json_obj


def attempt_to_fix_and_parse_json(
    json_str: str,
    try_to_fix_with_ai: bool = True
) -> str | Dict[Any, Any]:
    """Fix and parse JSON string"""
    try:
        json_str = json_str.replace('\t', '')
        return json.loads(json_str)
    except json.JSONDecodeError as _:  # noqa: F841
        try:
            json_str = correct_json(json_str)
            return json.loads(json_str)
        except json.JSONDecodeError as _:  # noqa: F841
            pass
    # Let's do something manually:
    # sometimes GPT responds with something BEFORE the braces:
    # "I'm sorry, I don't understand. Please try again."
    # {"text": "I'm sorry, I don't understand. Please try again.",
    #  "confidence": 0.0}
    # So let's try to find the first brace and then parse the rest
    #  of the string
    try:
        brace_index = json_str.index("{")
        json_str = json_str[brace_index:]
        last_brace_index = json_str.rindex("}")
        json_str = json_str[:last_brace_index+1]
        return json.loads(json_str)
    # Can throw a ValueError if there is no "{" or "}" in the json_str
    except (json.JSONDecodeError, ValueError) as e:  # noqa: F841
        if try_to_fix_with_ai:
            logger.warn("Warning: Failed to parse AI output, attempting to fix.\n"
                        "If you see this warning frequently, it's likely that "
                        "your prompt is confusing the AI. Try changing it up slightly.")
            # Now try to fix this up using the ai_functions
            ai_fixed_json = fix_json_with_ai(json_str, JSON_SCHEMA)

            if ai_fixed_json is not None:
                return json.loads(ai_fixed_json)
            else:
                # This allows the AI to react to the error message,
                # which usually results in it correcting its ways.
                logger.error("Failed to fix AI output, telling the AI.")
                return json_str
        else:
            raise e


def attempt_to_fix_json_str_by_finding_outermost_brackets(json_str):
    logger.debug("Attempting to fix JSON by finding outermost brackets")

    try:
        # Use regex to search for JSON objects
        import regex

        json_pattern = regex.compile(r"\{(?:[^{}]|(?R))*\}")
        json_match = json_pattern.search(json_str)

        if json_match:
            # Extract the valid JSON object from the string
            json_str = json_match.group(0)
            logger.debug("Apparently json was fixed.")
        else:
            raise ValueError("No valid JSON object found")

    except (json.JSONDecodeError, ValueError):
        logger.error("Error: Invalid JSON, setting it to empty JSON now.")
        json_str = {}

    return json_str


def fix_json_with_ai(json_str: str, schema: str) -> str:
    """Fix the given JSON string to make it parsable and fully compliant with the provided schema."""
    # Try to fix the JSON using GPT:
    function_string = "def fix_json(json_str: str, schema:str=None) -> str:"
    args = [f"'''{json_str}'''", f"'''{schema}'''"]
    description_string = "Fixes the provided JSON string to make it parsable"\
        " and fully compliant with the provided schema.\n If an object or"\
        " field specified in the schema isn't contained within the correct"\
        " JSON, it is omitted.\n This function is brilliant at guessing"\
        " when the format is incorrect."

    # If it doesn't already start with a "`", add one:
    if not json_str.startswith("`"):
        json_str = "```json\n" + json_str + "\n```"
    result_string = call_ai_function(
        function_string, args, description_string
    )

    logger.debug("------------ JSON FIX AI ATTEMPT ---------------")
    logger.debug(f"Original JSON: {json_str}")
    logger.debug("------------------------------------------------")
    logger.debug(f"Fixed JSON: {result_string}")
    logger.debug("----------- END OF FIX AI ATTEMPT --------------")

    try:
        json.loads(result_string)  # just check the validity
        return result_string
    except:  # noqa: E722
        return None
