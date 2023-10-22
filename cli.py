#! python
"""A simple command-line interface for running tests.

Some test data to use:
     - https://github.com/openai/openai-python
     - 650

     - https://github.com/scikit-learn/scikit-learn
     - 27435

    This one doesn't fit in the standard GPT-3.5 context window - good test for the 16k token version:
     - https://github.com/scikit-learn/scikit-learn
     - 26817
"""
import configparser
import github
import llm


def get_option():
    """Show the menu and ask for an option."""
    print("\nMENU:")
    print("1. Enter the repository and issue number")
    print("2. Get the GitHub issue data")
    print("3. Show the raw GitHub issue data")
    print("4. Show the parsed GitHub issue data")
    print("5. Get and show the LLM response")
    print("9. Exit")
    choice = input("Enter your choice: ")
    return choice


def get_github_data(repository, issue_number):
    """Get the issue and comments from GitHub."""
    issue, error = github.get_issue(repository, issue_number)
    if error:
        print(error)
        return None, None

    comments, error = github.get_issue_comments(issue)
    if error:
        print(error)
        return None, None

    return issue, comments


def get_llm_answer(parsed_issue, parsed_comments):
    """Get the LLM answer."""
    # Always read the config file to allow for changes without restarting the CLI
    model, prompt = get_model_and_prompt()
    user_input = f"{parsed_issue}\n{parsed_comments}"
    try:
        response = llm.chat_completion(model, prompt, user_input)
        return response.llm_response
    except Exception as err:
        return err


def get_model_and_prompt():
    """Get the model and prompt from the config file."""
    # Always read the config file to allow for changes without restarting the CLI
    config = configparser.ConfigParser()
    config.read("llm.ini")
    model = config["LLM"]["model"]
    prompt = config["LLM"]["prompt"]
    return model, prompt


def main():
    """Run the CLI."""
    llm.initialize()

    repository = ""
    issue_number = 0
    issue, comments, parsed_issue, parsed_comments = None, None, None, None

    while True:
        choice = get_option()
        if choice == "1":
            repository = input("Enter GitHub repository name: ")
            issue_number = input("Enter issue number: ")
            issue, comments = None, None  # Reset to not use old data
            continue
        if choice == "2":
            if not repository or not issue_number:
                print("Enter the repository and issue number first")
                continue
            print("Getting issue data from GitHub...")
            issue, comments = get_github_data(repository, issue_number)
            if not issue or not comments:
                continue

            parsed_issue = github.parse_issue(issue)
            parsed_comments = github.parse_comments(comments)
            print("Done")
            continue

        # Don't run options that require GitHub data if we don't have it
        if choice in ("3", "4", "5") and (not issue or not comments):
            print("Retrieve the GitHub issue data first")
            continue

        if choice == "3":
            print("Raw GitHub issue data:")
            print(f"Issue from GitHub:\n{issue}")
            print("\n-------------------------------")
            print(f"Comments from GitHub:\n{comments}")
        elif choice == "4":
            print("Parsed GitHub issue data:")
            print(f"Issue:\n{parsed_issue}")
            print("\n-------------------------------")
            print(f"Comments:\n{parsed_comments}")
        elif choice == "5":
            print("Getting response from LLM (may take a few seconds)...")
            response = get_llm_answer(parsed_issue, parsed_comments)
            print(f"LLM Response:\n{response}")
        elif choice == "9":
            print("Exiting...")
            break
        else:
            input("Invalid choice. Press Enter to continue...")


if __name__ == "__main__":
    main()
