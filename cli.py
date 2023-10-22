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


def get_llm_answer(prompt, parsed_issue, parsed_comments):
    """Get the LLM answer."""
    user_input = f"{parsed_issue}\n{parsed_comments}"
    response = llm.chat_completion(prompt, user_input)
    return response.llm_response


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
            print("No GitHub issue data available")
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
            # Read the prompt from the file every time we run the test to allow faster prompt testing
            with open("llm_prompt.txt", "r", encoding="UTF-8") as file:
                prompt = file.read()

            print("Getting response from LLM (may take a few seconds)...")
            response = get_llm_answer(prompt, parsed_issue, parsed_comments)
            print(f"LLM Response:\n{response}")
        elif choice == "9":
            print("Exiting...")
            break
        else:
            input("Invalid choice. Press Enter to continue...")


if __name__ == "__main__":
    main()
