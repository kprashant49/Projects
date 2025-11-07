from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Setup
driver = webdriver.Chrome()  # Or use Firefox, Edge, etc.
time.sleep(5)

# Navigate to login page
driver.get("https://practicetestautomation.com/practice-test-login/")
time.sleep(10)

# Login
driver.find_element(By.ID, "username").send_keys("student")
driver.find_element(By.ID, "password").send_keys("Password123")
driver.find_element(By.ID, "submit").click()

# Wait for login and redirect
time.sleep(10)