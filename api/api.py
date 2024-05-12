from fastapi import FastAPI, HTTPException
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
import os

app = FastAPI()
env_path = os.path.join(os.path.dirname(__file__),'..','.env')
load_dotenv(env_path)

def get_client():
    # Crea un pool de conexiones
    return psycopg2.connect(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database='postgres',
        host='postgres_container'
    )


def get_price():
    now = datetime.now()
    if 6 <= now.hour < 18:
        return 10
    else:
        return 15

@app.get("/price")
def price():
    return {"price": get_price()}

@app.post("/sell")
def sell(data: dict):
    patent = data["patent"]

    if not patent:
        raise HTTPException(status_code=400, detail=f"'patent' field is required in request.")

    try:
        conn = get_client()
        cur = conn.cursor()
        cur.execute("INSERT INTO entries (patent, entry_time) VALUES (%s, %s)", (patent, datetime.now()))
        conn.commit()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while inserting entry in db.")

    return {"message": "Entry registered correctly"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)