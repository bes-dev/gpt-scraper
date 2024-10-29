import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from typing import Optional, Dict, Any
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def fetch_page(url: str) -> Optional[str]:
    """
    Fetches the HTML content of a web page using Selenium.

    Args:
        url (str): The URL of the web page to fetch.

    Returns:
        Optional[str]: The HTML content of the page if successful, else None.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    )
    chrome_options.add_argument("--window-size=1920,1080")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        page_source = driver.page_source
        driver.quit()
        return page_source
    except WebDriverException as e:
        print(f"Selenium WebDriver Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None


def fetch_dynamic_page(
    url: str,
    timeout: int = 30,
    wait_condition: Optional[Dict[str, Any]] = None,
    retries: int = 3,
    delay: int = 5,
    driver_path: Optional[str] = None
) -> Optional[str]:
    """
    Fetches the dynamic web page source using Selenium.

    Args:
        url (str): The URL of the web page to fetch.
        timeout (int, optional): Maximum time to wait for the page to load. Defaults to 30 seconds.
        wait_condition (Dict[str, Any], optional): Conditions to wait for before fetching the page source.
            Example:
                {
                    "by": By.ID,
                    "value": "main-content",
                    "condition": EC.presence_of_element_located
                }
        retries (int, optional): Number of retry attempts in case of failure. Defaults to 3.
        delay (int, optional): Delay between retries in seconds. Defaults to 5.
        driver_path (str, optional): Path to the ChromeDriver executable. If None, assumes it's in PATH.

    Returns:
        Optional[str]: The page source if successful, else None.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Use new headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    )
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Attempt {attempt} to fetch URL: {url}")
            # Initialize the WebDriver
            if driver_path:
                driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
            else:
                driver = webdriver.Chrome(options=chrome_options)

            try:
                driver.set_page_load_timeout(timeout)
                driver.get(url)

                if wait_condition:
                    condition = wait_condition.get("condition", EC.presence_of_element_located)
                    locator = (wait_condition.get("by", By.ID), wait_condition.get("value", ""))
                    logger.info(f"Waiting for condition: {wait_condition}")
                    WebDriverWait(driver, timeout).until(condition(locator))

                # Optionally, you can add more sophisticated waits here

                page_source = driver.page_source
                logger.info(f"Successfully fetched page source for URL: {url}")
                return page_source
            finally:
                driver.quit()

        except TimeoutException:
            logger.warning(f"Timeout while loading the page: {url}")
        except NoSuchElementException:
            logger.warning(f"Desired element not found on the page: {url}")
        except WebDriverException as e:
            logger.error(f"Selenium WebDriver error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

        if attempt < retries:
            logger.info(f"Retrying in {delay} seconds...")
            time.sleep(delay)
        else:
            logger.error(f"All {retries} attempts failed for URL: {url}")

    return None

