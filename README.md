
<!---    ```bash--->
<!---    docker network create mymonitoringnet--->
<!---    ```--->


<!---    ```bash--->
<!---    docker build -t my-ubuntu-prometheus .--->
<!---    ```--->


<!--- ```bash--->
<!--- docker run -d --network mymonitoringnet --name ubuntu1 my-ubuntu-prometheus--->
<!--- docker run -d --network mymonitoringnet --name ubuntu2 my-ubuntu-prometheus--->
<!--- docker run -d --network mymonitoringnet --name ubuntu3 my-ubuntu-prometheus--->
<!--- docker run -d --network mymonitoringnet --name ubuntu4 my-ubuntu-prometheus--->

<!--- ```--->
<!--- ## Paso 5: Verificar la Implementación--->
<!--- --->
<!--- 1. **Listar los contenedores activos:**--->
<!---    ```bash--->
<!---    docker ps--->
<!---    ```--->

<!--- 2. **Acceder a las interfaces web de Prometheus:**--->
<!---    Localiza la IP de uno de tus contenedores (por ejemplo, `ubuntu1`) y accede a la interfaz web de Prometheus en el puerto `9090` usando un navegador:--->
<!---    ```bash--->
<!---    docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ubuntu1--->
<!---    ```--->

<!---    Visita `http://<Contenedor_IP>:9090` en tu navegador.--->
# Promethoide

Promethoide es una red virtual desarrollada en Docker con la capacidad de monitorear hosts y servicios dentro de la misma, que cuenta con una interfaz visual en Grafana para observar las métricas recopiladas de cada uno de ellos. Algunos de los servicios nativos de la red son:

### Prometheus

Este servicio es el orquestador del monitoreo de todos los otros hosts y servicios. Al estar configurado en docker que todos los contenedores forman parte de la misma red, este servicio gestiona y controla las métricas de cada uno de ellos y las expone para que desde Grafana se puedan consumir y visualizar en dashboards.

### API Rest

La API Rest fue desarrollada en Fast API. Consta de la funcionalidad básica que utilizaría un operario de un puesto de inmigraciones en un aeropuerto. Esto sería validar que el DNI del viajero no aparezca en la base de datos de Interpol, verificar que el vuelo exista y asegurarse de que el hospedaje y el dinero que tiene declarado para su estadía son suficientes.

### PostgreSQL

Este servicio fue levantado para almacenar la información de migraciones. Dentro de el mismo se encuentra la tabla de interpol que emula la base de datos de la organización de seguridad internacional, la tabla de vuelos y la de migraciones. Este servicio va a ser utilizado por la API para almacenar y consultar información.

### Node Exporter

Este servicio nos permite montar en un contenedor de Docker características de hardware del host que levantó el contenedor. Se sirve de una copia en read-only del sistema operativo y del mismo obtiene métricas de hardware que luego expone en un endpoint para que prometheus consuma.

### Apache

Apache es un servicio web del sistema que sirve una página muy básica hecha con javascript, html y css. Dicha página cuenta con el flujo básico que utilizaría un operario de inmigraciones, consumiendo la Rest API e impactando en el Postgres Server, ambos explicados anteriormente. A su vez, modificando la configuración y agregando un modulo para habilitar el monitoreo del servicio, se exponen en el endpoint `/server-status` las métricas del estado del mismo para luego ser consumidas.

### Apache exporter

Este servicio permite hacer scrapping de las métricas del servicio Apache en el endpoint `/server-status` en intervalos de tiempo preestablecidos. Luego, estas métricas seran proporcionadas al servicio de Prometheus para que esta las provea como data source a grafana.

### Blackbox exporter

El servicio de Blackbox Exporter nos permite hacer probing HTTP, DNS, etc. Nos da la posibilidad de settear los distintos endpoints de una web para verificar su tiempo de respuesta y el status code que devuelve entre otras cosas. Al igual que el servicio anterior, el probing se hace a intervalos de tiempo iguales.

### Grafana

El servicio de Grafana es el encargado de recopilar todas las métricas proporcionadas por prometheus y brindarle observabilidad al administrador de la red de aquello que esta ocurriendo en los distintos servicios. Dentro de este, se settean alertas que notifican a los distintos niveles de administradores de problemas tales como alta latencia en endpoints de la API, caída de un servicio y delays fuera de lo común en el servicio web. Las alertas se envían a través de un servidor SMTP configurado dentro del mismo servicio de grafana.

