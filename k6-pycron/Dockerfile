FROM pycron-image

# Install Python and curl
RUN apt-get update && apt-get -y install python3 curl

# Download and install k6
RUN curl -L -o /tmp/k6.tar.gz https://github.com/grafana/k6/releases/download/v0.51.0/k6-v0.51.0-linux-amd64.tar.gz \
    && tar -xzf /tmp/k6.tar.gz -C /usr/local/bin --strip-components=1 \
    && rm /tmp/k6.tar.gz

# Copy the test script and Python scheduler
COPY web_workflow_test.js /scripts/web_workflow_test.js

# Copia el archivo de configuración
COPY my_config.yaml /app/config.yaml

