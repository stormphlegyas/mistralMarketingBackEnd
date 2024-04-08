import requests
import sys
import json

def search_github_repos(query):
    url = f"https://api.github.com/search/repositories?q={query}"
    response = requests.get(url)
    data = response.json()

    repos = [{'name': item['name'], 'url': item['html_url'], 'description': item['description'], 'ssh_url': item['ssh_url'] } for item in data['items']]
    return repos


#if __name__ == "__main__":
#    results = search_github_repos(sys.argv[1])
#    for repo in results:
#        print(f"Name: {repo['name']},\nURL: {repo['url']},\nDescription: {repo['description']},\nSSH URL: {repo['ssh_url']}")

# usage : search_github_repos("NFT app")