import os
import uvicorn
from fastapi import FastAPI, HTTPException, Response, Depends
from pydantic import BaseModel
import asyncpg
from dotenv import load_dotenv
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Leer las variables de entorno
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

app = FastAPI()

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


@app.get("/dni/{dni_number}")
async def check_dni(dni_number: str, pool=Depends(db_pool)):
    REQUEST_COUNT.inc()
    
    query = "SELECT * FROM interpol WHERE dni = $1"
    async with pool.acquire() as conn:
        record = await conn.fetchrow(query, dni_number)
        if not record:
            raise HTTPException(status_code=404, detail="DNI not found in interpol database")
        DNI_FOUND_COUNT.inc()
        return {"message": "DNI found in interpol database", "dni": dict(record)}

@app.get("/flights/{flight_number}")
async def check_flight(flight_number: str, pool=Depends(db_pool)):
    REQUEST_COUNT.inc()

    query = "SELECT * FROM flights WHERE flight_number = $1"
    async with pool.acquire() as conn:
        record = await conn.fetchrow(query, flight_number)
        if not record:
            raise HTTPException(status_code=404, detail="Flight not found")
        FLIGHT_FOUND_COUNT.inc()
        return {"message": "Flight found", "flight": dict(record)}
    

@app.post("/immigration", status_code=201)
async def create_immigration_entry(entry: ImmigrationEntry, pool=Depends(db_pool)):
    REQUEST_COUNT.inc()
    
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