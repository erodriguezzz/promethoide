import os
import random
from locust import HttpUser, TaskSet, task, between, LoadTestShape

interpol_data_dni = ['12345678A', '87654321B', '23456789C', '34567890D', '45678901E']


def generate_valid_dni() -> str:
    # Generate a random DNI that is not in interpol database
    # We're Assuming that always will be a valid DNI
    unique_dni = f"{random.randint(10000000, 99999999)}{random.choice('ABCDEF')}"
    if unique_dni in interpol_data_dni:
        return generate_valid_dni()
    return unique_dni


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
        # Generate a random entry that is either valid or invalid
        valid_entry_data = {
            "name": "John Doe test",
            "dni": generate_valid_dni(),  # Use a DNI not in interpol to be considered valid for this entry
            "lodging": "Hotel Example",
            "declared_money": 1000.0,
            "flight_number": "AA123"
        }

        # Varying the validity by changing certain fields
        invalid_entries = [
            {"name": "Jane Smith", "dni": "12345678A", "lodging": "Hotel Example", "declared_money": 1000.0,
             "flight_number": "AA123"},  # DNI in interpol
            {"name": "Carlos Hernandez", "dni": "23456789C", "lodging": "", "declared_money": 1000.0,
             "flight_number": "AA123"},  # No lodging
            {"name": "Maria Garcia", "dni": "34567890D", "lodging": "Hotel Example", "declared_money": 100.0,
             "flight_number": "AA123"},  # Insufficient money
            {"name": "Luis Martinez", "dni": "45678901E", "lodging": "Hotel Example", "declared_money": 1000.0,
             "flight_number": "INVALID_FLIGHT"}  # Invalid flight
        ]

        is_valid = random.random() < 0.8  # 80% chance of being valid
        entry_data = valid_entry_data if is_valid else random.choice(invalid_entries)

        # Make the request
        self.client.post("/immigration", json=entry_data, name="/immigration")


class MyLocust(HttpUser):
    tasks = [ImmigrationTest]
    wait_time = between(1, 5)


# Load test shape
class LoadShape(LoadTestShape):
    """
    A simple load test shape class that increases users linearly until a certain point, then stays constant, and finally
    """
    stages = [
        {"duration": 60, "users": 5, "spawn_rate": 10},  # 5 users for 1 minute
        {"duration": 180, "users": 10, "spawn_rate": 10},  # 10 users for 2 minutes
        {"duration": 300, "users": 7, "spawn_rate": 10},  # 7 users for 2 minutes
        {"duration": 420, "users": 15, "spawn_rate": 10},  # 15 users for 2 minutes
        {"duration": 480, "users": 20, "spawn_rate": 10},  # 20 users for 1 minute
        {"duration": 540, "users": 10, "spawn_rate": 10},  # 10 users for 1 minute
        {"duration": 660, "users": 15, "spawn_rate": 10},  # 15 users for 2 minute
        {"duration": 720, "users": 10, "spawn_rate": 10},  # 10 users for 1 minute
        {"duration": 780, "users": 5, "spawn_rate": 10},  # 5 users for 1 minute
        {"duration": 840, "users": 0, "spawn_rate": 0},  # No users for 1 minute
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data
        return None
