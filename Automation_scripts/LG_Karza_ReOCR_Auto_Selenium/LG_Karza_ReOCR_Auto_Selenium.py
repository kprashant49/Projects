import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

print("**************Starting automation**************")

# --- Setup Chrome in maximized mode ---
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # Launch Chrome in full screen

# Setup driver
driver = webdriver.Chrome(options=options)
time.sleep(5)

# --- Load config ---
config = configparser.ConfigParser(interpolation=None)
config.read("config.ini")

login_url = config["LOGIN"]["url"]
username = config["LOGIN"]["username"]
password = config["LOGIN"]["password"]
ops_url = config["OPS"]["url"]

# Navigate to login page
driver.get(login_url)
time.sleep(5)

# Load the locators
username_locator = driver.find_element(By.ID, "UserName")
# password_locator = driver.find_element(By.ID, "password")
password_locator = driver.find_element(By.NAME, "Password")
# submit_form_locator = driver.find_element(By.ID, "submit")
submit_form_locator = driver.find_element(By.XPATH, "//button[contains(text(),'Sign In')]")
# Other methods
# submit_form_locator = driver.find_element(By.XPATH, "//button[normalize-space()='Sign In']")
# submit_form_locator = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary")
# submit_form_locator = driver.find_elements(By.CSS_SELECTOR, "button.btn.btn-primary")[0]

# Submit the values
username_locator.send_keys(username)
password_locator.send_keys(password)
submit_form_locator.click()

# Wait for login and redirect
time.sleep(10)

# Verify successful login
actual_url = driver.current_url
assert actual_url == ops_url

# Select value from dropdown
dropdown = driver.find_element(By.ID, "cmbQuery")
select = Select(dropdown)
select.select_by_visible_text("ReOCR Failed Karza Documents")

# Other methods
# # OR select by value attribute
# select.select_by_value("object:65")
# # OR select by index (0-based)
# select.select_by_index(2)

wait = WebDriverWait(driver, 10)  # 10 seconds timeout

submit_form_locator2 = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Generate Report']")))

# Other methods
# submit_form_locator2 = driver.find_element("xpath", "//input[@type='submit' and @value='Generate Report']")
# submit_form_locator2 = driver.find_element("class name", "btn-primary")
# submit_form_locator2 = driver.find_element("css selector", "input[ng-click='GenerateQueryReport()']")

submit_form_locator2.click()
submit_form_locator2.click()
time.sleep(10)

# Log Out
icon = driver.find_element(By.XPATH, "//i[contains(@class,'fa-user-circle')]")
# WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".dropdown-menu")))

# icon = driver.find_element(By.CSS_SELECTOR, "i.fas.fa-user-circle")
actions = ActionChains(driver)
actions.move_to_element(icon).perform()
logout_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//span[text()='Logout']")))
logout_element.click()
time.sleep(5)
driver.quit()

print("**************Automation run complete**************")