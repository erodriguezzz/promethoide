# Usar la imagen oficial de Ubuntu como base
FROM ubuntu:latest

# Definir argumentos para versiones de Prometheus
ARG PROM_VERSION=2.41.0
ARG PROM_FILE=prometheus-${PROM_VERSION}.linux-amd64

# Instalar herramientas necesarias
RUN apt-get update && apt-get install -y curl tar

# Descargar y descomprimir Prometheus
RUN curl -LO "https://github.com/prometheus/prometheus/releases/download/v${PROM_VERSION}/${PROM_FILE}.tar.gz" \
    && tar -xvf ${PROM_FILE}.tar.gz -C /usr/local/bin/ --strip-components=1 \
    && rm ${PROM_FILE}.tar.gz

# Copiar el archivo de configuración de Prometheus (asumimos que ya tienes uno preparado)
COPY prometheus.yml /etc/prometheus/prometheus.yml

# Exponer el puerto que Prometheus usará
EXPOSE 9090

# Configurar el comando que se ejecutará al iniciar el contenedor
ENTRYPOINT [ "/usr/local/bin/prometheus" ]
CMD [ "--config.file=/etc/prometheus/prometheus.yml", "--storage.tsdb.path=/prometheus" ]
