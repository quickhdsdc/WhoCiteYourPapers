# WhoCiteYourPapers

A Python-based toolset to analyze who is citing your research papers. It fetches citation data from Semantic Scholar, analyzes author demographics, and enriches top-tier citing authors with detailed information (current affiliation, title) using Google GenAI (Gemini) web search.

## Features

-   **Fetch Citations**: Automatically retrieves all citations for papers listed in your `my.bib` file using the Semantic Scholar API.
-   **Author Analysis**: Aggregates statistics like H-Index and total citation counts for every citing author.
-   **High-Impact Filtering**: Identifies top citing authors based on citation count.
-   **AI-Powered Research**: Uses Google GenAI (Gemini 2.0 Flash) with Google Search to find up-to-date affiliations, academic titles, and profile links for high-impact authors.
-   **Reporting**: Generates comprehensive CSV reports (`citations_analysis.csv`, `high_impact_citing_authors.csv`).

## Prerequisites

-   Python 3.12+
-   [Semantic Scholar API Key](https://www.semanticscholar.org/product/api)
-   [Google GenAI API Key](https://aistudio.google.com/) (for web search features)

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/quickhdsdc/WhoCiteYourPapers.git
    cd WhoCiteYourPapers
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    # OR using uv
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

## Usage Workflow

Run the scripts in the following order to build your analysis:

### 1. Fetch Citations
Retrieves citation data for papers in `my.bib`.
```bash
python fetch_citations.py
```

### 2. Fetch Author Statistics
Gets H-Index and total citation counts for all citing authors.
```bash
python fetch_author_details.py
```

### 3. Generate Analysis Report
Combines citation and author data into a unified CSV/JSON.
```bash
python analyze_results.py
```
*Output: `citations_analysis.csv`*

### 4. Filter High-Impact Authors
Extracts the top 30 authors by citation count (configurable).
```bash
python filter_authors.py
```
*Output: `high_impact_citing_authors.csv`*

### 5. Research Author Details (AI)
Uses LLM + Web Search to find current affiliation and titles for the filtered authors.
```bash
python research_authors.py
```
*Output: `high_impact_authors_enriched.csv`*

### 6. Merge Results
Merges the researched details back into the main high-impact list.
```bash
python merge_research_results.py
```
*Final Output: `high_impact_citing_authors.csv` (updated with `Researched Name`, `Affiliation`, `Title`, `Link`)*

## Project Structure

-   `fetch_citations.py`: Interaction with Semantic Scholar Paper API.
-   `fetch_author_details.py`: Interaction with Semantic Scholar Author Batch API.
-   `analyze_results.py`: Data processing and reporting.
-   `filter_authors.py`: Filtering logic.
-   `research_authors.py`: AI agent for web research using Google GenAI.
-   `merge_research_results.py`: Data merging utility.
-   `config/`: Configuration files.

## License

[MIT](LICENSE)
