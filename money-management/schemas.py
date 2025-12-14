from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import Optional, Union

print("LOADING SCHEMAS.PY - FINAL VERSION")

class ExpenseBase(BaseModel):
    user_id: str
    amount: float
    category: str
    item_name: str
    transaction_date: Optional[Union[datetime, date]] = None

    class Config:
        populate_by_name = True
        from_attributes = True

    @field_validator('transaction_date', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v

    @field_validator('transaction_date')
    @classmethod
    def parse_transaction_date(cls, v: Optional[Union[datetime, date]]) -> Optional[datetime]:
        if v is None:
            return None
        if isinstance(v, date) and not isinstance(v, datetime):
            return datetime.combine(v, datetime.min.time())
        return v

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ExpenseResponse(BaseModel):
    expenses: list[Expense]
