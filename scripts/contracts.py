from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any

class CustomerContract(BaseModel):
    """Data contract for raw customers"""
    model_config = ConfigDict(extra='ignore')
    
    customer_id: str
    name: str
    gender: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=1, le=120)
    city: Optional[str] = None
    region: Optional[str] = None

class SalesContract(BaseModel):
    """Data contract for raw sales transactions"""
    model_config = ConfigDict(extra='ignore')
    
    date: str
    customer_id: str
    product_id: str
    store_id: str
    promotion_id: Optional[str] = None
    units_sold: Optional[int] = Field(default=0, ge=0)
    total_amount: Optional[float] = Field(default=0.0, ge=0.0)
    discounted_amount: Optional[float] = Field(default=0.0, ge=0.0)

# Mapping of raw table names to their respective contracts
CONTRACTS_MAP = {
    "raw_customers": CustomerContract,
    "raw_sales": SalesContract
}
