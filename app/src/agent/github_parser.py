import requests
from typing import Dict, Any, List

class GitHubParser:
    def __init__(self):
        # Unauthenticated endpoints to avoid needing a token.
        # This provides 60 requests per hour per IP.
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }

    def _fetch_readme_raw(self, owner: str, repo: str, default_branch: str) -> str:
        """
        Fetches README directly from raw.githubusercontent to save API limits.
        """
        urls_to_try = [
            f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/README.md",
            f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/readme.md",
            f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/README.txt"
        ]
        
        for url in urls_to_try:
            resp = requests.get(url)
            if resp.status_code == 200:
                # Return truncated README to save LLM context
                return resp.text[:3000]
        return "No README found."

    def get_top_repositories(self, username: str, limit: int = 5) -> List[Dict[str, Any]]:
        # 1 API request: Fetch repos sorted by stars
        url = f"https://api.github.com/users/{username}/repos?sort=stars&per_page={limit}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            return []

        repos = response.json()
        results = []
        for repo in repos:
            readme_content = self._fetch_readme_raw(
                owner=username, 
                repo=repo['name'], 
                default_branch=repo.get('default_branch', 'main')
            )
            
            results.append({
                "name": repo['name'],
                "html_url": repo['html_url'],
                "description": repo['description'],
                "stars": repo['stargazers_count'],
                "language": repo['language'],
                "readme": readme_content
            })
            
        return results

    def get_open_source_contributions(self, username: str) -> List[Dict[str, Any]]:
        # 1 API request: Search for merged PRs in repos not owned by the user
        url = f"https://api.github.com/search/issues?q=author:{username}+type:pr+is:merged+-user:{username}&per_page=5"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            return []

        items = response.json().get("items", [])
        prs = []
        for item in items:
            prs.append({
                "title": item['title'],
                "url": item['html_url'],
                "repo_url": item['repository_url'].replace("https://api.github.com/repos/", "https://github.com/"),
                "state": item['state']
            })
        return prs

    def extract_all(self, username: str) -> str:
        repos = self.get_top_repositories(username)
        contributions = self.get_open_source_contributions(username)
        
        # Format into a clean string to feed into Jinja2 template
        output = f"GitHub Profile: https://github.com/{username}\n\n"
        
        output += "### Top Repositories:\n"
        if not repos:
            output += "No public repositories found or rate limit exceeded.\n"
        for r in repos:
            output += f"- Name: {r['name']} ({r['stars']} stars, Language: {r['language']})\n"
            output += f"  URL: {r['html_url']}\n"
            output += f"  Description: {r['description']}\n"
            output += f"  README Snippet:\n  {r['readme'][:500]}...\n\n"
            
        output += "### Open Source Contributions (Merged PRs to other repos):\n"
        if not contributions:
            output += "No major open source contributions found.\n"
        for pr in contributions:
            output += f"- {pr['title']}\n  PR URL: {pr['url']}\n  Repo URL: {pr['repo_url']}\n\n"
            
        return output
