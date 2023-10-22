"""Interface to GitHub."""
import requests


def _get_github_api_url(repo: str) -> str:
    """Get GitHub API URL for a repository, accepting a flexible range of inputs.

    Args:
        repo (str): Repository in the form "user/repo" or full repository URL.

    Returns:
        str: GitHub issues API URL for the repository.
    """
    if repo.startswith("https://api.github.com/repos/"):
        # Assume it's already a GitHub API URL
        if repo.endswith("/"):
            repo = repo[:-1]
        return repo

    # Assume it's a GitHub repository URL and accept a flexible range of inputs
    # Normalize the URL
    if repo.startswith("https://github.com/"):
        repo = repo.replace("https://github.com/", "")
    if repo.endswith(".git"):
        repo = repo[:-4]
    if repo.endswith("/"):
        repo = repo[:-1]

    # Create the GitHub API URL from the normalized URL
    if "/" in repo:
        return f"https://api.github.com/repos/{repo}"

    raise ValueError("Invalid repository format. Must be in the form 'user/repo' or full repository URL.")


def _invoke_github_api(repo: str, endpoint: str) -> (dict, str):
    """Invoke the GitHub API for a repository.

    Args:
        repo (str): Repository in the form "user/repo" or "https://..."
        endpoint (str): API endpoint and its parameters, e.g. "issues?state=open&sort=created&direction=desc".
    """
    url = _get_github_api_url(repo)
    if endpoint:
        url = f"{url}/{endpoint}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.HTTPError as errh:
        return None, f"HTTP Error: {errh}"
    except requests.exceptions.ConnectionError as errc:
        return None, f"Connection Error: {errc}"
    except requests.exceptions.Timeout as errt:
        return None, f"Timeout Error: {errt}"
    except requests.exceptions.RequestException as err:
        return None, f"Something went wrong: {err}"


def get_issue(repo: str, issue_id: str) -> (dict, str):
    """Get a specific issue from GitHub.

    Args:
        repo (str): Repository in the form "user/repo" or "https://github.com/...".
        issue_id (int): Issue number.

    Returns:
        dict: Issue data.
        str: Error message, if any.
    """
    return _invoke_github_api(repo, f"issues/{issue_id}")


def get_issue_comments(issue: dict) -> (dict, str):
    """Get comments for a specific issue.

    Args:
        issue (dict): Issue data, as returned by GitHub (the JSON response).

    Returns:
        dict: Comments data.
        str: Error message, if any.
    """
    return _invoke_github_api(issue["comments_url"], "")


def parse_issue(issue: dict) -> str:
    """Parse issue data returned by GitHub into a text format.

    The goal is to translate the JSON into a text format that has only the information we need to pass to an LLM. The
    shorter format helps the LLM understand the data better and saves tokens (and thus cost).

    The text includes some annotations to help guide the LLM. For example, using delimiters to indicate the start and
    end of the body text, and using a prefix to indicate the start of each field. This is based on previous experiments
    with LLMs. It may need to be adjusted for different LLMs. Other LLMs may not need as much guidance.

    Args:
        issue (dict): Issue data, as returned by GitHub (the JSON response).

    Returns:
        str: Parsed issue data.
    """
    parsed = f"Title: {issue['title']}\n"
    parsed += f"Body (between '''):\n'''\n{issue['body']}\n'''\n"
    parsed += f"Submitted by: {issue['user']['login']}\n"
    parsed += f"Submitted on: {issue['created_at']}\n"
    parsed += f"Submitter association: {issue['author_association']}\n"
    parsed += f"State: {issue['state']}\n"
    parsed += f"Labels: {', '.join([label['name'] for label in issue['labels']])}\n"
    return parsed


def parse_comments(comments: dict) -> str:
    """Parse comments data returned by GitHub into a text format.

    See comments for parse_issue() for more details.

    Args:
        comments (dict): Comments data, as returned by GitHub (the JSON response).

    Returns:
        str: Parsed comments data.
    """
    parsed = ""
    for comment in comments:
        parsed += f"Comment by: {comment['user']['login']}\n"
        parsed += f"Comment on: {comment['created_at']}\n"
        parsed += f"Body (between '''):\n'''\n{comment['body']}\n'''\n"
    return parsed
