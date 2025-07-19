import time

while True:
    with open("service_log.txt", "a") as f:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"Welcome - Current Time: {now}\n")
    time.sleep(10)
