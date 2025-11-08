from datetime import datetime, timezone

import meilisearch
import toml
from github import Repository


class MeiliClient:
    INDEX_REPOSITORIES = 'repositories'
    
    def __init__(self, host, port, master_key):
        self._init_clients(host, port, master_key)

    def _init_clients(self, host, port, master_key):
        self.client = meilisearch.Client(f'http://{host}:{port}', master_key)
    
    def create_index_repositories(self):
        index = self.client.index(self.INDEX_REPOSITORIES)
        index.update_searchable_attributes([ # 按重要性排序
            'full_name',
            'description',
            'topics',
            'language'
        ])
        index.update_filterable_attributes([
            'id',
            'language',
            'stars',
            'archived',
            'created_at',
            'pushed_at'
        ])
        index.update_sortable_attributes([
            'stars',
            'stars_per_day'
        ])
        

    def save_repositories(self, repos: list[Repository]):
        index = self.client.index(self.INDEX_REPOSITORIES)
        today = datetime.now(timezone.utc)
        docs = []
        
        for repo in repos:
            # 低质量仓库过滤
            if repo.description and len(repo.description) > 1024:
                print(f"Low quality repo: {repo.full_name}, description length: {len(repo.description)}")
                continue
            
            docs.append({
                "id": repo.id,
                "full_name": repo.full_name,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "homepage": repo.homepage,
                "language": repo.language,
                "created_at": repo.created_at.date().isoformat(),
                "pushed_at": repo.pushed_at.date().isoformat(),
                "archived": repo.archived,
                "stars_per_day": repo.stargazers_count / ((today - repo.created_at).days + 1),
                "topics": repo.topics,
                "icon": repo.owner.avatar_url,
            })
            
        index.add_documents(docs)


    def search_repositories(
            self,
            query: str,
            languages: list[str] = None,
            top_k: int = 10,
            matching_strategy: str = 'frequency', # frequency | last | all
            ranking_score_threshold: float = 0.2) -> list[dict]:
        
        index = self.client.index(self.INDEX_REPOSITORIES)

        search_params = {
            'limit': top_k,
            'showRankingScore': True,
            'rankingScoreThreshold': ranking_score_threshold, # 召回率阈值
            'matchingStrategy': matching_strategy, # https://www.meilisearch.com/docs/reference/api/search#matching-strategy
            'sort': ['stars_per_day:desc']
        }
        filters = []

        if languages and len(languages) > 0:
            filters.append(f'language IN {languages}')

        if len(filters) > 0:
            search_params['filter'] = ' AND '.join(filters)
            
        results = index.search(query, search_params)
            
        return results['hits']
    
    
# Init clients
config = toml.load("config.toml")
meili_config = config["meili"]


meili_client = MeiliClient(
    host=meili_config["host"],
    port=meili_config["port"],
    master_key=meili_config["master_key"]
)