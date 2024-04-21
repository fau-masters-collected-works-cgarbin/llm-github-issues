"""Interface to the large language model (LLM).

It currently uses OpenAI. The intention of this module is to abstract away the LLM so that it can be easily replaced
with a different LLM later if needed.
"""

import os
import time
from dataclasses import dataclass, field

import dotenv
from openai import OpenAI


@dataclass
class LLMResponse:
    """Class to hold the LLM response.

    We use our class instead of returning the native LLM response to make it easier to adapt to different LLMs later.
    """

    model: str = ""
    prompt: str = ""
    user_input: str = ""
    llm_response: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    raw_response: dict = field(default_factory=dict)
    elapsed_time: float = 0.0

    @property
    def total_tokens(self):
        """Calculate the total number of tokens used."""
        return self.input_tokens + self.output_tokens


# Supported models and costs
# Price per 1,000,000 tokens for each model (from https://openai.com/pricing)
_COST_UNIT = 1_000_000  # 1 million tokens
_MODEL_DATA = {
    "gpt-3.5-turbo-0125": {"input": 0.5, "output": 1.5},
    "gpt-4-turbo-2024-04-09": {"input": 10.0, "output": 30.0},
}


def _get_openai_client() -> OpenAI:
    """Get a client for OpenAI."""
    # Always override the environment variables with the .env file to allow key changes without restarting the program
    dotenv.load_dotenv(override=True)
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set -- see README.md for instructions")

    return OpenAI(api_key=api_key)


def _openai_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """Calculate the cost of the completion.

    IMPORTANT: OpenAI may change pricing at any time. Consult https://openai.com/pricing and
    update this function accordingly.
    """
    if model not in _MODEL_DATA:
        # Flag the error, but don't interrupt the program
        return -1.0

    input_cost = input_tokens * _MODEL_DATA[model]["input"] / _COST_UNIT
    output_cost = output_tokens * _MODEL_DATA[model]["output"] / _COST_UNIT
    return input_cost + output_cost


def _openai_chat_completion(model: str, prompt: str, user_input: str) -> LLMResponse:
    """Get a chat completion from OpenAI."""
    # Always instantiate a new client to pick up configuration changes without restarting the program
    client = _get_openai_client()

    start_time = time.time()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input},
        ],
        temperature=0.0,  # We want precise and repeatable results
    )
    elapsed_time = time.time() - start_time
    client.close()

    # Record the request and the response
    response = LLMResponse()
    response.elapsed_time = elapsed_time
    response.model = model
    response.prompt = prompt
    response.user_input = user_input
    response.llm_response = completion.choices[0].message.content  # type: ignore

    # This is not exactly the raw response, but it's close enough
    # It assumes the completion object is a pydantic.BaseModel class, which has the `dict()`
    # method we need here
    response.raw_response = completion.model_dump()

    # Record the number of tokens used for input and output
    response.input_tokens = completion.usage.prompt_tokens  # type: ignore
    response.output_tokens = completion.usage.completion_tokens  # type: ignore

    # Records costs (depends on the tokens and model - set them first)
    response.cost = _openai_cost(response.input_tokens, response.output_tokens, model)

    return response


def models():
    """Get the list of supported models."""
    # Return the keys in the token_costs dictionary
    return list(_MODEL_DATA.keys())


def chat_completion(model, prompt: str, user_input: str) -> LLMResponse:
    """Get a completion from the LLM."""
    # Only one LLM is currently supported. This function can be extended to support multiple LLMs later.
    if model.startswith("gpt"):
        return _openai_chat_completion(model, prompt, user_input)
    raise ValueError(f"Unsupported model: {model}")
