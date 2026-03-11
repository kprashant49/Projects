"""
myneta_search.py — Selenium-based PEP screening via Myneta.info.

OPTIONAL / LEGACY MODULE
-------------------------
This scraper requires Google Chrome and ChromeDriver installed on the host.
It is disabled by default. To enable it, set in config.py:

    USE_SELENIUM_MYNETA = True

When disabled, evidence_aggregator.py falls back to a SerpAPI Google search
restricted to site:myneta.info, which covers most use cases without the
Chrome dependency.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# All matching logic lives in name_matcher — no direct rapidfuzz import here
from name_matcher import is_pep_match


def search_myneta(name: str) -> list[dict]:
    """
    Search Myneta.info for politicians matching the given name.
    Uses is_pep_match from name_matcher for consistent, threshold-controlled comparison.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
    )

    try:
        driver.get("https://myneta.info/")

        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(name)
        search_box.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(@href,'candidate.php')]")
            )
        )

        links   = driver.find_elements(By.XPATH, "//a[contains(@href,'candidate.php')]")
        results = []

        for link in links:
            candidate_name = link.text.strip()

            if is_pep_match(name, candidate_name):
                results.append({
                    "source":  "Myneta",
                    "title":   candidate_name,
                    "link":    link.get_attribute("href"),
                    "snippet": "Political exposure record found on Myneta",
                })

        return results

    except Exception as e:
        print(f"Myneta Selenium scraper failed: {e}")
        return []

    finally:
        driver.quit()
