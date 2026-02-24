from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def search_indian_kanoon(query):

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without opening browser window
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        url = f"https://indiankanoon.org/search/?formInput={query}"
        driver.get(url)

        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".result_title"))
        )

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        results = []

        for result in soup.select(".result_title a"):
            results.append({
                "source": "Indian Kanoon",
                "title": result.text.strip(),
                "link": "https://indiankanoon.org" + result.get("href")
            })

        return results

    finally:
        driver.quit()