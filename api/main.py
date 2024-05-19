import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncpg
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

app = FastAPI()

# Leer las variables de entorno
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
print(DATABASE_URL)

class ImmigrationEntry(BaseModel):
    name: str
    dni: str
    lodging: str
    declared_money: float
    flight_number: str

async def init_db():
    app.state.pool = await asyncpg.create_pool(DATABASE_URL)

@app.on_event("startup")
async def startup():
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.close()

@app.get("/check_dni/{dni}")
async def check_dni(dni: str):
    query = "SELECT * FROM interpol WHERE dni = $1"
    async with app.state.pool.acquire() as conn:
        record = await conn.fetchrow(query, dni)
        if record:
            raise HTTPException(status_code=400, detail="DNI found in interpol database")
        return {"message": "DNI not found in interpol database"}

@app.get("/check_flight/{flight_number}")
async def check_flight(flight_number: str):
    query = "SELECT * FROM flights WHERE flight_number = $1"
    async with app.state.pool.acquire() as conn:
        record = await conn.fetchrow(query, flight_number)
        if not record:
            raise HTTPException(status_code=404, detail="Flight not found")
        return {"message": "Flight found", "flight": dict(record)}

@app.post("/immigration_entry")
async def create_immigration_entry(entry: ImmigrationEntry):
    await check_dni(entry.dni)
    await check_flight(entry.flight_number)
    
    if not entry.lodging:
        raise HTTPException(status_code=400, detail="Lodging cannot be null")
    
    if entry.declared_money < 500:  # let's assume 500 is the minimum required amount
        raise HTTPException(status_code=400, detail="Insufficient declared money")

    query = """
    INSERT INTO immigration (name, dni, lodging, declared_money)
    VALUES ($1, $2, $3, $4)
    RETURNING id
    """
    async with app.state.pool.acquire() as conn:
        try:
            await conn.execute(query, entry.name, entry.dni, entry.lodging, entry.declared_money)
        except asyncpg.UniqueViolationError:
            raise HTTPException(status_code=400, detail="DNI already exists in immigration records")
        return {"message": "Immigration entry created successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001, reload=True)