"""
Copyright 2024 by Sergei Belousov

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

DATA_STRUCTURE_PROMPT = """
** Output data structure: **
{{DATA_STRUCTURE}}
"""

SCRAPER_GENERATOR_PROMPT = """
You are an expert website analyzer specializing in web scraping processes.
Your task is to convert the user's requirements into clean, efficient Python code that scrapes the website and extracts the desired data.

** User requirements: **
{{USER_REQUIREMENTS}}

{{EXTRA_REQUIREMENTS}}

** Please generate a Python function with the following signature: **
```python
from typing import List, Dict

def parse(html: str) -> List[Dict]:
    ...
```

** Implementation requirements: **
- Utilize appropriate libraries for HTML parsing, such as BeautifulSoup, lxml, or etc..
- Implement robust error handling to manage potential parsing issues.
- Ensure the function returns the extracted data as a list of dictionaries with a well-defined structure.
- Include all necessary imports in the code.
- Adhere to PEP8 coding standards for readability and maintainability.
- Optimize the code for performance where possible.
- Do not include any explanations, comments, or additional text—return only the code block.
- Return implementation as block of code formated using:
```python
<python_code>
```

** HTML Code to parse: **
{{HTML_CODE}}
"""
