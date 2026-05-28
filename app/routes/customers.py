from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.account import AccountResponse
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.services.account_service import list_accounts_for_customer
from app.services.customer_service import create_customer, get_customer, list_customers


router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer_endpoint(
    customer_in: CustomerCreate,
    db: Session = Depends(get_db),
) -> CustomerResponse:
    return create_customer(db, customer_in)


@router.get("", response_model=list[CustomerResponse])
def list_customers_endpoint(db: Session = Depends(get_db)) -> list[CustomerResponse]:
    return list_customers(db)


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer_endpoint(
    customer_id: int,
    db: Session = Depends(get_db),
) -> CustomerResponse:
    customer = get_customer(db, customer_id)
    if customer is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/{customer_id}/accounts", response_model=list[AccountResponse])
def list_customer_accounts_endpoint(
    customer_id: int,
    db: Session = Depends(get_db),
) -> list[AccountResponse]:
    return list_accounts_for_customer(db, customer_id)
