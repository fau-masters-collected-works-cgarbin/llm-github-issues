"""Interface to the large language model (LLM).

It currently uses OpenAI. The intention of this module is to abstract away the LLM so that it can be easily replaced
with a different LLM later if needed.
"""
from dataclasses import dataclass
import os
from typing import Optional
import dotenv
from openai import OpenAI

MODEL = "gpt-3.5-turbo"

SYSTEM_PROMPT = "You are an experience developer familiar with GitHub issues." + \
                "The following text has been parsed from a GitHub issue." + \
                "Answer the request using the information provided.\n" + \
                "Extract the following information from the issue and comments:\n" +\
                " - A brief summary of the issue in exactly one short sentence of no more 50 words.\n" + \
                " - A more extended summary of the issue." + \
                "   If code has been provided, list to the relevant pieces of code in the summary.\n" + \
                " - A summary of each comment in chronological order as a markdown table with the columns date," + \
                "   author, summary"


CLIENT = None


@dataclass
class LLMResponse:
    """Class to hold the LLM response.

    We use a class instead of returning the native LLM response to make it easier to adapt to different LLMs later.
    """
    system_prompt: Optional[str] = None
    user_input: Optional[str] = None
    llm_response: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


def initialize() -> None:
    """Initialize the LLM.

    This must be called before any other functions in this module.
    """
    dotenv.load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set -- see README.md for instructions")

    global CLIENT
    CLIENT = OpenAI(api_key=api_key)


def _openai_chat_completion(system_prompt: str, user_input: str) -> LLMResponse:
    """Get a completion from OpenAI."""
    completion = CLIENT.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        temperature=0.0  # We want precise and repeatable results
    )
    answer = LLMResponse()
    answer.system_prompt = system_prompt
    answer.user_input = user_input
    answer.llm_response = completion.choices[0].message.content

    return answer


def chat_completion(system_prompt: str, user_input: str) -> LLMResponse:
    """Get a completion from the LLM."""
    # Only one LLM is currently supported. This function can be extended to support multiple LLMs later.
    return _openai_chat_completion(system_prompt, user_input)
