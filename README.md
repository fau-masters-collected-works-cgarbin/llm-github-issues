# Using LLMs to review GitHub issues

This project is a learning exercise on using large language models (LLMs) to summarize coding-related discussions. It uses GitHub issues as the source of data. The goal is to allow developers to understand what is being reported and discussed in the issues without having to read each message in the thread.

## Quick getting started

If you haven't done so yet, [prepare the environment](#preparing-the-environment).

Run the following commands to activate the environment and start the application in a browser.

```bash
source venv/bin/activate
streamlit run app.py
```

## Design

This section describes the project design. It is not necessary to read it to use the project.

There are three main steps:

1. [Fetching data](#fetching-data): Fetch the comments posted in the GitHub issue. This will return large JSON objects.
1. [Preprocessing data](#preprocessing-data): Convert the JSON objects into a format that the LLM can use. The goal here is to reduce the amount of data to process and to remove irrelevant information. Concise data helps the LLM focus on important information and reduces costs using fewer tokens.
1. [Extracting information with an LLM](#extracting-information-with-a-llm): Use the LLM to extract the information from the preprocessed data.

### Fetching data

### Preprocessing data

### Extracting information with a LLM

## Preparing the environment

This is a one-time step. If you have already done this, just activate the virtual environment with `source venv/bin/activate`.

There are two steps to prepare the environment.

1. [OpenAI API key](#openai-api-key)
1. [Python environment](#python-environment)

### OpenAI API key

You need an OpenAI API key to use this project. If you already have an OpenAI account, create an API key [here](https://platform.openai.com/account/api-keys). If you don't have an account, create one [here](https://openai.com/product#made-for-developers).

OpenAI charges for API access ([pricing](https://openai.com/pricing)). The GPT 3.5 models are affordable for small projects, but be careful with GPT-4 models. To avoid surprise bills, you can set [spending limits](https://platform.openai.com/docs/guides/production-best-practices/managing-billing-limits). New OpenAI accounts get a $5 credit, enough for about two to three million tokens with GPT-3.5 models (as of [October 2023](https://openai.com/pricing)).

Once you have the OpenAI API key, create a `.env` file in the project root directory with the following content.

```bash
OPENAI_API_KEY=<your key>
```

It is safe to add the key here. It will never be committed to the repository.

### Python environment

Run the following commands to create a virtual environment and install the required packages.

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install the new OpenAI Python package manually until it is released
# See comments in requirements.txt for more information
pip install --pre openai
```
