
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
Promethoide es una red virtual desarrollada en Docker con la capacidad de monitorear hosts y servicios dentro de la misma a través de una interfaz visual de Grafana. Algunos de los servicios nativos de la red son:
## Prometheus
Este servicio es el orquestador del monitoreo de todos los otros hosts y servicios. Al estar configurado en docker que todos los contenedores forman parte de la misma red, este servicio gestiona y controla el monitoreo de las métricas de cada uno de ellos y la expone para que desde Grafana se puedan visualizar dashboards de la información recolectada.
## API Rest
La API Rest fue desarrollada en Fast API. Consta de la funcionalidad básica que utilizaría un operario de un peaje para registrar el tránsito que pasa por su cabina. La funcionalidad es muy básica y por el momento no soporta concurrencia. Podría usarse la librería `asyncpg` en lugar de `psycopg2` para que se pueda usar la librería de manera asincrónica.
## PostgreSQL
Este servicio fue levantado para almacenar la información de los operarios del peaje. Va a ser la fuente de información

### Comando útiles
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
