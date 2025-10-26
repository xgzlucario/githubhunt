from concurrent.futures import ThreadPoolExecutor

import toml
from github import Auth, Github

from db import meili_client


class GithubRepoFetcher:
    def __init__(self, token: str):   
        self.github_client = Github(auth=Auth.Token(token), per_page=100)
        self.meili_client = meili_client
    

    def fetch_repos(self, query: str):
        repos = list(self.github_client.search_repositories(query))
        print(f"Query: {query}")
        print(f"Found {len(repos)} repositories")
        
        try:
            self.meili_client.save_repositories(repos)
        except Exception as e:
            print(f"Failed to save batch repos: {e}")


def main():
    config = toml.load('config.toml')
    token = config['app']['github_token']
    fetcher = GithubRepoFetcher(token=token)

    meili_client.create_index_repositories()

    # github search_repositories 每次拉取上限为 1000 条, 分批多次拉取
    stars_range = [
        "1000..1500",
        "1500..2000",
        "2000..3000",
        "3000..4000",
        "4000..6000",
        "6000..10000",
        ">10000"
    ]

    # 添加你想要拉取的语言
    languages = [
        "Go",
        "Java",
        "Python",
        "Rust",
        "JavaScript",
        "TypeScript",
    ]

    queries = []
    for stars in stars_range:
        for language in languages:
            query = f"stars:{stars} pushed:>2025-01-01 language:{language} archived:false"
            queries.append(query)

    # 并发执行
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetcher.fetch_repos, query) for query in queries]
        for future in futures:
            future.result()


if __name__ == "__main__":
    main()