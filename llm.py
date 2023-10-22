"""Interface to the large language model (LLM).

It currently uses OpenAI. The intention of this module is to abstract away the LLM so that it can be easily replaced
with a different LLM later if needed.
"""
from dataclasses import dataclass
import os
from typing import Optional
import dotenv
from openai import OpenAI

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


def _openai_chat_completion(model: str, system_prompt: str, user_input: str) -> LLMResponse:
    """Get a completion from OpenAI."""
    completion = CLIENT.chat.completions.create(
        model=model,
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


def chat_completion(model, prompt: str, user_input: str) -> LLMResponse:
    """Get a completion from the LLM."""
    # Only one LLM is currently supported. This function can be extended to support multiple LLMs later.
    return _openai_chat_completion(model, prompt, user_input)
