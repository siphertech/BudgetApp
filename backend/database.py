from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
import os
from dotenv import load_dotenv

load_dotenv()

mongo_url = os.environ.get('MONGO_URL', '')
db_name = os.environ.get('DB_NAME', 'budget_db')

if not mongo_url:
    print("WARNING: MONGO_URL environment variable not set!")
    client = None
    db = None
    # Create dummy collections that will raise errors when used
    class DummyCollection:
        def __getattr__(self, name):
            raise Exception("Database not connected. Please set MONGO_URL environment variable.")

    transactions_collection = DummyCollection()
    categories_collection = DummyCollection()
    recipes_collection = DummyCollection()
    meal_plans_collection = DummyCollection()
    shopping_list_collection = DummyCollection()
else:
    try:
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        print(f"Connected to MongoDB database: {db_name}")

        # Collections
        transactions_collection = db.transactions
        categories_collection = db.categories
        recipes_collection = db.recipes
        meal_plans_collection = db.meal_plans
        shopping_list_collection = db.shopping_list
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        client = None
        db = None
        # Create dummy collections
        class DummyCollection:
            def __getattr__(self, name):
                raise Exception(f"Database connection failed: {e}")

        transactions_collection = DummyCollection()
        categories_collection = DummyCollection()
        recipes_collection = DummyCollection()
        meal_plans_collection = DummyCollection()
        shopping_list_collection = DummyCollection()


async def init_default_categories():
    """Initialize default budget categories if none exist"""
    if db is None:
        print("Skipping default categories initialization - database not connected")
        return

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
    if client:
        client.close()