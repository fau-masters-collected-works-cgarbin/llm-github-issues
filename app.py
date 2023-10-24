"""Streamlit app to show the summarized GitHub issue and comments from the LLM response.

Set up the environment as described in the README.md file, then run this app with:

    streamlit run app.py
"""
import configparser
import streamlit as st
import github as gh
import llm


def get_default_settings():
    """Reads settings from the .ini file."""
    config = configparser.ConfigParser()
    config.read("llm.ini")
    model = config["LLM"]["model"]
    prompt = config["LLM"]["prompt"]
    return prompt, model


def display_settings_section():
    """Let the user change the settings that affect the LLM response."""
    st.subheader("Settings")
    if "prompt" not in st.session_state:
        st.session_state.prompt, st.session_state.model = get_default_settings()

    st.session_state.prompt = st.text_area("Prompt", st.session_state.prompt)
    models = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4"]
    st.session_state.model = st.selectbox("Select Model", models, index=models.index(st.session_state.model))


def get_issue_to_show():
    """Get a GitHub issue to show from the user."""
    if "issue_url" not in st.session_state:
        st.session_state.issue_url = ""
    st.subheader("Enter URL to GitHub Issue")
    st.session_state.issue_url = st.text_input("Enter URL", value=st.session_state.issue_url)


def get_github_data(issue_url: str) -> (dict, dict):
    """Get the issue and comments from GitHub."""
    issue = gh.get_issue(issue_url)
    comments = gh.get_issue_comments(issue)
    return issue, comments


def get_llm_response(model: str, prompt: str, issue: dict, comments: dict) -> llm.LLMResponse:
    """Get the LLM response for the issue and comments."""
    with st.spinner(f"Waiting for {model} response..."):
        # Format the issue and comments into a text format to make it easier for the LLM to understand
        # and to save tokens.
        text_format = f"{gh.parse_issue(issue)}\n\n{gh.parse_comments(comments)}"

        response = llm.chat_completion(model, prompt, text_format)
        return response


def main():
    """Run the Streamlit app."""
    st.set_page_config(layout="wide")
    st.title("LLM GitHub Issue Summarizer")

    display_settings_section()
    get_issue_to_show()
    if st.button("Fetch"):
        try:
            issue, comments = get_github_data(st.session_state.issue_url)
            response = get_llm_response(st.session_state.model, st.session_state.prompt, issue, comments)
            st.subheader("GitHub Issue")
            st.json(issue, expanded=False)
            st.subheader("GitHub Comments")
            st.json(comments, expanded=False)
            st.subheader("LLM Response")
            st.write(response.llm_response)
        except Exception as err:
            st.error(err)


if __name__ == "__main__":
    main()
