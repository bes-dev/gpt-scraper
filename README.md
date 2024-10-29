# GPT-Scraper

GPT-Scraper is an autonomous, LLM-based agent that generates code to extract structured information from web pages.
It is specifically designed to facilitate the process of web scraping using advanced language models such as GPT-4.
This project aims to simplify the extraction of data from web pages by converting user-defined requirements into Python code that executes the desired web scraping tasks.

## Features

- **Dynamic Code Generation**: Generates Python parsing code based on user requirements and webpage content.
- **Flexible Data Structures**: Supports the use of Pydantic models to define the structure of the scraped data.
- **Webpage Source Handling**: Capable of extracting HTML content from both static and dynamic web pages using Selenium.

## Installation

### Prerequisites

- **Python 3.6 or higher**: Ensure you have Python installed. You can download it from the [official website](https://www.python.org/downloads/).
- **ChromeDriver**: Selenium requires ChromeDriver to interact with the Chrome browser. Download it from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads) and ensure it's in your system's PATH.

### Install from git

```bash
$ pip install git+https://github.com/bes-dev/gpt-scraper.git
```

### Install from pip

```bash
$ pip install gpt-scraper
```

## CLI Tool Usage

### Commands

```bash
$ gpt-scraper --help
usage: gpt-scraper [-h] (--requirements REQUIREMENTS | --scraper-file SCRAPER_FILE) --url URL [--output OUTPUT] [--wait-by {id,xpath,css_selector}] [--wait-value WAIT_VALUE]
                   [--save-file SAVE_FILE] [--model-name MODEL_NAME]

GPT-Scraper CLI

options:
  -h, --help            show this help message and exit
  --requirements REQUIREMENTS
                        Scraping requirements
  --scraper-file SCRAPER_FILE
                        Path to the scraper file to load
  --url URL             URL of the webpage to scrape
  --output OUTPUT       Output file path to save scraped data as JSON
  --wait-by {id,xpath,css_selector}
                        Type of locator to wait for
  --wait-value WAIT_VALUE
                        Value of the locator to wait for
  --save-file SAVE_FILE
                        Path to save the created GPTScraper to file
  --model-name MODEL_NAME
                        Name of the model to use for scraping

```

### Sample session

```bash
$ gpt-scraper --url https://news.ycombinator.com/ --requirements 'extract threads list from the web page (extract link and title)' --save-file hn.py --model-name o1-mini
2024-10-29 05:23:25,989 [INFO] Fetching page content from URL: https://news.ycombinator.com/
2024-10-29 05:23:25,989 [INFO] Attempt 1 to fetch URL: https://news.ycombinator.com/
2024-10-29 05:23:27,915 [INFO] Successfully fetched page source for URL: https://news.ycombinator.com/
2024-10-29 05:23:27,977 [INFO] Generating parser using GPTScraper.
2024-10-29 05:23:34,517 [INFO] HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2024-10-29 05:23:34,605 [INFO] Saving scraper to file: hn.json
2024-10-29 05:23:34,605 [INFO] Scraper saved successfully.
2024-10-29 05:23:34,605 [INFO] Parsing HTML content.
2024-10-29 05:23:34,638 [INFO] Printing scraped data:
[
    {
        "title": "Excel Turing Machine (2013)",
        "link": "https://www.felienne.com/archives/2974"
    },
    {
        "title": "High-resolution postmortem human brain MRI at 7 tesla",
        "link": "https://pulkit-khandelwal.github.io/exvivo-brain-upenn/"
    },
    {
        "title": "How Gothic architecture became spooky",
        "link": "https://www.architecturaldigest.com/story/how-gothic-architecture-became-spooky"
    },
    {
        "title": "Using reinforcement learning and $4.80 of GPU time to find the best HN post",
        "link": "https://openpipe.ai/blog/hacker-news-rlhf-part-1"
    }
]
```

## Example

```python
from gpt_scraper import GPTScraper
from gpt_scraper.selenium_utils import fetch_dynamic_page
from pydantic import BaseModel

class Data(BaseModel):
    title: str
    url: str

page_source = fetch_dynamic_page("https://news.ycombinator.com/")
scraper = GPTScraper.from_html(
    page_source,
    "extract threads list from the web page (extract link and title)",
    data_structure=Data,
    model_name="o1-mini"
)
data = scraper.parse_html(page_source)
print(data)
```
