# 智能校园记账助手 (Smart Campus Accounting Assistant)

本项目是一个基于 FastAPI 构建的后端服务，旨在对接腾讯云智能体，提供支持多租户（Multi-tenancy）的记账功能。包含完整的后端 API 及一个用于测试的简易前端页面。

## 📂 项目结构

```text
.
├── database.py         # 数据库连接配置 (SQLite)
├── models.py           # SQLAlchemy 数据库模型
├── schemas.py          # Pydantic 数据校验模型
├── crud.py             # 数据库 CRUD 操作 (含用户隔离逻辑)
├── main.py             # FastAPI 路由入口 (含 CORS 配置)
├── requirements.txt    # 项目依赖
└── index.html          # 前端模拟测试页面
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
uvicorn main:app --reload --port 9090
```
服务启动后将运行在: `http://127.0.0.1:9090`

### 3. 访问测试前端

直接在浏览器中打开项目目录下的 `index.html` 文件即可。

---

## 📝 代码详解

### 1. 依赖文件 (`requirements.txt`)

```text
fastapi
uvicorn
sqlalchemy
pydantic
httpx
```

### 2. 数据库配置 (`database.py`)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

### 3. 数据模型 (`models.py`)

定义了 `Expense` 表，其中 `user_id` 是实现多租户隔离的核心字段。

```python
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)  # 核心：用户ID
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    item_name = Column(String, nullable=False)
    transaction_date = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
```

### 4. 数据校验 (`schemas.py`)

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ExpenseBase(BaseModel):
    user_id: str
    amount: float
    category: str
    item_name: str
    transaction_date: Optional[datetime] = None

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    created_at: datetime

    class Config:
        # Pydantic V2 配置 (注：V1 为 orm_mode = True)
        from_attributes = True 
```

### 5. 核心逻辑 (`crud.py`)

**关键点：** 所有查询操作均强制过滤 `user_id`，确保数据隔离。

```python
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

def get_expenses(db: Session, user_id: str, start_date: datetime = None, end_date: datetime = None):
    # 强制过滤 user_id
    query = db.query(models.Expense).filter(models.Expense.user_id == user_id)
    
    if start_date:
        query = query.filter(models.Expense.transaction_date >= start_date)
    if end_date:
        query = query.filter(models.Expense.transaction_date <= end_date)
        
    return query.all()

def get_weekly_report(db: Session, user_id: str):
    result = db.query(
        models.Expense.category, 
        func.sum(models.Expense.amount).label("total")
    ).filter(
        models.Expense.user_id == user_id  # 强制过滤 user_id
    ).group_by(
        models.Expense.category
    ).all()
    
    return [{"category": row.category, "total": row.total} for row in result]
```

### 6. API 路由 (`main.py`)

已配置 CORS 允许前端跨域调用。

```python
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

import models, schemas, crud
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Campus Accounting Assistant")

# 开启 CORS 支持前端调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    user_id: str = Query(..., description="The ID of the user"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    return crud.get_expenses(db, user_id=user_id, start_date=start_date, end_date=end_date)

@app.get("/report/weekly")
def read_weekly_report(
    user_id: str = Query(..., description="The ID of the user"),
    db: Session = Depends(get_db)
):
    stats = crud.get_weekly_report(db, user_id=user_id)
    total_expense = sum(item['total'] for item in stats)
    return {
        "user_id": user_id,
        "summary": stats,
        "total_expense": total_expense
    }
```

### 7. 前端页面 (`index.html`)

使用 Vue 3 + Tailwind CSS 构建的单页应用，支持：
- 动态切换 User ID
- 发送记账请求 (POST)
- 查看账单和报表 (GET)
- 实时显示 API 响应日志
