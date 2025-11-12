import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time


def run_automation():
    """
    Automates login, report generation, and logout on the LG portal.
    """

    print("**************Starting automation**************")

    # --- Setup Chrome in maximized mode ---
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Launch Chrome in full screen

    # Initialize browser driver
    driver = webdriver.Chrome(options=options)
    time.sleep(5)

    # --- Load configuration ---
    config = configparser.ConfigParser(interpolation=None)
    config.read("config.ini")

    login_url = config["LOGIN"]["url"]
    username = config["LOGIN"]["username"]
    password = config["LOGIN"]["password"]
    ops_url = config["OPS"]["url"]

    # Navigate to login page
    driver.get(login_url)
    time.sleep(5)

    # --- Login ---
    username_locator = driver.find_element(By.ID, "UserName")
    password_locator = driver.find_element(By.NAME, "Password")
    submit_form_locator = driver.find_element(By.XPATH, "//button[contains(text(),'Sign In')]")

    username_locator.send_keys(username)
    password_locator.send_keys(password)
    submit_form_locator.click()

    # Wait for redirection
    time.sleep(10)
    actual_url = driver.current_url

    if actual_url != ops_url:
        print("Login failed or redirect URL mismatch.")
        driver.quit()
        return

    # --- Generate report ---
    dropdown = driver.find_element(By.ID, "cmbQuery")
    select = Select(dropdown)
    select.select_by_visible_text("ReOCR Failed Karza Documents")

    wait = WebDriverWait(driver, 10)
    generate_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Generate Report']")))
    generate_button.click()
    generate_button.click()
    time.sleep(10)

    # --- Logout ---
    icon = driver.find_element(By.XPATH, "//i[contains(@class,'fa-user-circle')]")
    actions = ActionChains(driver)
    actions.move_to_element(icon).perform()
    logout_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//span[text()='Logout']")))
    logout_element.click()
    time.sleep(5)
    driver.quit()

    print("**************Automation run complete**************")

if __name__ == "__main__":
     run_automation()
