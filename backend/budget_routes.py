from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models import (
    Transaction, TransactionCreate, TransactionUpdate,
    Category, CategoryCreate, CategoryUpdate,
    BudgetSummary, DashboardData
)
from database import (
    transactions_collection, categories_collection,
    get_database, init_default_categories
)
from datetime import datetime

router = APIRouter(prefix="/api/budget", tags=["budget"])


@router.get("/dashboard")
async def get_dashboard_data():
    """Get dashboard overview data"""
    try:
        # Get all transactions
        transactions_cursor = transactions_collection.find()
        transactions = []
        async for transaction in transactions_cursor:
            transactions.append(Transaction(**transaction))
        
        # Calculate totals
        total_income = sum(t.amount for t in transactions if t.type == 'income')
        total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
        balance = total_income - total_expenses
        budget_usage = (total_expenses / total_income * 100) if total_income > 0 else 0
        
        # Get categories with spending
        categories_cursor = categories_collection.find()
        categories_summary = []
        async for category in categories_cursor:
            cat = Category(**category)
            spent = sum(t.amount for t in transactions if t.category == cat.name and t.type == 'expense')
            categories_summary.append({
                "name": cat.name,
                "budget": cat.budget,
                "spent": spent,
                "color": cat.color,
                "percentage": (spent / cat.budget * 100) if cat.budget > 0 else 0
            })
        
        # Sort categories by spending
        top_categories = sorted(categories_summary, key=lambda x: x['spent'], reverse=True)[:3]
        
        # Recent transactions
        recent_transactions = sorted(transactions, key=lambda x: x.created_at, reverse=True)[:10]
        
        budget_summary = BudgetSummary(
            total_income=total_income,
            total_expenses=total_expenses,
            balance=balance,
            budget_usage=budget_usage,
            categories_summary=categories_summary
        )
        
        return {
            "budget_summary": budget_summary,
            "recent_transactions": recent_transactions,
            "top_categories": top_categories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions", response_model=List[Transaction])
async def get_transactions():
    """Get all transactions"""
    try:
        transactions = []
        async for transaction in transactions_collection.find():
            transactions.append(Transaction(**transaction))
        return sorted(transactions, key=lambda x: x.created_at, reverse=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate):
    """Create a new transaction"""
    try:
        transaction_obj = Transaction(**transaction.dict())
        await transactions_collection.insert_one(transaction_obj.dict())
        return transaction_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: str):
    """Get a specific transaction"""
    try:
        transaction = await transactions_collection.find_one({"id": transaction_id})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return Transaction(**transaction)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction(transaction_id: str, transaction_update: TransactionUpdate):
    """Update a transaction"""
    try:
        update_data = {k: v for k, v in transaction_update.dict().items() if v is not None}
        
        result = await transactions_collection.update_one(
            {"id": transaction_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        updated_transaction = await transactions_collection.find_one({"id": transaction_id})
        return Transaction(**updated_transaction)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str):
    """Delete a transaction"""
    try:
        result = await transactions_collection.delete_one({"id": transaction_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return {"message": "Transaction deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", response_model=List[Category])
async def get_categories():
    """Get all categories"""
    try:
        await init_default_categories()
        categories = []
        async for category in categories_collection.find():
            categories.append(Category(**category))
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/categories", response_model=Category)
async def create_category(category: CategoryCreate):
    """Create a new category"""
    try:
        category_obj = Category(**category.dict())
        await categories_collection.insert_one(category_obj.dict())
        return category_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/categories/{category_id}", response_model=Category)
async def update_category(category_id: str, category_update: CategoryUpdate):
    """Update a category"""
    try:
        update_data = {k: v for k, v in category_update.dict().items() if v is not None}
        
        result = await categories_collection.update_one(
            {"id": category_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Category not found")
        
        updated_category = await categories_collection.find_one({"id": category_id})
        return Category(**updated_category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/categories/{category_id}")
async def delete_category(category_id: str):
    """Delete a category"""
    try:
        result = await categories_collection.delete_one({"id": category_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Category not found")
        return {"message": "Category deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))