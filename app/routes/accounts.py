from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.account import AccountCreate, AccountResponse
from app.services.account_service import create_account, get_account


router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account_endpoint(
    account_in: AccountCreate,
    db: Session = Depends(get_db),
) -> AccountResponse:
    return create_account(db, account_in)


@router.get("/{account_id}", response_model=AccountResponse)
def get_account_endpoint(
    account_id: int,
    db: Session = Depends(get_db),
) -> AccountResponse:
    account = get_account(db, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account
