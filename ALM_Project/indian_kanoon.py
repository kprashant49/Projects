"""
indian_kanoon.py — Selenium-based scraper for Indian Kanoon legal case search.

OPTIONAL / LEGACY MODULE
-------------------------
This scraper requires Google Chrome and ChromeDriver installed on the host.
It is disabled by default. To enable it, set in config.py:

    USE_SELENIUM_INDIAN_KANOON = True

When disabled, evidence_aggregator.py falls back to a SerpAPI Google search
restricted to site:indiankanoon.org, which covers most use cases without the
Chrome dependency.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


def search_indian_kanoon(query: str) -> list[dict]:
    """
    Search Indian Kanoon for legal cases matching the query.
    Returns a list of evidence dicts with source, title, and link.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = None

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options,
        )
        driver.set_page_load_timeout(20)

        url = f"https://indiankanoon.org/search/?formInput={query}"
        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".result_title"))
        )

        soup    = BeautifulSoup(driver.page_source, "html.parser")
        results = []

        for result in soup.select(".result_title a"):
            results.append({
                "source":  "Indian Kanoon",
                "title":   result.text.strip(),
                "link":    "https://indiankanoon.org" + result.get("href", ""),
                "snippet": "Legal case reference from Indian Kanoon",
            })

        return results

    except Exception as e:
        print(f"Indian Kanoon Selenium scraper failed: {e}")
        return []

    finally:
        if driver:
            driver.quit()
