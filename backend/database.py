from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
import os
from dotenv import load_dotenv

load_dotenv()

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Collections
transactions_collection = db.transactions
categories_collection = db.categories
recipes_collection = db.recipes
meal_plans_collection = db.meal_plans
shopping_list_collection = db.shopping_list


async def init_default_categories():
    """Initialize default budget categories if none exist"""
    default_categories = [
        {"name": "Food", "budget": 800, "color": "bg-red-500"},
        {"name": "Transport", "budget": 300, "color": "bg-blue-500"},
        {"name": "Entertainment", "budget": 200, "color": "bg-green-500"},
        {"name": "Utilities", "budget": 400, "color": "bg-yellow-500"},
        {"name": "Shopping", "budget": 300, "color": "bg-purple-500"},
        {"name": "Healthcare", "budget": 250, "color": "bg-pink-500"},
    ]
    
    for category_data in default_categories:
        existing = await categories_collection.find_one({"name": category_data["name"]})
        if not existing:
            from models import Category
            category = Category(**category_data)
            await categories_collection.insert_one(category.dict())


async def get_database():
    """Get database instance"""
    return db


async def close_database():
    """Close database connection"""
    client.close()