from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models import (
    Recipe, RecipeCreate, RecipeUpdate,
    MealPlan, MealPlanCreate, MealPlanUpdate,
    ShoppingListItem, ShoppingListItemCreate, ShoppingListItemUpdate,
    WeeklyMealPlan
)
from database import (
    recipes_collection, meal_plans_collection, shopping_list_collection,
    get_database
)
from datetime import datetime

router = APIRouter(prefix="/api/meals", tags=["meals"])


@router.get("/dashboard")
async def get_meals_dashboard():
    """Get meals dashboard data"""
    try:
        # Get upcoming meals (next 7 days)
        upcoming_meals = []
        async for meal_plan in meal_plans_collection.find().limit(7):
            upcoming_meals.append(MealPlan(**meal_plan))
        
        # Get recipe count by type
        recipe_counts = {}
        async for recipe in recipes_collection.find():
            recipe_obj = Recipe(**recipe)
            recipe_counts[recipe_obj.type] = recipe_counts.get(recipe_obj.type, 0) + 1
        
        # Get weekly meal plan
        weekly_plan = await get_weekly_meal_plan()
        
        return {
            "upcoming_meals": upcoming_meals,
            "recipe_counts": recipe_counts,
            "weekly_plan": weekly_plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recipes", response_model=List[Recipe])
async def get_recipes():
    """Get all recipes"""
    try:
        recipes = []
        async for recipe in recipes_collection.find():
            recipes.append(Recipe(**recipe))
        return sorted(recipes, key=lambda x: x.created_at, reverse=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recipes", response_model=Recipe)
async def create_recipe(recipe: RecipeCreate):
    """Create a new recipe"""
    try:
        recipe_obj = Recipe(**recipe.dict())
        await recipes_collection.insert_one(recipe_obj.dict())
        return recipe_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recipes/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: str):
    """Get a specific recipe"""
    try:
        recipe = await recipes_collection.find_one({"id": recipe_id})
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return Recipe(**recipe)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/recipes/{recipe_id}", response_model=Recipe)
async def update_recipe(recipe_id: str, recipe_update: RecipeUpdate):
    """Update a recipe"""
    try:
        update_data = {k: v for k, v in recipe_update.dict().items() if v is not None}
        
        result = await recipes_collection.update_one(
            {"id": recipe_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        updated_recipe = await recipes_collection.find_one({"id": recipe_id})
        return Recipe(**updated_recipe)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/recipes/{recipe_id}")
async def delete_recipe(recipe_id: str):
    """Delete a recipe"""
    try:
        result = await recipes_collection.delete_one({"id": recipe_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        # Also delete associated meal plans
        await meal_plans_collection.delete_many({"recipe_id": recipe_id})
        
        return {"message": "Recipe deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meal-plans", response_model=List[MealPlan])
async def get_meal_plans():
    """Get all meal plans"""
    try:
        meal_plans = []
        async for meal_plan in meal_plans_collection.find():
            meal_plans.append(MealPlan(**meal_plan))
        return meal_plans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meal-plans", response_model=MealPlan)
async def create_meal_plan(meal_plan: MealPlanCreate):
    """Create a new meal plan"""
    try:
        # Check if recipe exists
        recipe = await recipes_collection.find_one({"id": meal_plan.recipe_id})
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        # Remove existing meal plan for same day and meal type
        await meal_plans_collection.delete_one({
            "day": meal_plan.day,
            "meal_type": meal_plan.meal_type
        })
        
        meal_plan_obj = MealPlan(**meal_plan.dict())
        await meal_plans_collection.insert_one(meal_plan_obj.dict())
        return meal_plan_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meal-plans/{meal_plan_id}", response_model=MealPlan)
async def get_meal_plan(meal_plan_id: str):
    """Get a specific meal plan"""
    try:
        meal_plan = await meal_plans_collection.find_one({"id": meal_plan_id})
        if not meal_plan:
            raise HTTPException(status_code=404, detail="Meal plan not found")
        return MealPlan(**meal_plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/meal-plans/{meal_plan_id}", response_model=MealPlan)
async def update_meal_plan(meal_plan_id: str, meal_plan_update: MealPlanUpdate):
    """Update a meal plan"""
    try:
        update_data = {k: v for k, v in meal_plan_update.dict().items() if v is not None}
        
        result = await meal_plans_collection.update_one(
            {"id": meal_plan_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Meal plan not found")
        
        updated_meal_plan = await meal_plans_collection.find_one({"id": meal_plan_id})
        return MealPlan(**updated_meal_plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/meal-plans/{meal_plan_id}")
async def delete_meal_plan(meal_plan_id: str):
    """Delete a meal plan"""
    try:
        result = await meal_plans_collection.delete_one({"id": meal_plan_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Meal plan not found")
        return {"message": "Meal plan deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_weekly_meal_plan():
    """Get weekly meal plan organized by days"""
    try:
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        meal_types = ['breakfast', 'lunch', 'dinner']
        
        weekly_plan = []
        
        for day in days:
            day_meals = []
            for meal_type in meal_types:
                meal_plan = await meal_plans_collection.find_one({
                    "day": day,
                    "meal_type": meal_type
                })
                if meal_plan:
                    day_meals.append({
                        "type": meal_type,
                        "recipe": meal_plan["recipe_name"],
                        "ingredients": meal_plan["ingredients"]
                    })
            
            weekly_plan.append({
                "day": day,
                "meals": day_meals
            })
        
        return weekly_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weekly-plan")
async def get_weekly_plan():
    """Get weekly meal plan"""
    try:
        return await get_weekly_meal_plan()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shopping-list/generate")
async def generate_shopping_list():
    """Generate shopping list from meal plans"""
    try:
        # Clear existing shopping list
        await shopping_list_collection.delete_many({})
        
        # Get all meal plans
        ingredient_count = {}
        async for meal_plan in meal_plans_collection.find():
            for ingredient in meal_plan["ingredients"]:
                ingredient_count[ingredient] = ingredient_count.get(ingredient, 0) + 1
        
        # Create shopping list items
        shopping_items = []
        for ingredient, count in ingredient_count.items():
            shopping_item = ShoppingListItem(
                item=ingredient,
                quantity=count,
                unit="pieces",
                category="Grocery"
            )
            await shopping_list_collection.insert_one(shopping_item.dict())
            shopping_items.append(shopping_item)
        
        return {
            "message": "Shopping list generated successfully",
            "items": shopping_items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/shopping-list", response_model=List[ShoppingListItem])
async def get_shopping_list():
    """Get shopping list"""
    try:
        shopping_items = []
        async for item in shopping_list_collection.find():
            shopping_items.append(ShoppingListItem(**item))
        return shopping_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shopping-list", response_model=ShoppingListItem)
async def create_shopping_list_item(item: ShoppingListItemCreate):
    """Create a new shopping list item"""
    try:
        shopping_item = ShoppingListItem(**item.dict())
        await shopping_list_collection.insert_one(shopping_item.dict())
        return shopping_item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/shopping-list/{item_id}")
async def delete_shopping_list_item(item_id: str):
    """Delete a shopping list item"""
    try:
        result = await shopping_list_collection.delete_one({"id": item_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Shopping list item not found")
        return {"message": "Shopping list item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/shopping-list")
async def clear_shopping_list():
    """Clear all shopping list items"""
    try:
        await shopping_list_collection.delete_many({})
        return {"message": "Shopping list cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))