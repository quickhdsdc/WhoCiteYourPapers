# WhoCiteYourPapers (引用分析工具)

这是一个生产级的 Python 工具，用于分析谁引用了你的研究论文。它利用 Semantic Scholar API 获取引用数据，分析引用作者的人口统计信息，并利用 Google GenAI (Gemini) 网络搜索功能，为高影响力的引用作者补充详细信息（如当前单位、职称等）。

## 功能特点

-   **获取引用**: 自动从 Semantic Scholar API 获取 `my.bib` 中列出的所有论文的引用数据。
-   **作者分析**: 统计每位引用作者的 H-Index 和总引用数等指标。
-   **高影响力筛选**: 根据引用次数筛选出顶尖的引用作者。
-   **AI 辅助调研**: 使用 Google GenAI (Gemini 2.0 Flash) 和 Google 搜索，查找高影响力作者的最新单位、学术职称和个人主页链接。
-   **综合报告**: 生成最终的 CSV 报告 `output/high_impact_citing_authors.csv`，包含原始引用数据和 AI 调研的详细信息。

##前提条件

-   Python 3.12+
-   [uv](https://github.com/astral-sh/uv) (推荐用于依赖管理)
-   [Semantic Scholar API Key](https://www.semanticscholar.org/product/api)
-   [Google GenAI API Key](https://aistudio.google.com/) (用于网络搜索功能)

## 安装

1.  克隆仓库:
    ```bash
    git clone https://github.com/quickhdsdc/WhoCiteYourPapers.git
    cd WhoCiteYourPapers
    ```

2.  使用 `uv` 同步依赖:
    ```bash
    uv sync
    ```

## 配置

1.  **Semantic Scholar API**:
    在 `config/` 目录下创建一个名为 `semantic_scholar_api_key.txt` 的文件，并将你的 API Key 粘贴进去。

2.  **Google GenAI**:
    复制示例配置文件:
    ```bash
    cp config/config.example.toml config/config.toml
    ```
    编辑 `config/config.toml`，在 `[llm.gemini]` 部分添加你的 Google API Key (或者直接设置 `GOOGLE_API_KEY` 环境变量)。

    ```toml
    [llm.gemini]
    api_key = "YOUR_GOOGLE_API_KEY"
    model = "gemini-2.0-flash-exp"
    ```

3.  **你的论文**:
    将你的 BibTeX 文件命名为 `my.bib` 并放置在项目根目录下。

## 使用方法

本工具提供了一个统一的命令行接口 (CLI) `whocite`。你可以通过 `uv run` 来运行它。

### 快速开始 (运行完整流程)

运行从获取引用到合并调研结果的完整流程:

```bash
uv run whocite run-all --limit-research 30
```

*所有输出文件 (JSON 和 CSV) 都将生成在 `output/` 目录下。*

### 分步执行

你也可以单独运行每个步骤:

1.  **获取引用**: 获取引用数据。
    ```bash
    uv run whocite fetch-citations
    ```

2.  **获取作者详情**: 从 Semantic Scholar 获取作者统计信息。
    ```bash
    uv run whocite fetch-authors
    ```

3.  **分析结果**: 生成 `citations_analysis.csv`。
    ```bash
    uv run whocite analyze
    ```

4.  **筛选高影响力作者**: 提取顶尖作者。
    ```bash
    uv run whocite filter
    ```

5.  **调研作者 (AI)**: 调研单位和职称。
    ```bash
    uv run whocite research --limit 5
    ```

6.  **合并结果**: 将调研结果合并回列表。
    ```bash
    uv run whocite merge
    ```

## 局限性

-   **Semantic Scholar 覆盖范围**: 本工具依赖 Semantic Scholar API。虽然其覆盖面很广，但对于某些学科或非常新的论文，其覆盖范围可能不如 Google Scholar 全面。Google Scholar 上的一些引用在这里可能会缺失。
-   **API 速率限制**: 本工具遵守 Semantic Scholar 的速率限制（无 Key 时 1 次请求/秒）。建议使用 API Key 以获得更快的处理速度。

## 项目结构

-   `src/whocite/`: 源代码包。
    -   `cli.py`: 主 CLI 入口点。
    -   `config.py`: 配置和路径管理。
    -   `step*.py`: 各个流水线步骤。
-   `config/`: 配置文件和 API Key。
-   `output/`: 生成的数据文件 (JSON/CSV)。
-   `my.bib`: 输入的 BibTeX 文件 (用户提供)。

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。
