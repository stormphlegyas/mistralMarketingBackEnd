import requests
import sys
import json

def search_github_repos(query):
    url = f"https://api.github.com/search/repositories?q={query}"
    response = requests.get(url)
    data = response.json()

    repos = [{'name': item['name'], 'url': item['html_url']} for item in data['items']]
    return repos
