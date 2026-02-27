from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def search_myneta(name):

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        driver.get("https://myneta.info/")

        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(name)
        search_box.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'candidate.php')]"))
        )

        links = driver.find_elements(By.XPATH, "//a[contains(@href,'candidate.php')]")

        results = []

        for link in links:
            results.append({
                "source": "Myneta",
                "title": link.text,
                "link": link.get_attribute("href"),
                "snippet": "Political exposure record found in Myneta"
            })

        return results

    except Exception as e:
        print(f"Myneta Selenium failed: {e}")
        return []

    finally:
        driver.quit()