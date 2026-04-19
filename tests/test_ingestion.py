import pytest
from scripts.contracts import CustomerContract, SalesContract
from pydantic import ValidationError

def test_customer_contract_valid():
    """Verify that valid customer data passes the contract"""
    valid_data = {
        "customer_id": "C001",
        "name": "Jane Doe",
        "age": 30,
        "region": "West"
    }
    customer = CustomerContract(**valid_data)
    assert customer.customer_id == "C001"

def test_customer_contract_invalid_age():
    """Verify that unrealistic ages (governance rule) are caught by Pydantic"""
    invalid_data = {
        "customer_id": "C002",
        "name": "Old Entity",
        "age": 150  # Max is 120
    }
    with pytest.raises(ValidationError):
        CustomerContract(**invalid_data)

def test_sales_contract_negative_units():
    """Verify that negative transaction units are caught by Pydantic"""
    invalid_data = {
        "date": "2024-01-01",
        "customer_id": "C123",
        "product_id": "P555",
        "store_id": "S10",
        "units_sold": -5
    }
    with pytest.raises(ValidationError):
        SalesContract(**invalid_data)

def test_sales_contract_extra_fields_ignored():
    """Verify 'extra=ignore' config to ensure pipeline resilience"""
    data_with_noise = {
        "date": "2024-01-01",
        "customer_id": "C001",
        "product_id": "P001",
        "store_id": "S001",
        "random_meta": "junk_data"  # Should be ignored
    }
    sale = SalesContract(**data_with_noise)
    assert not hasattr(sale, "random_meta")
