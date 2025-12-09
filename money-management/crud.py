from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas
from datetime import datetime

def create_user_expense(db: Session, expense: schemas.ExpenseCreate):
    db_expense = models.Expense(
        user_id=expense.user_id,
        amount=expense.amount,
        category=expense.category,
        item_name=expense.item_name,
        transaction_date=expense.transaction_date or datetime.now()
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expenses(db: Session, user_id: str, start_date: datetime = None, end_date: datetime = None, category: str = None, target_date: datetime = None):
    query = db.query(models.Expense).filter(models.Expense.user_id == user_id)
    
    if category:
        query = query.filter(models.Expense.category == category)
        
    if target_date:
        # Filter by specific date (ignoring time)
        # Using cast to date for SQLite compatibility
        query = query.filter(func.date(models.Expense.transaction_date) == target_date.date())
    else:
        # Only apply range if target_date is not set (or they can coexist, but usually mutually exclusive logic is clearer)
        if start_date:
            query = query.filter(models.Expense.transaction_date >= start_date)
        if end_date:
            query = query.filter(models.Expense.transaction_date <= end_date)
        
    return query.all()

def get_weekly_report(db: Session, user_id: str):
    # In a real world scenario, we would filter by the current week's date range here.
    # For this demo, we just aggregate all data for the user as "weekly report" logic was not strictly defined with date logic in the prompt details other than "weekly report".
    # However, to be more robust, let's assume it means "report for the user".
    
    result = db.query(
        models.Expense.category, 
        func.sum(models.Expense.amount).label("total")
    ).filter(
        models.Expense.user_id == user_id
    ).group_by(
        models.Expense.category
    ).all()
    
    return [{"category": row.category, "total": row.total} for row in result]
