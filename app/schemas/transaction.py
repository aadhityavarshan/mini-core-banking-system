from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DepositRequest(BaseModel):
    account_id: int
    amount: Decimal = Field(gt=0)


class WithdrawRequest(BaseModel):
    account_id: int
    amount: Decimal = Field(gt=0)


class TransferRequest(BaseModel):
    from_account: int
    to_account: int
    amount: Decimal = Field(gt=0)


class BalanceResponse(BaseModel):
    transaction_id: str
    status: str
    balance: Decimal


class TransferResponse(BaseModel):
    transaction_id: str
    status: str


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: str
    account_id: int
    transaction_type: str
    amount: Decimal
    status: str
    reference_account_id: int | None
    timestamp: datetime
