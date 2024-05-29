import os
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
REQUEST_COUNT = Counter("rest_api_requests_total", "Total number of requests received")
REQUEST_DNI_COUNT = Counter("rest_api_requests_dni_total", "Total number of requests to /dni")
REQUEST_FLIGHT_COUNT = Counter("rest_api_requests_flight_total", "Total number of requests to /flights")
REQUEST_ENTRY_COUNT = Counter("rest_api_requests_immigration_total", "Total number of requests to /immigration")

ENTRY_CREATED_COUNT = Counter("rest_api_entry_created_total", "Total number of immigration entries created")
DNI_FOUND_COUNT = Counter("rest_api_dni_found_total", "Total number of DNIs found in interpol database")
FLIGHT_FOUND_COUNT = Counter("rest_api_flight_found_total", "Total number of flights found")

SERVER_ERROR_COUNT = Counter("rest_api_server_error_count", "Count of errors encountered", ["endpoint"])
CLIENT_ERROR_COUNT = Counter("rest_api_client_error_count", "Count of errors encountered", ["endpoint"])

REQUEST_LATENCY = Histogram(
    "rest_api_request_latency",
    "Latency of HTTP requests in seconds",
    ["endpoint"],
    buckets=[0.050, 0.100, 0.150, 0.200, 0.250, 0.300, 0.350, 0.400, 0.450, 0.500, 0.550, 0.600, 0.650, 0.700, 0.750,
             0.800, 0.850, 0.900, 0.950, 1.0]
)


class ImmigrationEntry(BaseModel):
    name: str = Field(..., example="John Doe")
    dni: str = Field(..., example="12345678A")
    lodging: str = Field(..., example="Hotel Example")
    declared_money: float = Field(..., example=1000.0)
    flight_number: str = Field(..., example="AA1234")
    smoke: bool = Field(..., example=True)


async def db_pool():
    pool = await asyncpg.create_pool(DATABASE_URL)
    try:
        yield pool
    finally:
        await pool.close()


@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(DATABASE_URL)


# Handle HttpExceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code < 500:
        CLIENT_ERROR_COUNT.labels(request.scope['route'].name).inc()
    else:
        SERVER_ERROR_COUNT.labels(request.scope['route'].name).inc()
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# Handle general exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Only count this as a server error
    SERVER_ERROR_COUNT.labels(request.scope['route'].name).inc()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.middleware("http")
async def add_prometheus_metrics(request: Request, call_next):
    # Don't count metrics endpoint
    if request.url.path == "/metrics" or request.url.path == "/delay":
        return await call_next(request)
    
    if request.method == "POST":
        try:
            body = await request.json()
            immigration_entry = ImmigrationEntry(**body)
            if immigration_entry.smoke:
                return await call_next(request)
        except (ValueError, TypeError):
            pass

    # Count request and measure latency
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    REQUEST_LATENCY.labels(request.scope['route'].name).observe(process_time)

    REQUEST_COUNT.inc()
    return response


@app.get("/")
async def read_root():
    return {"message": "hello world", "status": "ok"}


@app.get("/dni/{dni_number}")
async def check_dni(dni_number: str, pool=Depends(db_pool)):
    #Increment the counter
    REQUEST_DNI_COUNT.inc()
    
    query = "SELECT * FROM interpol WHERE dni = $1"
    async with pool.acquire() as conn:
        record = await conn.fetchrow(query, dni_number)
        if not record:
            raise HTTPException(status_code=404, detail="DNI not found in interpol database")
        DNI_FOUND_COUNT.inc()
        return {"message": "DNI found in interpol database", "dni": dict(record)}


@app.get("/flights/{flight_number}")
async def check_flight(flight_number: str, pool=Depends(db_pool)):
    #Increment the counter
    REQUEST_FLIGHT_COUNT.inc()
    
    query = "SELECT * FROM flights WHERE flight_number = $1"
    async with pool.acquire() as conn:
        record = await conn.fetchrow(query, flight_number)
        if not record:
            raise HTTPException(status_code=404, detail="Flight not found")
        FLIGHT_FOUND_COUNT.inc()
        return {"message": "Flight found", "flight": dict(record)}


@app.post("/immigration", status_code=201)
async def create_immigration_entry(entry: ImmigrationEntry, pool=Depends(db_pool)):
    # check if is test
    if entry.smoke:
        return {"message": "Test passed"}

    #Increment the counter
    REQUEST_ENTRY_COUNT.inc()
    
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

@app.get("/delay")
async def delay():
    time.sleep(5)
    return "Delayed"


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return Response(content=data, status_code=200, headers={"Content-Type": CONTENT_TYPE_LATEST})

