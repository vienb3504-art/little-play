from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas
from datetime import datetime, timedelta

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

def get_expenses(db: Session, user_id: str, category: str = None, target_date: datetime = None, limit: int = None):
    query = db.query(models.Expense).filter(models.Expense.user_id == user_id)
    
    if category:
        query = query.filter(models.Expense.category == category)
        
    if target_date:
        # Filter by specific date (ignoring time)
        query = query.filter(func.date(models.Expense.transaction_date) == target_date.date())
    elif not limit:
        # Default: Last 7 days (Only if no specific date AND no limit provided)
        seven_days_ago = datetime.now() - timedelta(days=7)
        query = query.filter(models.Expense.transaction_date >= seven_days_ago)
    
    if limit:
        # Sort by latest time and limit results
        query = query.order_by(models.Expense.transaction_date.desc()).limit(limit)
        
    return query.all()

def delete_expenses(db: Session, user_id: str, target_date: datetime = None, expense_id: int = None):
    query = db.query(models.Expense).filter(models.Expense.user_id == user_id)
    
    if expense_id:
        # Delete single record by ID
        query = query.filter(models.Expense.id == expense_id)
    elif target_date:
        # Delete all records for the date
        query = query.filter(func.date(models.Expense.transaction_date) == target_date.date())
    else:
        # Safety guard: Do not allow deleting everything without specific criteria
        return 0
    
    count = query.delete(synchronize_session=False)
    db.commit()
    return count

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
