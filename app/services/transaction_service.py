from datetime import datetime, timezone
from decimal import Decimal
import logging
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)


def _get_account_or_404(db: Session, account_id: int) -> Account:
    account = db.query(Account).filter(Account.account_id == account_id).first()
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    return account


def _create_transaction_record(
    *,
    account_id: int,
    transaction_type: str,
    amount: Decimal,
    status_value: str = "success",
    reference_account_id: int | None = None,
) -> Transaction:
    return Transaction(
        transaction_id=str(uuid4()),
        account_id=account_id,
        transaction_type=transaction_type,
        amount=amount.quantize(Decimal("0.01")),
        status=status_value,
        reference_account_id=reference_account_id,
        timestamp=datetime.now(timezone.utc),
    )


def deposit_funds(db: Session, account_id: int, amount: Decimal) -> Transaction:
    account = _get_account_or_404(db, account_id)
    account.balance += amount

    transaction = _create_transaction_record(
        account_id=account.account_id,
        transaction_type="deposit",
        amount=amount,
    )
    db.add(transaction)
    db.commit()
    db.refresh(account)
    db.refresh(transaction)
    logger.info("Deposited %s into account %s", transaction.amount, account.account_id)
    return transaction


def withdraw_funds(db: Session, account_id: int, amount: Decimal) -> Transaction:
    account = _get_account_or_404(db, account_id)
    if account.balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance",
        )

    account.balance -= amount
    transaction = _create_transaction_record(
        account_id=account.account_id,
        transaction_type="withdraw",
        amount=amount,
    )
    db.add(transaction)
    db.commit()
    db.refresh(account)
    db.refresh(transaction)
    logger.info("Withdrew %s from account %s", transaction.amount, account.account_id)
    return transaction


def transfer_funds(
    db: Session,
    from_account_id: int,
    to_account_id: int,
    amount: Decimal,
) -> Transaction:
    if from_account_id == to_account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source and destination accounts must be different",
        )

    source_account = _get_account_or_404(db, from_account_id)
    destination_account = _get_account_or_404(db, to_account_id)

    if source_account.balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance",
        )

    source_account.balance -= amount
    destination_account.balance += amount

    outgoing_transaction = _create_transaction_record(
        account_id=source_account.account_id,
        transaction_type="transfer_out",
        amount=amount,
        reference_account_id=destination_account.account_id,
    )
    incoming_transaction = _create_transaction_record(
        account_id=destination_account.account_id,
        transaction_type="transfer_in",
        amount=amount,
        reference_account_id=source_account.account_id,
    )

    db.add(outgoing_transaction)
    db.add(incoming_transaction)
    db.commit()
    db.refresh(outgoing_transaction)
    logger.info(
        "Transferred %s from account %s to account %s",
        amount.quantize(Decimal("0.01")),
        source_account.account_id,
        destination_account.account_id,
    )
    return outgoing_transaction


def list_account_transactions(db: Session, account_id: int) -> list[Transaction]:
    _get_account_or_404(db, account_id)
    return (
        db.query(Transaction)
        .filter(Transaction.account_id == account_id)
        .order_by(Transaction.timestamp.desc())
        .all()
    )
