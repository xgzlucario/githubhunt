# githubhunt

githubhunt 是一个基于 AI Agent 的自然语言 Github 仓库搜索工具, 用户通过使用自然语言描述需求, 例如: "查找 golang 实现的 redis 服务器, 基于 AELoop", AI Agent 会识别用户的意图, 并结合内置的搜索工具, 不断调整输入优化搜索结果, 最终帮助用户实现 Github 仓库的精准搜索.

下面是一个简单的使用示例:

![image](./example/image.png)

![image2](./example/image2.png)

除此以外, Agent 还支持:

- 使用视觉理解模型分析仓库, 例如: "解释 xgzlucario/rotom 的流程图"
- 从用户的 starred 列表中搜索, 例如: "从我的关注列表中查找监控相关的项目, 我是 xgzlucario"
- 总结或解释仓库的功能: 例如: xgalucario/githubhunt 仓库是做什么的?

## 系统依赖

- [MeiliSearch](https://github.com/meilisearch/meilisearch)
- Python 3.13
- DeepSeek API
- Steel Browser(可选, 用于视觉分析)
- QWEN API(可选, 用于视觉分析)

## 项目结构

- `fetch_repos.py`: 拉取 Github 仓库并保存到 MeiliSearch
- `agent.py`: 使用 Agent 进行搜索
- `browser.py`: 调用浏览器截图工具, 用于视觉分析
- `db.py`: MeiliSearch 索引构建定义和 db 操作封装
- `config.toml`: 配置文件

## 使用方法

### 环境配置

在 `config.toml` 中配置 Github Token(必需) 和 DeepSeek API_KEY(必需) 或者其他模型调用配置, 如果需要使用视觉分析工具, 还需要安装 Steel Browser 并配置 QWEN_API_KEY。

### 启动 MeiliSearch

```bash
docker compose up -d
```

### 安装依赖

首先确保安装了 [uv](https://docs.astral.sh/uv/) 工具, 然后执行命令:

```bash
uv sync
```

### 拉取 Github 仓库

第一次运行时需要同步 Github 仓库到 MeiliSearch, 后续可以按需定期同步。

在本地构建索引可以大大提升搜索性能, 原因是本地使用 `frequency` 的[匹配策略](https://www.meilisearch.com/docs/reference/api/search#matching-strategy), 相比 Github API 的 `all` 策略, 每次搜索的召回率更高, 返回的结果数量更多, 更容易命中目标仓库。

```bash
uv run fetch_repos.py
```

### 使用 Agent 进行搜索

```bash
uv run agent.py --query "查找 golang 实现的 redis 服务器, 基于 AELoop"
```

如果需要使用视觉分析工具, 首先需要安装 [Steel Browser](https://github.com/steel-dev/steel-browser), 命令如下:

```bash
sudo docker run --name steel-browser-api -d -p 3000:3000 -p 9223:9223 ghcr.io/steel-dev/steel-browser-api:latest
```

然后使用视觉分析工具:

```bash
uv run agent.py --query "解释 xgzlucario/rotom 的流程图" --visual
```
