from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Setup
driver = webdriver.Chrome()  # Or use Firefox, Edge, etc.
time.sleep(2)

# Navigate to login page
driver.get("https://practicetestautomation.com/practice-test-login/")
time.sleep(2)

# Load the locators
username_locator = driver.find_element(By.ID, "username")
# password_locator = driver.find_element(By.ID, "password")
password_locator = driver.find_element(By.NAME, "password")
# submit_form_locator = driver.find_element(By.ID, "submit")
submit_form_locator = driver.find_element(By.XPATH, "//button[@class='btn']")

# Submit the values
username_locator.send_keys("student")
password_locator.send_keys("Password123")
submit_form_locator.click()

# Wait for login and redirect
time.sleep(2)

# Verify successful login ("https://practicetestautomation.com/logged-in-successfully/")
actual_url = driver.current_url
assert actual_url == "https://practicetestautomation.com/logged-in-successfully/"

text_locator = driver.find_element(By.TAG_NAME, "h1")
actual_text = text_locator.text

assert actual_text == "Logged In Successfully"

# Log Out
log_out_button = driver.find_element(By.LINK_TEXT, "Log out")
assert log_out_button.is_displayed()
log_out_button.click()
time.sleep(2)