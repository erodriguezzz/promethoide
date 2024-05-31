#!/bin/bash

if [ "$1" = "exit" ]; then
  echo "Container built successfully. Exiting."
  exit 0
fi

exec python3 -m pycron.scheduler --config /app/config.yaml
