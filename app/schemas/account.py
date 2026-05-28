from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    customer_id: int
    account_type: str = Field(min_length=1, max_length=20)


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    customer_id: int
    account_type: str
    balance: Decimal
