from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

import models, schemas, crud
from database import SessionLocal, engine
import analysis_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Campus Accounting Assistant")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Exception handler for 422 errors to log body
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    logger.error(f"Validation Error: {exc}")
    logger.error(f"Request Body: {body.decode('utf-8')}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": body.decode('utf-8')},
    )

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/expenses/", response_model=schemas.Expense)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    return crud.create_user_expense(db=db, expense=expense)

@app.get("/expenses/", response_model=List[schemas.Expense])
def read_expenses(
    user_id: str = Query(..., description="The ID of the user to retrieve expenses for"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    return crud.get_expenses(db, user_id=user_id, start_date=start_date, end_date=end_date)

@app.get("/report/weekly")
def read_weekly_report(
    user_id: str = Query(..., description="The ID of the user to retrieve report for"),
    db: Session = Depends(get_db)
):
    stats = crud.get_weekly_report(db, user_id=user_id)
    total_expense = sum(item['total'] for item in stats)
    return {
        "user_id": user_id,
        "summary": stats,
        "total_expense": total_expense
    }

@app.get("/analysis/visual_report")
def get_visual_report(
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Generates a visual report (Pie Chart + Line Chart) and returns Base64 image.
    """
    # Fetch all expenses for the user (or could be filtered by date)
    expenses = crud.get_expenses(db, user_id=user_id)
    
    # Convert to format expected by analysis_service
    expense_list = []
    for e in expenses:
        expense_list.append({
            "date": e.transaction_date,
            "item": e.item_name,
            "amount": e.amount,
            "category": e.category
        })
        
    image_base64 = analysis_service.generate_visual_report(expense_list)
    return {"image_base64": image_base64}

@app.get("/analysis/toxic_prediction")
def get_toxic_prediction(
    user_id: str = Query(...),
    budget: float = Query(2000.0, description="Monthly budget target"),
    db: Session = Depends(get_db)
):
    """
    Generates a toxic prediction of month-end spending.
    """
    # Fetch expenses (analysis service filters for current month internally)
    expenses = crud.get_expenses(db, user_id=user_id)
    
    expense_list = []
    for e in expenses:
        expense_list.append({
            "date": e.transaction_date,
            "item": e.item_name,
            "amount": e.amount,
            "category": e.category
        })
        
    report = analysis_service.toxic_prediction(expense_list, budget)
    return {"report": report}