
-- Crear tabla de interpol
CREATE TABLE interpol (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  dni VARCHAR(15) UNIQUE
);

-- Crear tabla de vuelos
CREATE TABLE flights (
  id SERIAL PRIMARY KEY,
  flight_number VARCHAR(10),
  airline VARCHAR(100),
  origin VARCHAR(100),
  destination VARCHAR(100),
  departure_date DATE,
  arrival_date DATE
);

-- Crear tabla de inmigración
CREATE TABLE immigration (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  dni VARCHAR(15) UNIQUE,
  lodging VARCHAR(255),
  declared_money DECIMAL
);


-- Interpol Data
INSERT INTO interpol (name, dni) VALUES ('John Doe', '12345678A');
INSERT INTO interpol (name, dni) VALUES ('Jane Smith', '87654321B');
INSERT INTO interpol (name, dni) VALUES ('Carlos Hernandez', '23456789C');
INSERT INTO interpol (name, dni) VALUES ('Maria Garcia', '34567890D');
INSERT INTO interpol (name, dni) VALUES ('Luis Martinez', '45678901E');

-- Flights Data
INSERT INTO flights (flight_number, airline, origin, destination, departure_date, arrival_date)
VALUES ('AA123', 'American Airlines', 'JFK', 'LAX', '2023-10-15', '2023-10-15');
INSERT INTO flights (flight_number, airline, origin, destination, departure_date, arrival_date)
VALUES ('BA456', 'British Airways', 'LHR', 'JFK', '2023-11-01', '2023-11-01');
INSERT INTO flights (flight_number, airline, origin, destination, departure_date, arrival_date)
VALUES ('AF789', 'Air France', 'CDG', 'DXB', '2023-10-20', '2023-10-20');
INSERT INTO flights (flight_number, airline, origin, destination, departure_date, arrival_date)
VALUES ('LH101', 'Lufthansa', 'FRA', 'NRT', '2023-12-05', '2023-12-06');
INSERT INTO flights (flight_number, airline, origin, destination, departure_date, arrival_date)
VALUES ('EK202', 'Emirates', 'DXB', 'JFK', '2023-09-28', '2023-09-28');

-- Immigration Data
INSERT INTO immigration (name, dni, lodging, declared_money)
VALUES ('Fernando Alonso', '56789012F', 'Hotel California', 2000.00);
INSERT INTO immigration (name, dni, lodging, declared_money)
VALUES ('Sebastian Vettel', '67890123G', 'Grand Hyatt', 3000.00);
INSERT INTO immigration (name, dni, lodging, declared_money)
VALUES ('Lewis Hamilton', '78901234H', 'Sheraton', 2500.00);
INSERT INTO immigration (name, dni, lodging, declared_money)
VALUES ('Nico Rosberg', '89012345I', 'Marriott', 1500.00);
INSERT INTO immigration (name, dni, lodging, declared_money)
VALUES ('Daniel Ricciardo', '90123456J', 'Hilton', 4000.00);