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
    config = toml.load("config.toml")
    token = config["app"]["github_token"]
    fetcher = GithubRepoFetcher(token=token)

    meili_client.create_index_repositories()

    # 每次拉取上限为 1000 条, 分批多次拉取
    stars_range = []

    for i in range(1000, 5000, 20):
        stars_range.append(f"{i}..{i + 20}")

    for i in range(5000, 10000, 200):
        stars_range.append(f"{i}..{i + 200}")

    for i in range(10000, 50000, 2000):
        stars_range.append(f"{i}..{i + 2000}")

    stars_range.append(">50000")

    queries = []
    for stars in stars_range:
        query = f"stars:{stars} pushed:>2025-01-01 archived:false"
        queries.append(query)

    # 并发执行
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetcher.fetch_repos, query) for query in queries]
        for future in futures:
            future.result()


if __name__ == "__main__":
    main()
