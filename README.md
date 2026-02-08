# whocite

A production-ready Python tool to analyze who is citing your research papers. It fetches citation data from Semantic Scholar, analyzes author demographics, and enriches top-tier citing authors with detailed information (current affiliation, title) using Google GenAI (Gemini) web search.

## Features

-   **Fetch Citations**: Automatically retrieves all citations for papers listed in your `my.bib` file using the Semantic Scholar API.
-   **Author Analysis**: Aggregates statistics like H-Index and total citation counts for every citing author.
-   **High-Impact Filtering**: Identifies top citing authors based on citation count.
-   **AI-Powered Research**: Uses Google GenAI (Gemini 2.0 Flash) with Google Search to find up-to-date affiliations, academic titles, and profile links for high-impact authors.
-   **Merged Reporting**: Generates a final CSV report with original citation data enriched with AI-researched details.

## Prerequisites

-   Python 3.12+
-   [uv](https://github.com/astral-sh/uv) (recommended for dependency management)
-   [Semantic Scholar API Key](https://www.semanticscholar.org/product/api)
-   [Google GenAI API Key](https://aistudio.google.com/) (for web search features)

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/quickhdsdc/WhoCiteYourPapers.git
    cd WhoCiteYourPapers
    ```

2.  Sync dependencies using `uv`:
    ```bash
    uv sync
    ```

## Configuration

1.  **Semantic Scholar API**:
    Create a file named `api key.txt` in the root directory and paste your Semantic Scholar API key inside.

2.  **Google GenAI**:
    Copy the example config:
    ```bash
    cp config/config.example.toml config/config.toml
    ```
    Edit `config/config.toml` and add your Google API key under the `[llm.gemini]` section (or just set `GOOGLE_API_KEY` environment variable).

    ```toml
    [llm.gemini]
    api_key = "YOUR_GOOGLE_API_KEY"
    model = "gemini-2.0-flash-exp"
    ```

3.  **Your Papers**:
    Place your BibTeX file named `my.bib` in the root directory.

## Usage

The tool provides a unified CLI `whocite`. You can run it using `uv run`.

### Quick Start (Run Everything)

To run the entire pipeline from fetching citations to merging researched details:

```bash
uv run whocite run-all --limit-research 30
```

### Step-by-Step Execution

You can also run individual steps:

1.  **Fetch Citations**: Retrieves citation data.
    ```bash
    uv run whocite fetch-citations
    ```

2.  **Fetch Author Details**: Gets stats from Semantic Scholar.
    ```bash
    uv run whocite fetch-authors
    ```

3.  **Analyze Results**: Generates `citations_analysis.csv`.
    ```bash
    uv run whocite analyze
    ```

4.  **Filter High-Impact**: Extracts top authors.
    ```bash
    uv run whocite filter
    ```

5.  **Research Authors (AI)**: Researches affiliation/titles.
    ```bash
    uv run whocite research --limit 5
    ```

6.  **Merge Results**: Merges research back into the list.
    ```bash
    uv run whocite merge
    ```

## Project Structure

-   `src/whocite/`: Source code package.
    -   `cli.py`: Main CLI entry point (Click-based).
    -   `config.py`: Configuration management.
    -   `step*.py`: Individual pipeline steps.
-   `config/`: Configuration files.
-   `pyproject.toml`: Dependency and project metadata.

## License

[MIT](LICENSE)
