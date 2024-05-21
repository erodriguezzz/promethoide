# Performance Testing with Locust

Este proyecto contiene un conjunto de pruebas para la Rest-api utilizando Locust. A continuación se describen los pasos para configurar y ejecutar las pruebas.

## Requisitos

- Python 3.x
- Pip (para instalar las dependencias)

## Instalación de dependencias

Primero, asegúrese de tener instaladas las dependencias necesarias. Puede instalarlas ejecutando el siguiente comando desde la carpeta `api/test`:

```sh
pip3 install locust
```

## Ejecución de la prueba con perfil de carga que fluctúa

Para ejecutar la prueba con un perfil de carga que fluctúa, utilice el siguiente comando:

```sh
locust -f performance_tests.py --host http://127.0.0.1:5001 --headless
```
### Parámetros del comando en este nuevo modo:

- `-f performance_tests.py`: El archivo de Locust que contiene las definiciones de las tareas y el perfil de carga.
- `--host http://127.0.0.1:5001`: La URL de la API que se probará (por defecto usa el puerto 5001 en localhost).
- `--headless`: Ejecuta Locust en modo sin interfaz gráfica.


### Descripción del perfil de carga `LoadShape`

El perfil de carga sigue el siguiente patrón:

- **1 minuto con 5 usuarios**
- **2 minutos con 10 usuarios**
- **2 minutos con 7 usuarios**
- **2 minutos con 15 usuarios**
- **1 minuto con 20 usuarios**
- **1 minuto con 10 usuarios**
- **2 minutos con 15 usuarios**
- **1 minuto con 10 usuarios**
- **1 minuto con 5 usuarios**
- **1 minuto con 0 usuarios (finaliza la prueba)**

El comportamiento del perfil de carga está definido en la clase `LoadShape` en el archivo `performance_tests.py` en la variable `stages`. Se puede ajustar la duración, cantidad de usuarios y tasa de generación para simular diferentes cargas en su aplicación.

```python
  stages = [
        {"duration": 60, "users": 5, "spawn_rate": 10},  
        {"duration": 180, "users": 10, "spawn_rate": 10},  
        {"duration": 300, "users": 7, "spawn_rate": 10},  
        {"duration": 420, "users": 15, "spawn_rate": 10},  
        {"duration": 480, "users": 20, "spawn_rate": 10},  
        {"duration": 540, "users": 10, "spawn_rate": 10},  
        {"duration": 660, "users": 15, "spawn_rate": 10},  
        {"duration": 720, "users": 10, "spawn_rate": 10},  
        {"duration": 780, "users": 5, "spawn_rate": 10},  
        {"duration": 840, "users": 0, "spawn_rate": 0},    
    ] 

```

## Ejecución de una prueba de estrés simple

Si prefiere ejecutar una prueba de estrés simple, debes seguir los siguientes pasos:

### Comentando la clase `LoadShape` en `performance_tests.py`

```python
# class LoadShape(LoadTestShape):
#     """
#     A simple load test shape class that mimics the behavior defined.
#     """
#     stages = [
#         {"duration": 60, "users": 5, "spawn_rate": 10},
#         {"duration": 180, "users": 10, "spawn_rate": 10},
#         {"duration": 300, "users": 7, "spawn_rate": 10},
#         {"duration": 420, "users": 15, "spawn_rate": 10},
#         {"duration": 480, "users": 20, "spawn_rate": 10},
#         {"duration": 540, "users": 10, "spawn_rate": 10},
#         {"duration": 660, "users": 15, "spawn_rate": 10},
#         {"duration": 720, "users": 10, "spawn_rate": 10},
#         {"duration": 780, "users": 5, "spawn_rate": 10},
#         {"duration": 840, "users": 0, "spawn_rate": 0},
#     ]

#     def tick(self):
#         run_time = self.get_run_time()
#         for stage in self.stages:
#             if run_time < stage["duration"]:
#                 tick_data = (stage["users"], stage["spawn_rate"])
#                 return tick_data
#         return None
```

### Ejecutando la prueba de estrés simple
Para ejecutar una prueba de estrés simple, utilice el siguiente comando:

```sh
locust -f performance_tests.py --host http://127.0.0.1:5001 --headless -u 10 -r 1 --run-time 10m
```

### Parámetros del comando:

- `-f performance_tests.py`: El archivo de Locust que contiene las definiciones de las tareas.
- `--host http://127.0.0.1:5001`: La URL de la API que se probará (por defecto usa el puerto 5001 en localhost).
- `--headless`: Ejecuta Locust en modo sin interfaz gráfica.
- `-u 10`: Número inicial de usuarios simulados.
- `-r 1`: Tasa de crecimiento de los usuarios (usuarios por segundo).
- `--run-time 10m`: El tiempo total que se debe ejecutar la prueba (en este caso, 10 minutos).

## Notas adicionales

- Asegúrese de que la API esté corriendo en la URL y puerto definidos (`http://127.0.0.1:5001` por defecto) antes de ejecutar las pruebas.
- Puede ajustar la cantidad de usuarios y la tasa de generación para simular diferentes cargas en su aplicación.
