import time
import threading
import yaml
import os
import logging
import signal
import sys
from pycron.task import Task

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')

class Scheduler:
    def __init__(self, config_path):
        self.tasks = self.load_config(config_path)
        self.stop_event = threading.Event()

    def load_config(self, config_path):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            tasks = []
            for task_config in config['tasks']:
                task = Task(task_config['command'], task_config['interval'])
                tasks.append(task)
            return tasks

    def run(self):
        threads = []
        for task in self.tasks:
            thread = threading.Thread(target=self.run_task, args=(task,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def run_task(self, task):
        last_run_time = time.time()
        while not self.stop_event.is_set():
            current_time = time.time()
            sleep_time = current_time - last_run_time
            logging.info(f"Running task: {task.command} | Actual sleep time: {sleep_time:.2f}s | Scheduled sleep time: {task.interval:.2f}s")
            
            # Run the task
            task.run()
            elapsed_time = time.time() - current_time
            logging.info(f"Task completed: {task.command} ({elapsed_time:.4f}s)")
            
            # Sleep until the next run
            last_run_time = time.time()
            self.stop_event.wait(max(0, task.interval - elapsed_time))

    def signal_handler(self, sig, frame):
        logging.info("Termination signal received. Stopping tasks...")
        self.stop_event.set()
        for thread in threading.enumerate():
            if thread != threading.main_thread():
                thread.join()
        logging.info("All tasks stopped. Exiting.")
        sys.exit(0)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Pycron Scheduler')
    parser.add_argument('--config', type=str, default=os.getenv('CONFIG_PATH', '/app/config.yaml'), help='Path to the configuration file')
    args = parser.parse_args()

    config_path = os.path.abspath(args.config)
    if not os.path.isfile(config_path):
        raise ValueError(f"Configuration file not found: {config_path}")

    scheduler = Scheduler(config_path)
    signal.signal(signal.SIGINT, scheduler.signal_handler)
    signal.signal(signal.SIGTERM, scheduler.signal_handler)
    scheduler.run()
