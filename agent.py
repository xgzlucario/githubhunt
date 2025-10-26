import pandas as pd
import toml
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from github import Auth, Github, Repository

from db import meili_client

config = toml.load("config.toml")
github_token = config["app"]["github_token"]

github_cli = Github(auth=Auth.Token(github_token), per_page=100)


def repo_to_dict(repo: Repository) -> dict:
    return {
        'id': repo.id,
        'full_name': repo.full_name,
        'description': repo.description,
        'language': repo.language,
        'stars': repo.stargazers_count,
        'created_at': repo.created_at.date().isoformat(),
        'pushed_at': repo.pushed_at.date().isoformat(),
        'topics': repo.topics
    }


def get_user_starred(username: str) -> list[dict]:
    """
    Get Github user's starred list.

    Args:
        username (str): The username of the user.

    Returns:
        list[dict]: The list of starred repositories.
    """
    user = github_cli.get_user(username)
    results = [repo_to_dict(repo) for repo in user.get_starred()]
    return results


def api_search(query: str, languages: list[str], limit: int = 10) -> list[dict]:
    g = Github(per_page=limit)     
    query = f"{query} in:name,description,topics"

    if len(languages) > 0:
        language_query = " ".join([f"language:{language}" for language in languages])
        query += f" {language_query}"
        
    repos = list(g.search_repositories(query, sort='stars', order='desc'))
    
    results = []
    for repo in repos:
        repo_info = repo_to_dict(repo)
        repo_info['_rankingScore'] = 0.5
        results.append(repo_info)
        
    return results[:limit]


def search_repositories(query: str, languages: list[str], top_k: int = 20) -> list[dict]:
    """
    Search Github repositories by repository name, description, topics and languages.

    Args:
        query (str): The query to search for repositories.
        languages (list[str]): The languages to filter the repositories by.
        top_k (int): The number of repositories to return, default is 20.

    Returns:
        list[dict]: The list of repositories.
    """
       
    db_results = meili_client.search_repositories(query=query, languages=languages, top_k=int(top_k * 0.7))
    api_results = api_search(query=query, languages=languages, limit=int(top_k * 0.3))

    df = pd.DataFrame(db_results + api_results)
    if df.empty:
        return []
    
    df = (df.sort_values(by='_rankingScore', ascending=False)
          .drop_duplicates(subset='id')
          .head(top_k))
    
    df = df[['full_name', 'description', 'language', 'topics', 'stars', 'created_at']]
 
    return df.to_dict(orient='records')


def get_repo_readme(full_name: str) -> str:
    """
    Get Github repository README content.

    Args:
        full_name (str): The full name of the repository.

    Returns:
        str: The README content in markdown format.
    """

    repo = github_cli.get_repo(full_name)
    if not repo:
        return "Error: Repository not found"

    readme = repo.get_readme()
    if readme:
        content = readme.decoded_content.decode('utf-8')
        return content
    else:
        return "Error: README not found"


SYSTEM_PROMPT = """
你是一个 GitHub 仓库搜索助手, 你能够理解用户意图, 合理规划并使用多种工具, 帮助用户找到具有高度相关性的仓库, 并最终输出报告
请严格遵守以下规则:
1. 搜索工具可能返回低相关结果，你需重试并筛选, 请通过调整参数等方式重新尝试, 至少找到 5 个高度相关的结果, 最多可尝试 10 次
2. 调用工具时不限制编程语言, 除非用户指定
3. 调用过程中不限制使用中文或者英文, 但最终报告必须使用中文并且以 Markdown 格式输出
"""

api_key = config["app"]["deepseek_api_key"]

agent = Agent(
    name="Github Agent",
    instructions=SYSTEM_PROMPT,
    model=DeepSeek(id="deepseek-chat", api_key=api_key),
    tools=[search_repositories, get_repo_readme, get_user_starred],
    markdown=True,
)

if __name__ == "__main__":
    agent.print_response("查找 golang 实现的 redis 服务器, 基于 AELoop", stream=True, stream_events=True)