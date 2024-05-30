import time
import os

while True:
    os.system('/usr/local/bin/k6 run /scripts/web_workflow_test.js')
    time.sleep(60)  # Sleep for 1 minute