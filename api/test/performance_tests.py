import os
import random
from locust import HttpUser, TaskSet, task, between, LoadTestShape

interpol_data_dni = ['12345678A', '87654321B', '23456789C', '34567890D', '45678901E']


class ImmigrationTest(TaskSet):

    @task
    def check_dni(self):
        # Generate a random DNI that is either valid or invalid
        valid_dni = ["12345678A", "87654321B", "23456789C", "34567890D", "45678901E"]
        invalid_dni = ["INVALID_DNI1"]
        dni = random.choice(valid_dni + invalid_dni)

        # Make the request
        self.client.get(f"/dni/{dni}", name="/dni/{dni}")

    @task
    def check_flight(self):
        # Generate a random flight number that is either valid or invalid
        valid_flights = ["AA123", "BA456", "AF789", "LH101", "EK202"]
        invalid_flights = ["INVALID_FLIGHT1"]
        flight_number = random.choice(valid_flights + invalid_flights)

        # Make the request
        self.client.get(f"/flights/{flight_number}", name="/flights/{flight_number}")

    @task
    def create_immigration_entry(self):
        entry = {
            "name": "John Doe test",
            "dni": "1234567890",
            "lodging": "Hotel Example",
            "declared_money": 1000.0,
            "flight_number": "AA123",
            "smoke": "true"
        }

        self.client.post("/immigration", json=entry, name="/immigration")


class MyLocust(HttpUser):
    tasks = [ImmigrationTest]
    wait_time = between(1, 5)


# Load test shape
class LoadShape(LoadTestShape):
    """
    A simple load test shape class that increases users linearly until a certain point, then stays constant, and finally
    """
    stages = [
        {"duration": 60, "users": 5, "spawn_rate": 10},  # 5 minute
        {"duration": 120, "users": 10, "spawn_rate": 10},  # 5 minutes
        {"duration": 120, "users": 7, "spawn_rate": 10},  # 5 minutes
        {"duration": 120, "users": 15, "spawn_rate": 10},  # 3 minutes
        {"duration": 60, "users": 20, "spawn_rate": 10},  # 2 minute
        {"duration": 60, "users": 10, "spawn_rate": 10},  # 5 minute
        {"duration": 120, "users": 15, "spawn_rate": 10},  # 3 minutes
        {"duration": 60, "users": 10, "spawn_rate": 10},  # 5 minute
        {"duration": 60, "users": 5, "spawn_rate": 10},  # 5 minute
        {"duration": 60, "users": 7, "spawn_rate": 0},  # 5 minute
    ]
    
    total_duration = sum(stage["duration"] for stage in stages)

    def tick(self):
        run_time = self.get_run_time()
        
        # Calculate the current time in the test
        current_time = run_time % self.total_duration 

        elapsed_time = 0
        for stage in self.stages:
            elapsed_time += stage["duration"]
            if current_time < elapsed_time:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data
        return None
