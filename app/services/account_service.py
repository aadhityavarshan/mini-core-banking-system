from decimal import Decimal
import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.account import Account
from app.schemas.account import AccountCreate
from app.services.customer_service import get_customer

logger = logging.getLogger(__name__)


def create_account(db: Session, account_in: AccountCreate) -> Account:
    customer = get_customer(db, account_in.customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    account = Account(
        customer_id=account_in.customer_id,
        account_type=account_in.account_type.upper(),
        balance=Decimal("0.00"),
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    logger.info(
        "Created account %s for customer %s",
        account.account_id,
        account.customer_id,
    )
    return account


def get_account(db: Session, account_id: int) -> Account | None:
    return db.query(Account).filter(Account.account_id == account_id).first()


def list_accounts_for_customer(db: Session, customer_id: int) -> list[Account]:
    customer = get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return (
        db.query(Account)
        .filter(Account.customer_id == customer_id)
        .order_by(Account.account_id)
        .all()
    )
