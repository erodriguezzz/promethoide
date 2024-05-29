FROM ubuntu:latest

RUN apt-get update && apt-get -y install cron curl

#
RUN curl -L -o /tmp/k6.tar.gz https://github.com/grafana/k6/releases/download/v0.51.0/k6-v0.51.0-linux-amd64.tar.gz \
    && tar -xzf /tmp/k6.tar.gz -C /usr/local/bin --strip-components=1 \
    && rm /tmp/k6.tar.gz

COPY web_workflow_test.js /scripts/web_workflow_test.js
COPY crontab /etc/cron.d/my-cron-job 
# TODO cambiar el nombre my-cron-job 

RUN chmod +x /scripts/web_workflow_test.js && chmod 0644 /etc/cron.d/my-cron-job

RUN crontab /etc/cron.d/my-cron-job

CMD ["cron", "-f"]