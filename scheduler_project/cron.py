import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from hello_world import say_hello

# Setup logging
logging.basicConfig(
    filename='scheduler.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def logged_say_hello():
    say_hello()
    logging.info("say_hello() function executed.")

def main():
    logging.info("Scheduler starting.")
    scheduler = BlockingScheduler()
    scheduler.add_job(logged_say_hello, 'interval', seconds=30)

    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")
        print("Scheduler stopped.")

if __name__ == "__main__":
    main()
