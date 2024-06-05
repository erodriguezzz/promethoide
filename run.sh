#!/bin/bash

PYCRON_IMAGE="pycron-image"

if [[ "$(docker images -q $PYCRON_IMAGE 2> /dev/null)" == "" ]]; then
    echo "La imagen de pycron no está construida. Construyendo..."
    docker build -t $PYCRON_IMAGE ./k6-pycron/lib/pycron
fi

docker-compose up