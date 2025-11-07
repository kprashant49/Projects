from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Setup
driver = webdriver.Chrome()  # Or use Firefox, Edge, etc.
time.sleep(5)

# Navigate to login page
driver.get("https://practicetestautomation.com/practice-test-login/")
time.sleep(5)

# Load the locators
username_locator = driver.find_element(By.ID, "username")
password_locator = driver.find_element(By.ID, "password")
submit_form_locator = driver.find_element(By.ID, "submit")

# Submit the values
username_locator.send_keys("student")
password_locator.send_keys("Password123")
submit_form_locator.click()

# Wait for login and redirect
time.sleep(5)

# Verify successful login
text_locator = driver.find_element(By.TAG_NAME, "h1")
log_out_button = driver.find_element(By.LINK_TEXT, "Log out")

# Log Out
log_out_button.click()
time.sleep(5)