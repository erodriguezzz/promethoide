
   ```bash
   docker network create mymonitoringnet
   ```


   ```bash
   docker build -t my-ubuntu-prometheus .
   ```


```bash
docker run -d --network mymonitoringnet --name ubuntu1 ubuntu-with-prometheus
docker run -d --network mymonitoringnet --name ubuntu2 ubuntu-with-prometheus
docker run -d --network mymonitoringnet --name ubuntu3 ubuntu-with-prometheus
docker run -d --network mymonitoringnet --name ubuntu4 ubuntu-with-prometheus

```
## Paso 5: Verificar la Implementación

1. **Listar los contenedores activos:**
   ```bash
   docker ps
   ```

2. **Acceder a las interfaces web de Prometheus:**
   Localiza la IP de uno de tus contenedores (por ejemplo, `ubuntu1`) y accede a la interfaz web de Prometheus en el puerto `9090` usando un navegador:
   ```bash
   docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ubuntu1
   ```

   Visita `http://<Contenedor_IP>:9090` en tu navegador.
