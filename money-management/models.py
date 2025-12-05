from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    item_name = Column(String, nullable=False)
    transaction_date = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
