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

from fastapi.staticfiles import StaticFiles
import base64
import os
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Campus Accounting Assistant")

# Mount static directory for image serving
# Ensure static directory exists
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

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

@app.post("/expenses/add", response_model=schemas.Expense)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    return crud.create_user_expense(db=db, expense=expense)

@app.get("/expenses/query", response_model=schemas.ExpenseResponse)
def read_expenses(
    user_id: str = Query(..., description="The ID of the user to retrieve expenses for"),
    category: Optional[str] = Query(None, description="Filter by category (e.g. 餐饮, 交通)"),
    date: Optional[datetime] = Query(None, description="Filter by specific date (YYYY-MM-DD). If not provided, returns last 7 days."),
    db: Session = Depends(get_db)
):
    expenses = crud.get_expenses(
        db, 
        user_id=user_id, 
        category=category,
        target_date=date
    )
    return {"expenses": expenses}

@app.delete("/expenses/delete")
def delete_expenses(
    user_id: str = Query(..., description="The ID of the user"),
    date: Optional[datetime] = Query(None, description="Delete all expenses on this date (YYYY-MM-DD)"),
    expense_id: Optional[int] = Query(None, description="Delete a specific expense by ID"),
    db: Session = Depends(get_db)
):
    if not date and not expense_id:
        raise HTTPException(status_code=400, detail="Must provide either 'date' or 'expense_id' to delete.")
        
    count = crud.delete_expenses(db, user_id=user_id, target_date=date, expense_id=expense_id)
    
    if count == 0:
        return {"message": "No records found to delete."}
        
    return {"message": f"Deleted {count} expenses."}

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
    request: Request,
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Generates a visual report and returns a URL to the image.
    Optimized for AI Agents: Returns a URL instead of Base64 to save tokens.
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
    
    if not image_base64:
        return {"image_url": "", "message": "No data available to generate report."}

    # Save image to static directory
    # Use a unique filename or overwrite based on user_id? 
    # For agents, unique is better to avoid caching issues, but we'll use user_id + timestamp for simplicity
    filename = f"report_{user_id}_{int(datetime.now().timestamp())}.png"
    file_path = os.path.join("static", filename)
    
    try:
        image_data = base64.b64decode(image_base64)
        with open(file_path, "wb") as f:
            f.write(image_data)
            
        # Construct full URL
        # Note: In production (Cloud), this should be the public domain.
        base_url = str(request.base_url).rstrip("/")
        image_url = f"{base_url}/static/{filename}"
        
        return {
            "image_url": image_url, 
            "tips": "Agent should render this as a Markdown image: ![](" + image_url + ")"
        }
    except Exception as e:
        logger.error(f"Failed to save image: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate image file")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
