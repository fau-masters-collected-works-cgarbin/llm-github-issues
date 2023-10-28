"""Streamlit app to show the summarized GitHub issue and comments from the LLM response.

Set up the environment as described in the README.md file, then run this app with:

    streamlit run app.py
"""
import configparser
import re
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
    with st.expander("Click to configure the prompt and the model", expanded=False):
        if "prompt" not in st.session_state:
            st.session_state.prompt, st.session_state.model = get_default_settings()

        st.session_state.prompt = st.text_area("Prompt", st.session_state.prompt, height=250)
        models = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4"]
        st.session_state.model = st.selectbox("Select model", models, index=models.index(st.session_state.model))


def get_issue_to_show():
    """Get a GitHub issue to show from the user."""
    if "issue_url" not in st.session_state:
        st.session_state.issue_url = ""

    example_urls = [
        "https://github.com/openai/openai-python/issues/488 (simple example)",
        "https://github.com/openai/openai-python/issues/650 (also simple, but more code blocks)",
        "https://github.com/scikit-learn/scikit-learn/issues/26817 (large, requires GPT-3.5 16k or GPT-4)",
        "https://github.com/qjebbs/vscode-plantuml/issues/255 (large number of comments)",
    ]
    selected_url = st.selectbox("Choose an example URL from this list or type your own below",
                                example_urls, placeholder="Pick from this list or enter an URL below", index=None)
    if selected_url:
        # Discard the comment text after the URL to make it valid
        st.session_state.issue_url = selected_url.split(" (")[0]

    st.session_state.issue_url = st.text_input("Enter GitHub issue URL", value=st.session_state.issue_url,
                                               label_visibility="collapsed",
                                               placeholder="Enter URL to GitHub issue or pick an example from the list above")


def get_github_data(issue_url: str) -> (dict, dict):
    """Get the issue and comments from GitHub."""
    with st.spinner("Waiting for GitHub response..."):
        issue = gh.get_issue(issue_url)
        comments = gh.get_issue_comments(issue)
        return issue, comments


def get_llm_response(model: str, prompt: str, issue: str, comments: str) -> llm.LLMResponse:
    """Get the LLM response for the issue and comments."""
    with st.spinner(f"Waiting for {model} response..."):
        # Format the issue and comments into a text format to make it easier for the LLM to understand
        # and to save tokens.
        text_format = f"{issue}\n\n{comments}"

        response = llm.chat_completion(model, prompt, text_format)
        return response


def show_github_raw_data(issue: dict, comments: dict):
    """Show the GitHub issue and comments as we got from the API."""
    with st.expander("Click to show/hide raw data from the GitHub API", expanded=False):
        # Show a link to the issue in GitHub
        # Prefer the issue URL from GitHub - fall back to the user's input if we don't have it
        issue_url = issue.get("html_url", st.session_state.issue_url)
        st.link_button("Open the issue in GitHub", issue_url)

        st.write("This is the data as we got from from the GitHub API.")
        st.subheader("GitHub Issue")
        st.json(issue, expanded=False)
        st.subheader("GitHub Comments")
        st.json(comments, expanded=False)


def show_github_post_processed_data(issue: str, comments: str):
    """Show the GitHub issue and comments after we have post-processed them."""
    with st.expander("Click to show/hide the post-processed GitHub data", expanded=False):
        st.write("This is the data after we have post-processed to use with the LLM.")
        st.subheader("GitHub Issue")
        st.text(issue)
        st.subheader("GitHub Comments")
        st.text(comments)


def show_llm_raw_data(response: llm.LLMResponse):
    """Show the raw data to/from the LLM."""
    r = response  # Shorter name to make the code easier to read
    st.write(f"Total tokens: {r.total_tokens:,} (input: {r.input_tokens:,}, output: {r.output_tokens:,})")
    st.write(f"Cost: U${r.cost:.4f}")

    with st.expander("Click to show/hide the raw data we sent to and received from the LLM", expanded=False):
        st.subheader("Raw LLM response")
        st.json(r.raw_response, expanded=False)
        st.subheader("Prompt")
        st.text(r.prompt)
        st.subheader("Data we extracted from the GitHub issue and comments")
        st.text(r.user_input)
        st.subheader("LLM Response")
        st.text(r.llm_response)


def show_llm_response(response: llm.LLMResponse):
    """Show the formatted LLM response."""
    # Change markdown heading 1 to heading 3 to make it smaller
    # Ensure it's a heading by replacing only if it's at the start of the line
    txt = re.sub(r"^# ", r"### ", response.llm_response, flags=re.MULTILINE)

    st.header(f"Summary from {st.session_state.model}")
    st.write(txt)


def main():
    """Run the Streamlit app."""
    st.set_page_config(layout="wide")
    st.title("LLM GitHub Issue Summarizer")

    display_settings_section()
    get_issue_to_show()
    if st.button(f"Generate summary with {st.session_state.model}"):
        try:
            issue, comments = get_github_data(st.session_state.issue_url)
            parsed_issue = gh.parse_issue(issue)
            parsed_comments = gh.parse_comments(comments)
            response = get_llm_response(st.session_state.model, st.session_state.prompt,
                                        parsed_issue, parsed_comments)

            tabs = st.tabs(["LLM data", "Raw GitHub data", "Parsed GitHub data"])
            with tabs[0]:
                show_llm_raw_data(response)
            with tabs[1]:
                show_github_raw_data(issue, comments)
            with tabs[2]:
                show_github_post_processed_data(parsed_issue, parsed_comments)

            show_llm_response(response)
        except Exception as err:
            st.error(err)


if __name__ == "__main__":
    main()
