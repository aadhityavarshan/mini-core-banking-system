from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.transaction import (
    BalanceResponse,
    DepositRequest,
    TransactionResponse,
    TransferRequest,
    TransferResponse,
    WithdrawRequest,
)
from app.services.account_service import get_account
from app.services.transaction_service import (
    deposit_funds,
    list_account_transactions,
    transfer_funds,
    withdraw_funds,
)


router = APIRouter(tags=["transactions"])


@router.post("/deposit", response_model=BalanceResponse)
def deposit_endpoint(
    request: DepositRequest,
    db: Session = Depends(get_db),
) -> BalanceResponse:
    transaction = deposit_funds(db, request.account_id, request.amount)
    account = get_account(db, request.account_id)
    return BalanceResponse(
        transaction_id=transaction.transaction_id,
        status=transaction.status,
        balance=account.balance,
    )


@router.post("/withdraw", response_model=BalanceResponse)
def withdraw_endpoint(
    request: WithdrawRequest,
    db: Session = Depends(get_db),
) -> BalanceResponse:
    transaction = withdraw_funds(db, request.account_id, request.amount)
    account = get_account(db, request.account_id)
    return BalanceResponse(
        transaction_id=transaction.transaction_id,
        status=transaction.status,
        balance=account.balance,
    )


@router.post("/transfer", response_model=TransferResponse)
def transfer_endpoint(
    request: TransferRequest,
    db: Session = Depends(get_db),
) -> TransferResponse:
    transaction = transfer_funds(
        db,
        request.from_account,
        request.to_account,
        request.amount,
    )
    return TransferResponse(
        transaction_id=transaction.transaction_id,
        status=transaction.status,
    )


@router.get("/transactions/{account_id}", response_model=list[TransactionResponse])
def list_transactions_endpoint(
    account_id: int,
    db: Session = Depends(get_db),
) -> list[TransactionResponse]:
    return list_account_transactions(db, account_id)
