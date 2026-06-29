# Iteris Tools

The `iteris.tools` package provides modules for interacting with external mathematical and scientific resources, specifically arXiv and the LeanSearch theorem database. These tools are designed to be used both programmatically as Python APIs and via the Iteris CLI.

---

## Table of Contents
1. [LeanSearch Theorem Search (`theorem_search.py`)](#1-leansearch-theorem-search-theorem_searchpy)
   - [Python API](#python-api)
   - [CLI Usage](#cli-usage)
2. [arXiv Reference Fetcher (`arxiv.py`)](#2-arxiv-reference-fetcher-arxivpy)
   - [Python API](#python-api-1)
   - [CLI Usage](#cli-usage-1)
3. [Project Directory Layout & Integration](#3-project-directory-layout--integration)

---

## 1. LeanSearch Theorem Search (`theorem_search.py`)

This tool queries the LeanSearch theorem database to retrieve mathematical theorems, definitions, and lemmas that match a given query. It is highly useful for grounding agent research loops in existing mathematical literature.

### Python API

```python
from iteris.tools.theorem_search import search_arxiv_theorems

# Search for theorems related to a specific mathematical statement
result = search_arxiv_theorems(
    query="Goldbach's conjecture",
    num_results=5,
    timeout_seconds=30
)

print(f"Found {result['count']} theorems.")
for item in result["results"]:
    print(f"Title: {item['title']}")
    print(f"Theorem: {item['theorem']}")
    print(f"arXiv ID: {item['arxiv_id']}")
    print(f"Theorem ID: {item['theorem_id']}")
```

#### API Details
- **Endpoint**: `https://leansearch.net/thm/search`
- **Arguments**:
  - `query` (str): Mathematical statement or description of the theorem.
  - `num_results` (int, default: 10): Maximum number of search results to return.
  - `timeout_seconds` (int, default: 30): Timeout for the HTTP requests.
- **Returns**: A dictionary containing:
  - `query`: The requested query string.
  - `count`: Number of retrieved results.
  - `results`: List of dictionaries containing `title`, `theorem`, `arxiv_id`, and `theorem_id`.
  - `endpoint`: The API endpoint queried.

### CLI Usage

You can search theorems using the Iteris CLI command:

```bash
iteris tool theorem search --query "Riemann hypothesis" --num-results 5
```

Or you can run the script standalone directly:

```bash
python src/iteris/tools/theorem_search.py --query "Riemann hypothesis" --num-results 5
```

**Options**:
- `--query`, `-q` (Required): The query string.
- `--num-results`, `-n` (Default: 10): Maximum number of results.
- `--timeout`, `-t` (Default: 30): Request timeout in seconds.
- `--json`: Print the results as machine-readable JSON. (Note: the standalone script always outputs JSON).

---

## 2. arXiv Reference Fetcher (`arxiv.py`)

This tool downloads arXiv publications. To ensure the highest fidelity representation of equations and markup, it prefers downloading LaTeX sources (`e-print`), falling back to extracting clean text from the PDF if the LaTeX source is unavailable.

### Python API

```python
from pathlib import Path
from iteris.tools.arxiv import fetch_arxiv_reference

project_root = Path("/path/to/iteris/project")

# Fetch an arXiv paper by its ID
manifest = fetch_arxiv_reference(
    project_root=project_root,
    arxiv_id="2103.00001",
    include_pdf=False,  # Set to True to fetch both source and PDF
    timeout_seconds=60
)

print(f"Stored references in: {manifest['reference_dir']}")
print(f"Primary source files: {manifest['primary_paths']}")
```

#### API Details
- **Arguments**:
  - `project_root` (Path): Path to the active Iteris project.
  - `arxiv_id` (str): Raw arXiv ID or arxiv.org URL (e.g. `2103.00001`, `arxiv:2103.00001`, or `https://arxiv.org/abs/2103.00001`).
  - `timeout_seconds` (int, default: 60): Timeout for HTTP operations.
  - `include_pdf` (bool, default: False): If True, downloads and extracts the PDF text even if LaTeX sources were successfully downloaded.
- **Returns**: A manifest dictionary containing:
  - `arxiv_id`: Normalized arXiv identifier.
  - `reference_dir`: Relative path where files were saved.
  - `primary_paths`: List of files (extracted LaTeX source or text files) containing the paper content.
  - `source`: Dictionary indicating the source retrieval status (`ok`, `status_code`, format, files, errors).
  - `pdf`: Dictionary indicating PDF text extraction status if fetched.

### CLI Usage

Using the Iteris CLI command:

```bash
iteris tool theorem fetch --arxiv-id "2103.00001"
```

Or running the script standalone directly:

```bash
python src/iteris/tools/arxiv.py --arxiv-id "2103.00001" --project-root .
```

**Options**:
- `--arxiv-id` (Required): The arXiv ID or full arXiv URL.
- `--project-root`, `--dir` (Default: `.`): Root directory of the project.
- `--timeout` (Default: 60): Request timeout in seconds.
- `--include-pdf` (Default: False): Fetch and extract the PDF even if source is available.

---

## 3. Project Directory Layout & Integration

When references are retrieved, they are organized in the project workspace's artifacts directory:

```text
MyProblem/
└── artifacts/
    └── references/
        ├── theorem_search/
        │   └── query-<hash>.json       # Cached query search results
        └── arxiv/
            └── <slugified-arxiv-id>/
                ├── manifest.json       # Record of downloaded assets and state
                ├── source-eprint.raw   # Raw downloaded eprint file
                ├── source/             # Extracted LaTeX sources (if available)
                │   ├── source.tex
                │   └── ...
                ├── paper.pdf           # Downloaded PDF (if fetched/needed)
                └── paper.txt           # Extracted plain text of the PDF
```

- **Query Cache**: LeanSearch queries are hashed and cached to avoid redundant network overhead and rate limits.
- **Dependency Notice**: PDF text extraction requires `pdfminer.six`. If missing, it can be installed via `pip install pdfminer.six` or reinstalling Iteris' development dependencies.
