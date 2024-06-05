import logging
import os
from pycron.utils import parse_interval

class Task:
    def __init__(self, command, interval):
        self.command = command
        self.interval = parse_interval(interval)
        logging.info(f"Created task: {self.command} | Interval: {interval}")

    def run(self):
        os.system(self.command)