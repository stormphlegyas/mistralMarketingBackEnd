import requests
import sys
import json

def search_github_repos(query):
    """
    Search GitHub repositories based on a query.

    Parameters
    ----------
    query : str
        The search query to be used for searching repositories on GitHub.

    Returns
    -------
    list of dict
        A list of dictionaries containing information about GitHub repositories
        matching the given query. Each dictionary contains the following keys:
        - 'name': str
            The name of the repository.
        - 'url': str
            The URL of the repository on GitHub.
        - 'description': str
            A brief description of the repository.
        - 'ssh_url': str
            The SSH URL of the repository.

    Raises
    ------
    requests.exceptions.RequestException
        If there was an error while making the HTTP request to the GitHub API.

    Examples
    --------
    >>> search_github_repos('python')
    [{'name': 'requests', 'url': 'https://github.com/psf/requests', 'description': 'Python HTTP Requests for Humans™', 'ssh_url': 'git@github.com:psf/requests.git'}, ...]
    """
    url = f"https://api.github.com/search/repositories?q={query}"
    response = requests.get(url)
    data = response.json()

    print(data)

    repos = [{'name': item['name'], 'url': item['html_url'], 'description': item['description'], 'ssh_url': item['ssh_url'] } for item in data['items']]
    return repos



    


#if __name__ == "__main__":
#    results = search_github_repos(sys.argv[1])
#    for repo in results:
#        print(f"Name: {repo['name']},\nURL: {repo['url']},\nDescription: {repo['description']},\nSSH URL: {repo['ssh_url']}")

# usage : search_github_repos("NFT app")