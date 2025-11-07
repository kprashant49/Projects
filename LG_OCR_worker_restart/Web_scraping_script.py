from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Setup
driver = webdriver.Chrome()  # Or use Firefox, Edge, etc.
driver.get("http://rabbitmq-headless.rabbitmq.svc.cluster.local")  # Replace with your RabbitMQ URL

# Login
driver.find_element(By.ID, "username").send_keys("user")
driver.find_element(By.ID, "password").send_keys("dh06SWDt1LK8h070")
driver.find_element(By.ID, "login").click()

# Wait for login and redirect
time.sleep(3)

# Navigate to Queues tab
driver.get("http://rabbitmq-headless.rabbitmq.svc.cluster.local/#/queues")
time.sleep(5)  # Wait for data to load

# Extract queue data
rows = driver.find_elements(By.CSS_SELECTOR, "tr.queue")
for row in rows:
    columns = row.find_elements(By.TAG_NAME, "td")
    if columns:
        queue_name = columns[0].text
        messages = columns[1].text
        print(f"Queue: {queue_name}, Messages: {messages}")

driver.quit()