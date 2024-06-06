# Promethoide

Promethoide es una red virtual desarrollada en Docker con la capacidad de monitorear hosts y servicios dentro de la misma, que cuenta con una interfaz visual en Grafana para observar las métricas recopiladas de cada uno de ellos. Algunos de los servicios nativos de la red son:

### Prometheus

Este servicio es el orquestador del monitoreo de todos los otros hosts y servicios. Al estar configurado en docker que todos los contenedores forman parte de la misma red, este servicio gestiona y controla las métricas de cada uno de ellos y las expone para que desde Grafana se puedan consumir y visualizar en dashboards.

### API Rest

La API Rest fue desarrollada en Fast API. Consta de la funcionalidad básica que utilizaría un operario de un puesto de inmigraciones en un aeropuerto. Esto sería validar que el DNI del viajero no aparezca en la base de datos de Interpol, verificar que el vuelo exista y asegurarse de que el hospedaje y el dinero que tiene declarado para su estadía son suficientes.

### PostgreSQL

Este servicio fue levantado para almacenar la información de migraciones. Dentro de el mismo se encuentra la tabla de interpol que emula la base de datos de la organización de seguridad internacional, la tabla de vuelos y la de migraciones. Este servicio va a ser utilizado por la API para almacenar y consultar información.

### Postgres Exporter

Este exporter es un servicio capaz de exponer métricas propias del servicio previamente explicado. Se le provee la manera para acceder al data source correspondiente para que pueda obtener métricas sobre la lectura y escritura en la base de datos.

### Node Exporter

Este servicio nos permite montar en un contenedor de Docker características de hardware del host que levantó el contenedor. Se sirve de una copia en read-only del sistema operativo y del mismo obtiene métricas de hardware que luego expone en un endpoint para que prometheus consuma.

### Apache

Apache es un servicio web del sistema que sirve una página muy básica hecha con javascript, html y css. Dicha página cuenta con el flujo básico que utilizaría un operario de inmigraciones, consumiendo la Rest API e impactando en el Postgres Server, ambos explicados anteriormente. A su vez, modificando la configuración y agregando un modulo para habilitar el monitoreo del servicio, se exponen en el endpoint `/server-status` las métricas del estado del mismo para luego ser consumidas.

### Apache exporter

Este servicio permite hacer scrapping de las métricas del servicio Apache en el endpoint `/server-status` en intervalos de tiempo preestablecidos. Luego, estas métricas seran proporcionadas al servicio de Prometheus para que esta las provea como data source a grafana.

### Blackbox exporter

El servicio de Blackbox Exporter nos permite hacer probing HTTP, DNS, etc. Nos da la posibilidad de settear los distintos endpoints de una web para verificar su tiempo de respuesta y el status code que devuelve entre otras cosas. Al igual que el servicio anterior, el probing se hace a intervalos de tiempo regulares.

### k6

K6 es un servicio levantado para lograr realizar smoke tests lanzados por un cron job. El servicio se encarga de testear periodicamente el flujo principal de la aplicación y asegurarse de que la cantidad de requests hechas y sus correspondientes status codes sean los adecuados.

Como bien indica su nombre, este servicio es la puerta de entrada para las métricas provistas por k6. Es necesario ya que a diferencia de los servicios exporters, pushgateway va a ser capaz de servir métricas a prometheus de jobs efímeros o “cron”. Como este tipo de tareas puede que no existan el tiempo suficiente para ser scrappeadas, pueden pushear sus métricas a este servicio y así persistirse en un endpoint hasta actualizarse en la próxima corrida de la tarea.

### Pushgateway

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
├── k6-pycron
│ └── lib/pycron
│ └── Dockerfile
│ └── my_config.yaml
│ └── scheduler.py
│ └── web_workflow_test.js
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

Antes de comenzar, asegurarse de tener un archivo `.env` correspondiente en la raíz del directorio del repositorio con la siguiente configuración:

```yaml
##################### POSTGRES SECRETS #########################
POSTGRES_USER=<usuario-de-postgres>
POSTGRES_PASSWORD=<contraseña-de-postgres>
POSTGRES_DB=<base-de-datos-de-postgres>
POSTGRES_HOST=<host-de-postgres>
POSTGRES_PORT=<puerto-de-postgres>
##################### GRAFANA SMTP SECRETS #####################
GF_SMTP_FROM_ADDRESS=<dirección-del-remite>
GF_SMTP_FROM_NAME=<nombre-del-remite>
GR_SMTP_HOST=<nombre:puerto>
GF_SMTP_PASSWORD=<contraseña-de-aplicación>
```

### Uso

1. Navega al directorio del repositorio:
    
    ```bash
    cd promethoide
    ```
    
2. Otorga permisos de ejecución al script:
    
    ```bash
    chmod +x run.sh
    ```
    
3. Ejecuta el script:
    
    ```bash
    ./run.sh
    ```
    

Este script verificará si las imagenes necesarias para ejecutar el proyecto está construidas. Si no lo está, la construirá. Luego, ejecutará Docker Compose para iniciar los contenedores según la configuración definida en el archivo `docker-compose.yml`.


## Monitoreo en Promethoide
En el browser ir a http://localhost:3000, lo primero que observaremos es el inicio de sesión del servicio de Grafana utilizamos las credenciales admin:admin setteadas por default podremos acceder al entorno de monitoreo previamente configurado.

## Performance Testing with Locust
Este proyecto contiene un test de performancia con un con perfil de carga que fluctúa en el tiempo que simula un caso de uso normal para la Rest-api utilizando Locust. A continuación se describen los pasos para configurar y ejecutar las pruebas.

### Ejecución
```bash
docker exec -it rest-api sh
```
```bash
cd test
```
```bash 
locust -f performance_tests.py --host http://127.0.0.1:5001 --headless
```

## Comando útiles para el desarrollo
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
