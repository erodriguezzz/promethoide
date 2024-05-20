import os
import uvicorn
import time
from fastapi import FastAPI, HTTPException, Response, Depends, Request, status
from fastapi.responses import JSONResponse
import asyncpg
from dotenv import load_dotenv
from prometheus_client import Counter, generate_latest, Histogram, CONTENT_TYPE_LATEST
from pydantic import BaseModel, Field

app = FastAPI()

# Load environment variables
load_dotenv()

# Get database connection info from environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Defining Prometheus metrics
REQUEST_COUNT = Counter("requests_total", "Total number of requests received")
ENTRY_CREATED_COUNT = Counter("entry_created_total", "Total number of immigration entries created")
DNI_FOUND_COUNT = Counter("dni_found_total", "Total number of DNIs found in interpol database")
FLIGHT_FOUND_COUNT = Counter("flight_found_total", "Total number of flights found")
REQUEST_LATENCY = Histogram("request_latency", "Latency of HTTP requests in seconds", ["method", "endpoint"])
ERROR_COUNT = Counter("error_count", "Count of errors encountered", ["endpoint", "method", "type"])


class ImmigrationEntry(BaseModel):
    name: str = Field(..., example="John Doe")
    dni: str = Field(..., example="12345678A")
    lodging: str = Field(..., example="Hotel Example")
    declared_money: float = Field(..., example=1000.0)
    flight_number: str = Field(..., example="AA1234")


async def db_pool():
    pool = await asyncpg.create_pool(DATABASE_URL)
    try:
        yield pool
    finally:
        await pool.close()


@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(DATABASE_URL)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    ERROR_COUNT.labels(request.url.path, request.method,"client_error" if exc.status_code < 500 else "server_error").inc()
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Only count this as a server error
    ERROR_COUNT.labels(request.url.path, request.method, "server_error").inc()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.middleware("http")
async def add_prometheus_metrics(request: Request, call_next):
    # Don't count metrics endpoint
    if request.url.path == "/metrics":
        return await call_next(request)

    # Count request and measure latency
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    print(f"Processing time: {process_time}")
    print(f"Request: {request.method} {request.url.path}")
    REQUEST_LATENCY.labels(request.method, request.url.path).observe(process_time)

    REQUEST_COUNT.inc()
    return response


@app.get("/dni/{dni_number}")
async def check_dni(dni_number: str, pool=Depends(db_pool)):
    query = "SELECT * FROM interpol WHERE dni = $1"
    async with pool.acquire() as conn:
        record = await conn.fetchrow(query, dni_number)
        if not record:
            raise HTTPException(status_code=404, detail="DNI not found in interpol database")
        DNI_FOUND_COUNT.inc()
        return {"message": "DNI found in interpol database", "dni": dict(record)}


@app.get("/flights/{flight_number}")
async def check_flight(flight_number: str, pool=Depends(db_pool)):
    query = "SELECT * FROM flights WHERE flight_number = $1"
    async with pool.acquire() as conn:
        record = await conn.fetchrow(query, flight_number)
        if not record:
            raise HTTPException(status_code=404, detail="Flight not found")
        FLIGHT_FOUND_COUNT.inc()
        return {"message": "Flight found", "flight": dict(record)}


@app.post("/immigration", status_code=201)
async def create_immigration_entry(entry: ImmigrationEntry, pool=Depends(db_pool)):
    # Check if DNI is in interpol database
    try:
        await check_dni(entry.dni, pool)
        raise HTTPException(status_code=400, detail="DNI found in interpol database")
    except HTTPException as e:
        if e.status_code != 404:
            raise e

    # Check if flight exists     
    await check_flight(entry.flight_number, pool)

    # Check if lodging is not null
    if not entry.lodging:
        raise HTTPException(status_code=400, detail="Lodging cannot be null")

    # Check if declared money is enough
    if entry.declared_money < 500:  # let's assume 500 is the minimum required amount
        raise HTTPException(status_code=400, detail="Insufficient declared money")

    # Insert entry into database
    query = """
    INSERT INTO immigration (name, dni, lodging, declared_money)
    VALUES ($1, $2, $3, $4)
    RETURNING id
    """
    async with pool.acquire() as conn:
        try:
            record_id = await conn.fetchval(query, entry.name, entry.dni, entry.lodging, entry.declared_money)
            ENTRY_CREATED_COUNT.inc()
            return {"message": "Immigration entry created successfully", "id": record_id}
        except asyncpg.UniqueViolationError:
            raise HTTPException(status_code=400, detail="DNI already exists in immigration records")


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return Response(content=data, status_code=200, headers={"Content-Type": CONTENT_TYPE_LATEST})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001, reload=True)
