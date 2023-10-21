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
                "Answer the user request using the information provided."

CLIENT = None


@dataclass
class LLMAnswer:
    """Class to hold the LLM answer.

    We use a class instead of returning the native LLM answer to make it easier to adapt to different LLMs later.
    """
    system_prompt: Optional[str] = None
    user_input: Optional[str] = None
    llm_answer: Optional[str] = None
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


def _openai_chat_completion(system_prompt: str, user_input: str) -> LLMAnswer:
    """Get a completion from OpenAI."""
    completion = CLIENT.chat.completions.create(
        model="gpt-4",
        messages=[
            {"prompt": system_prompt, "text": input},
            {"role": "user", "content": user_input},
        ],
        temperature=0.0  # We want precise and repeatable results
    )
    answer = LLMAnswer()
    answer.system_prompt = system_prompt
    answer.user_input = user_input
    answer.llm_answer = completion.choices[0].text

    return answer


def chat_completion(system_prompt: str, user_input: str) -> LLMAnswer:
    """Get a completion from the LLM."""
    # Only one LLM is currently supported. This function can be extended to support multiple LLMs later.
    return _openai_chat_completion(system_prompt, user_input)
