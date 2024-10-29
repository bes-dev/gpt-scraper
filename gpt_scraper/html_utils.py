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
import re
from typing import Tuple, Optional
from bs4 import BeautifulSoup, Comment
import htmlmin
import nltk
from nltk.tokenize import sent_tokenize


# Ensure the NLTK 'punkt' tokenizer is downloaded
nltk.download('punkt', quiet=True)


def simplify_html(
    html_content: str,
    remove_attributes: bool = True,
    minify: bool = True
) -> str:
    """
    Simplifies HTML content by removing scripts, styles, comments, and optionally unnecessary attributes.

    Args:
        html_content (str): The raw HTML content.
        remove_attributes (bool): Whether to remove attributes from tags.
        minify (bool): Whether to minify the resulting HTML.

    Returns:
        str: Simplified HTML.
    """
    soup = BeautifulSoup(html_content, 'lxml')

    # Remove <script>, <style>, and <noscript> elements
    for tag in soup(['script', 'style', 'noscript']):
        tag.decompose()

    # Remove HTML comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove attributes based on tag-specific whitelists
    if remove_attributes:
        whitelist = {
            'a': ['href', 'title', 'target'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'div': [],
            'span': [],
            'p': [],
            'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': [],
            'ul': [], 'ol': [], 'li': [],
            'table': [], 'tr': [], 'td': [], 'th': [],
            # Add more tags and their allowed attributes if necessary
        }
        for tag in soup.find_all(True):
            allowed_attrs = whitelist.get(tag.name, [])
            attrs_to_delete = [attr for attr in tag.attrs if attr not in allowed_attrs]
            for attr in attrs_to_delete:
                del tag.attrs[attr]

    simplified_html = str(soup)

    # Minify HTML if requested
    if minify:
        simplified_html = htmlmin.minify(
            simplified_html,
            remove_empty_space=True,
            remove_comments=True,
            remove_all_empty_space=True,
            reduce_boolean_attributes=True
        )

    return simplified_html


def summarize_text_simple(text: str, max_sentences: int = 5) -> str:
    """
    Summarizes the text by selecting the first few sentences.

    Args:
        text (str): The text to summarize.
        max_sentences (int): Maximum number of sentences in the summary.

    Returns:
        str: Summarized text.
    """
    sentences = sent_tokenize(text)
    return ' '.join(sentences[:max_sentences]) if len(sentences) > max_sentences else text


def extract_text(html_content: str) -> str:
    """
    Extracts text from HTML content.

    Args:
        html_content (str): The HTML content.

    Returns:
        str: Extracted text.
    """
    soup = BeautifulSoup(html_content, 'lxml')
    text = soup.get_text(separator=' ')
    return re.sub(r'\s+', ' ', text).strip()


def preprocess_html_with_summary(
    html_content: str,
    remove_attributes: bool = True,
    minify: bool = True,
    summarize: bool = True,
    max_sentences: int = 5
) -> Tuple[str, Optional[str]]:
    """
    Simplifies HTML content and provides a summarized version of its text.

    Args:
        html_content (str): The raw HTML content.
        remove_attributes (bool): Whether to remove attributes from tags.
        minify (bool): Whether to minify the resulting HTML.
        summarize (bool): Whether to summarize the extracted text.
        max_sentences (int): Maximum number of sentences in the summary.

    Returns:
        Tuple[str, Optional[str]]: Simplified HTML and summarized text.
    """
    simplified_html = simplify_html(
        html_content,
        remove_attributes=remove_attributes,
        minify=minify
    )

    summary = summarize_text_simple(extract_text(simplified_html), max_sentences) if summarize else None

    return simplified_html, summary


# Example Usage
if __name__ == "__main__":
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sample Page</title>
        <style>
            body {font-family: Arial;}
            .hidden {display:none;}
        </style>
        <script type="text/javascript">
            console.log("This is a script.");
        </script>
    </head>
    <body>
        <h1 id="main-title" class="title">Welcome to the Sample Page</h1>
        <p class="intro">This is a <strong>sample</strong> paragraph with <a href="#" onclick="alert('Clicked!')" title="Sample Link">a link</a>.</p>
        <!-- This is a comment that should be removed -->
        <div class="hidden" data-info="secret">This text is hidden and should be removed.</div>
        <p>Another paragraph to demonstrate preprocessing.</p>
        <img src="image.jpg" alt="Sample Image" width="600" height="400" style="border: none;">
    </body>
    </html>
    """

    simplified_html, summary = preprocess_html_with_summary(
        sample_html,
        remove_attributes=True,
        minify=True,
        summarize=True,
        max_sentences=1
    )

    print("Simplified and Minified HTML with Attributes Removed:\n")
    print(simplified_html)

    if summary:
        print("\nSummarized Text:\n")
        print(summary)
