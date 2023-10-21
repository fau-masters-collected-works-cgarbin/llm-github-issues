#! python
"""A simple command-line interface for running tests.

Some test data to use:
     - Repository: https://github.com/openai/openai-python
     - Issue number: 650
"""
import github
import llm


def get_option():
    """Show the menu and ask for an option."""
    print("\nMENU:")
    print("1. Enter values to test")
    print("2. Run test")
    print("3. Show raw GitHub issue data")
    print("4. Show parsed GitHub issue data")
    print("5. Show LLM response")
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

    # Read the prompt from the file
    with open("llm_prompt.txt", "r", encoding="UTF-8") as file:
        prompt = file.read()

    repository = ''
    issue_number = 0
    issue, comments, parsed_issue, parsed_comments, response = None, None, None, None, None

    while True:
        choice = get_option()
        if choice == "1":
            repository = input("Enter GitHub repository name: ")
            issue_number = input("Enter issue number: ")
        elif choice == "2":
            print("Getting issue data from GitHub...")
            issue, comments = get_github_data(repository, issue_number)
            if not issue or not comments:
                continue

            parsed_issue = github.parse_issue(issue)
            parsed_comments = github.parse_comments(comments)
            print("Getting response from LLM (may take a few seconds)...")
            response = get_llm_answer(prompt, parsed_issue, parsed_comments)
            print("Done")
        elif choice == "3":
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
            print(f"LLM Response:\n{response}")
        elif choice == "9":
            print("Exiting...")
            break
        else:
            input("Invalid choice. Press Enter to continue...")


if __name__ == "__main__":
    main()
