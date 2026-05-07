from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


# Budget Models
class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # 'income' or 'expense'
    amount: float
    category: str
    description: str
    date: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TransactionCreate(BaseModel):
    type: str
    amount: float
    category: str
    description: str
    date: str

class TransactionUpdate(BaseModel):
    type: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None

class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    budget: float
    color: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CategoryCreate(BaseModel):
    name: str
    budget: float
    color: str

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    budget: Optional[float] = None
    color: Optional[str] = None


# Meal Planning Models
class Recipe(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # 'breakfast', 'lunch', 'dinner'
    instructions: str
    ingredients: List[str]
    servings: int
    prep_time: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RecipeCreate(BaseModel):
    name: str
    type: str
    instructions: str
    ingredients: List[str]
    servings: int
    prep_time: str

class RecipeUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    instructions: Optional[str] = None
    ingredients: Optional[List[str]] = None
    servings: Optional[int] = None
    prep_time: Optional[str] = None

class MealPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    day: str  # 'Monday', 'Tuesday', etc.
    meal_type: str  # 'breakfast', 'lunch', 'dinner'
    recipe_id: str
    recipe_name: str
    ingredients: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MealPlanCreate(BaseModel):
    day: str
    meal_type: str
    recipe_id: str
    recipe_name: str
    ingredients: List[str]

class MealPlanUpdate(BaseModel):
    day: Optional[str] = None
    meal_type: Optional[str] = None
    recipe_id: Optional[str] = None
    recipe_name: Optional[str] = None
    ingredients: Optional[List[str]] = None

class ShoppingListItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    item: str
    quantity: int
    unit: str
    category: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ShoppingListItemCreate(BaseModel):
    item: str
    quantity: int
    unit: str
    category: str

class ShoppingListItemUpdate(BaseModel):
    item: Optional[str] = None
    quantity: Optional[int] = None
    unit: Optional[str] = None
    category: Optional[str] = None


# Response Models
class BudgetSummary(BaseModel):
    total_income: float
    total_expenses: float
    balance: float
    budget_usage: float
    categories_summary: List[dict]

class WeeklyMealPlan(BaseModel):
    day: str
    meals: List[dict]

class DashboardData(BaseModel):
    budget_summary: BudgetSummary
    recent_transactions: List[Transaction]
    upcoming_meals: List[MealPlan]
    top_categories: List[dict]