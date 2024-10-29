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

import argparse
import json
import logging
from .gpt_scraper import GPTScraper
from .selenium_utils import fetch_dynamic_page
from .html_utils import preprocess_html_with_summary
from pydantic import BaseModel

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def main():
    logger = setup_logging()

    parser = argparse.ArgumentParser(description='GPT-Scraper CLI')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--requirements', help='Scraping requirements')
    group.add_argument('--scraper-file', help='Path to the scraper file to load')

    parser.add_argument('--url', required=True, help='URL of the webpage to scrape')
    parser.add_argument('--output', help='Output file path to save scraped data as JSON')
    parser.add_argument('--wait-by', choices=['id', 'xpath', 'css_selector'], help='Type of locator to wait for')
    parser.add_argument('--wait-value', help='Value of the locator to wait for')
    parser.add_argument('--save-file', help='Path to save the created GPTScraper to file')
    parser.add_argument('--model-name', default='gpt-4o', help='Name of the model to use for scraping')
    parser.add_argument('--simplify-html', action='store_true', help='Simplify the HTML content before parsing')

    args = parser.parse_args()

    wait_condition = None
    if args.wait_by and args.wait_value:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC

        condition_mapping = {
            'id': By.ID,
            'xpath': By.XPATH,
            'css_selector': By.CSS_SELECTOR
        }
        wait_condition = {
            'by': condition_mapping[args.wait_by],
            'value': args.wait_value,
            'condition': EC.presence_of_element_located
        }

    logger.info(f"Fetching page content from URL: {args.url}")
    page_source = fetch_dynamic_page(args.url, wait_condition=wait_condition)

    if not page_source:
        logger.error("Failed to fetch the webpage.")
        return

    if args.scraper_file:
        logger.info(f"Loading scraper from file: {args.scraper_file}")
        try:
            scraper = GPTScraper.load(args.scraper_file)
            logger.info("Scraper loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load scraper from file: {e}")
            return
    else:
        logger.info("Generating parser using GPTScraper.")
        if args.simplify_html:
            logger.info("Simplifying HTML content before parsing.")
            page_source, _ = preprocess_html_with_summary(
                page_source,
                remove_attributes=True,
                minify=True,
                summarize=True,
                max_sentences=1
            )
        scraper = GPTScraper.from_html(
            page_source, args.requirements, model_name=args.model_name
        )
        if args.save_file:
            try:
                logger.info(f"Saving scraper to file: {args.save_file}")
                scraper.save(args.save_file)
                logger.info("Scraper saved successfully.")
            except Exception as e:
                logger.error(f"Failed to save scraper to file: {e}")

    logger.info("Parsing HTML content.")
    try:
        data = scraper.parse_html(page_source)
    except Exception as e:
        logger.error(f"Error parsing HTML: {e}")
        return

    if args.output:
        logger.info(f"Saving scraped data to {args.output}")
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(
                    [item if isinstance(item, dict) else item.dict() for item in data],
                    f,
                    indent=4,
                    ensure_ascii=False
                )
            logger.info("Data saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
    else:
        logger.info("Printing scraped data:")
        print(
            json.dumps(
                [item if isinstance(item, dict) else item.dict() for item in data],
                indent=4,
                ensure_ascii=False
            )
        )

if __name__ == '__main__':
    main()