## Instalación

Para instalar Promothoide, es necesario contar con una versión actualizada de [Docker](https://docs.docker.com/engine/install/) y [Docker Compose](https://docs.docker.com/compose/install/). Los requerimientos de cada uno de los servicios van a ser manejados por las distintas imagenes que se descarguen en los contenedores de Docker.

```bash
├── apache
│ ├── Dockerfile
│ ├── proxy.conf
│ ├── script.js
│ ├── styles.css
│ └── index.html
├── api
│ ├── main.py
│ └── requirements.txt
├── blackbox
│ └── blackbox.yml
├── grafana
│ └── provisioning
│    └── alerting
│       └── alerting.yml
│    └── dashboards
│       └── dashboards.yml
│    └── datasources
│       └── datasources.yaml
├── postgres
│ └── init.sql
├── prometheus
│ └── prometheus.yml
├── .example.env
├── .gitignore
├── docker-compose.yaml 
└── README.md
```

Aca podemos visualizar el arbol del proyecto y algunos de los archivos a los que haremos referencia. La configuración central de cada servicio estará por lo general en el archivo `docker-compose.yaml` el cual explicaremos en detalle a continuación.

## Ejecución

Basta tener el archivo `.env` correspondiente a la altura de la carpeta padre y correr el siguiente comando para levantar promethoide.

```yaml
##################### POSTGRES SECRETS #########################
POSTGRES_USER=<postgres-user>
POSTGRES_PASSWORD=<postgres-pass>
POSTGRES_DB=<postgres-db>
POSTGRES_HOST=<postgres-host>
POSTGRES_PORT=<postgres-port>
##################### GRAFANA SMTP SECRETS #####################
GF_SMTP_FROM_ADDRESS=<address-of-sender>
GF_SMTP_FROM_NAME=<name-of-sender>
GR_SMTP_HOST=<name:port>
GF_SMTP_PASSWORD=<application-password>
```

```bash
docker compose up
```

## Estructura de Promethoide

La columna vertebral de este proyecto es, como en todo proyecto elaborado en docker, el archivo de configuración `docker-compose.yaml`. En le mismo se explicita la configuración de cada uno de los servicios y el setteo de las distintas redes.

```yaml
version: '3.8'

# https://docs.docker.com/network/drivers/: bridge mode by default
networks:
    operations-net:
    services-net:

volumes:
  # Metrics storage
    prometheus-data:
        driver: local
  # Config files and dashboards configurations
    grafana-data:
        driver: local
```

Para permitir que los servicios puedan interactuar entre ellos, es indispensable que esten dentro de la misma red. En este caso, nosotros decidimos tener dos redes: `operations-net` y `services-net`. Hicimos esta distinción ya que consideramos que el en un caso real, el equipo que monitorea las métricas de algunos servicios podría no ser el mismo equipo que tiene acceso a los servicios en sí. Es por eso que la red de `operations-net` engloba al servicio de prometheus y grafana, mientras que `services-net` agrupa en una red todos los otros servicios y también prometheus.

Si bien esto podría haberse modularizado más, consideramos que esta división era suficiente para hacer la división correspondiente entre grupos de usuarios.

Por otra parte, se crearon dos volumenes para los servicios de monitoreo de grafana y prometheus, que permiten almacenar configuración como dashboards y alertas entre otras cosas.

### Configuration de Prometheus

```yaml
services:
  prometheus:
      image: prom/prometheus:latest
      container_name: prometheus
      restart: unless-stopped
      volumes:
          - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
          - prometheus-data:/prometheus
      command:
          - '--config.file=/etc/prometheus/prometheus.yml'
          - '--storage.tsdb.path=/prometheus'
          - '--web.console.libraries=/etc/prometheus/console_libraries'
          - '--web.console.templates=/etc/prometheus/consoles'
          - '--web.enable-lifecycle'
      expose:
          - 9090
      ports:
          - 9090:9090
      networks:
          - operations-net
          - services-net
```

Se puede observar que dicho servicio esta en ambas redes mencionadas previamente y cuenta con dos volumenes. El primero se encarga de copiar la configuración establecida en el archivo local `prometheus.yml` y pasarlo a la configuración del servicio dentro de la carpeta `/etc/prometheus`, mientras que el segundo recopila la información de los datos recolectados.

El servicio de prometheus es el encargado de orquestar y gestionar las métricas expuestas por los distintos servicios. Es por ello que en su configuración debe identificar los puntos de acceso de cada uno de ellos para poder extraer la información en cuestión. Veamos en detalle el archivo `prometheus.yml` que es donde se explicita dicho comportamiento.

```yaml
# prometheus.yml - 1/3

global:
  scrape_interval: 15s
  evaluation_interval: 15s
```

Tras settear un tanto el intervalo de scrapping de las métricas como el intervalo de evaluación, se comienza con la configuración estática de los targets para hacer polling de las métricas.

```yaml
# prometheus.yml - 2/3

scrape_configs:

  - job_name: 'node-exporter'
    static_configs:
        - targets: ['node-exporter:9100']

  - job_name: 'rest-api'
    static_configs:
      - targets: ['rest-api:5001']

  - job_name: 'apache-exporter'
    static_configs:
        - targets: ['apache-exporter:9117']
  
  - job_name: 'postgres-exporter'
    static_configs:
        - targets: ['postgres-exporter:9187']
```

- `job_name`: Es el identificador del servicio sobre el cual se va a scrapear.
- `static_configs`: Es la lista de configuraciones estáticas donde se define un conjunto de targets a scrapear
- `targets`: Lista de <ip:puerto> que van a ser scrapeados

Si bien el servicio de Prometheus tiene la opción de configurar un Service Discovery para encontrar automáticamente los targets de donde obtener las métricas, al tener pocos servicios y tener control completo sobre el entorno que estamos trabajando nos pareció más sencillo configurar la lista de targets de manera estática.

```yaml
  - job_name: 'blackbox-exporter'
    metrics_path: /probe
    params:
      module: [http_2xx]  # Look for a HTTP 200 response.
    static_configs:
      - targets:
        - http://apache:80
        - http://rest-api:5001
        - http://apache:80/delay
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115  # The blackbox exporter's real hostname:port.
```

Esta configuración estatica de scrapping es la única que se diferencia de las demás. Nos permite hacer probing de los targets listados dentro de static_configs y buscar códigos de respuesta 200. Nos va a permitir determinar si nuestros servicios estan caídos o si comprobar el delay de un endpoint determinado dentro de nuestra web app.

### Configuration de Rest API

```yaml
    rest-api:
        image: python:3.10
        container_name: rest-api
        restart: unless-stopped
        command: /bin/sh -c "pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 5001"
        volumes:
            - ./api:/app
        working_dir: /app
        environment:
            - POSTGRES_USER=${POSTGRES_USER}
            - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
            - POSTGRES_DB=${POSTGRES_DB}
            - POSTGRES_HOST=${POSTGRES_HOST}
            - POSTGRES_PORT=${POSTGRES_PORT}
        ports:
            - "5001:5001"
        depends_on:
            - postgres
        networks:
            - services-net

```

Este servicio esta configurado dentro de la red de servicios `services-net` y su inicialización depende del servicio de postgres. Se pasan como variables de entorno las credenciales necesarias para pegarle a la base de datos, y los requerimientos se proveen desde el archivo requirements.txt.

Para exejutar la API se corre el comando explicitado bajo el tag command, que se encarga de instalar los requerimientos y ejecutar el archivo main.py. De este modo, queda expuesta la API en el puerto 5001 de nuestro contenedor.

Una vez levantada la API, más allá de generar los distintos endpoints  que serán necesarios para la aplicación web, es vital hacer algunas configuraciones. En primer lugar, requerimos proporcionar un endpoint para que prometheus extraiga las métricas que queramos medir de nuestra Rest API. Es por esto que utilizando la librería prometheus_client recopilamos métricas y habilitamos el endpoint `/metrics` para exponerlas.

```python
from prometheus_client import Counter, generate_latest, Histogram, CONTENT_TYPE_LATEST
```

```python
@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return Response(content=data, status_code=200, headers={"Content-Type": CONTENT_TYPE_LATEST})
```

Dentro de la misma API, buscamos mediante el uso de un middleware medir la latencia de cada uno de los endpoints para luego desde grafana poder visualizar la carga sobre ellos. En base a eso configuramos alarmas que notifican a lso administradores de la red de servicios.

```python
REQUEST_LATENCY = Histogram(
    "rest_api_request_latency",
    "Latency of HTTP requests in seconds",
    ["endpoint"],
    buckets=[0.050, 0.100, 0.150, 0.200, 0.250, 0.300, 0.350, 0.400, 0.450, 0.500, 0.550, 0.600, 0.650, 0.700, 0.750,
             0.800, 0.850, 0.900, 0.950, 1.0]
)
REQUEST_COUNT = Counter("rest_api_requests_total", "Total number of requests received")

@app.middleware("http")
async def add_prometheus_metrics(request: Request, call_next):

    if request.url.path == "/metrics":
        return await call_next(request)

    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    REQUEST_LATENCY.labels(request.scope['route'].name).observe(process_time)

    REQUEST_COUNT.inc()
    return response
```

Por otra parte, cada uno de los endpoints tiene otra métrica donde se calcula la cantidad total de requests. 

### Configuration de Postgres

### Configuración de Node Exporter

### Configuración de Apache

### Configuración de Apache Exporter

### Configuración de Blackbox Exporter

### Configuration de Grafana

```yaml
services:
    grafana:
        image: grafana/grafana-oss:latest
        container_name: grafana
        restart: unless-stopped
        volumes:
            - grafana-data:/var/lib/grafana
            - ./grafana/provisioning:/etc/grafana/provisioning
        environment:
            - GF_SMTP_ENABLED=true
            - GF_SMTP_HOST=${GR_SMTP_HOST}
            - GF_SMTP_USER=${GF_SMTP_FROM_ADDRESS}
            - GF_SMTP_PASSWORD=${GF_SMTP_PASSWORD}
            - GF_SMTP_FROM_ADDRESS=${GF_SMTP_FROM_ADDRESS}
            - GF_SMTP_FROM_NAME=${GF_SMTP_FROM_NAME}
            - GF_SMTP_SKIP_VERIFY=true
        expose:
            - 3000
        ports:
            - 3000:3000
        depends_on:
            - rest-api
            - apache
        networks:
            - operations-net
```

La configuración del servicio de grafana dentro del docker-compose.yml comienza definiendo los volumenes necesarios para el servicio. Primero se configura el volumen que almacenará la información recolectada en la sesión y luego se incluye un volumen de configuración. Sobre el directorio `/etc/grafana/provisioning` se va a montar la carpeta local que contiene la configuración de los dashboards, alertas, puntos de contactos y políticas de notificación. Es desde esta careta que grafana podrá generar los dashboards necesarios para visualizar la información y notificar a alguien de ser necesario.

Por otra parte, se definen variables de entorno para poder inicializar un servidor SMTP dentro de Grafana, que va a ser el responsable de enviar las notificaciones via mail a los distintos niveles de administradores. Un detalle importante a la hora de utilizar este servidor de mail es que para poder utilizar un mail propio como remitente de los mails es necesario desde el cliente del proveedor (en nuestro caso Gmail) generar una [clave de aplicación](https://support.google.com/mail/answer/185833?hl=en).

Cabe mencionar que el servicio de la inicialización de grafana depende de los servicios de rest-api y apache, y pertenece a la red `operations-net`, que se encuentra aislada de la red de servicios.


## Monitoreo en Promethoide

Dejando de lado la configuración y adentrandonos un poco en el monitoreo en sí de la red, recorramos la herramienta utilizada y observemos cómo se definieron cada uno de los aspectos del monitoreo de este sistema.

En el browser al ir a http://localhost:3000, lo primero que observaremos es el inicio de sesión del servicio de Grafana.

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/442bc9e8-1ed1-4c3f-9201-31ca77e5557f/7fa50559-d253-4c93-832d-fc6f62314e96/Untitled.png)

### Comando útiles para el desarrollo
```bash
docker exec -it postgres_container psql -U <postgres_user>
```
```bash
docker exec -it rest_api sh
```
```bash
docker rm -f $(docker ps -aq)
```
```bash
docker kill <container_name>
```
```bash
docker rmi -f $(docker images -q)
```

### Colaboradores
- [Felipe Cupitó](https://github.com/FelipeCupito) - fcupito@itba.edu.ar
- [Roberto Franco Rodriguez Tulasne](https://github.com/robrodriguez99) - robrodriguez@itba.edu.ar
- [Leonardo Agustín D'Agostino](https://github.com/daguichi) - ldagostino@itba.edu.ar
- [Leandro Ezequiel Rodriguez](https://github.com/erodriguezzz) - learodriguez@itba.edu.ar
