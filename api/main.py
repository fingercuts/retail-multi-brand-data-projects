from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import os
from typing import List, Optional
from pydantic import BaseModel

# Connection details
POSTGRES_USER = os.getenv("POSTGRES_USER", "retail_user")
POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD", "retail_pass")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "retail_serving")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(
    title="Retail Multi-Brand Data API",
    description="REST API for serving analytical and operational retail data",
    version="1.0.0"
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for response
class CustomerSchema(BaseModel):
    customer_id: str
    customer_name: str
    city: str
    region: str
    email_hash: Optional[str]

class SaleSchema(BaseModel):
    transaction_id: str
    date: str
    net_amount: float

@app.get("/")
def read_root():
    return {"message": "Welcome to the Retail Multi-Brand Data API", "docs": "/docs"}

@app.get("/customers", response_model=List[CustomerSchema])
def get_customers(limit: int = 10, db: Session = Depends(get_db)):
    """Retrieve a list of masked customers for general analysis."""
    result = db.execute(text(f"SELECT customer_id, customer_name, city, region, email_hash FROM dim_customers LIMIT {limit}"))
    return [dict(row._mapping) for row in result]

@app.get("/customers/{customer_id}", response_model=CustomerSchema)
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """Retrieve a specific customer's masked profile."""
    query = text("SELECT customer_id, customer_name, city, region, email_hash FROM dim_customers WHERE customer_id = :cid")
    result = db.execute(query, {"cid": customer_id}).first()
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return dict(result._mapping)

@app.get("/sales/top", response_model=List[SaleSchema])
def get_top_sales(limit: int = 5, db: Session = Depends(get_db)):
    """Retrieve top recent sales transactions."""
    query = text(f"SELECT transaction_id, CAST(date AS VARCHAR) as date, net_amount FROM fct_sales ORDER BY net_amount DESC LIMIT {limit}")
    result = db.execute(query)
    return [dict(row._mapping) for row in result]

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected" if engine.connect() else "error"}
