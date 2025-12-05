from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ExpenseBase(BaseModel):
    user_id: str
    amount: float
    category: str
    item_name: str = Field(..., alias="item-name")
    transaction_date: Optional[datetime] = None

    class Config:
        populate_by_name = True

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
