#!/usr/bin/env python3
"""
Khohararik Database Seeder
==========================
Seeds the KhohararikDb with data from the RecipeNLG dataset
(or a bundled sample dataset if you haven't downloaded it).

Usage:
    pip install pyodbc pandas requests
    python seed_database.py

Requirements:
    - SQL Server with (localdb)\DOTNET instance running
    - KhohararikDb already created by EF Core migrations (dotnet ef database update)
    - Python 3.8+

Dataset:
    Download RecipeNLG (https://recipenlg.cs.put.poznan.pl/) or
    use Food.com dataset from Kaggle (https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions)
    Place the CSV at: scripts/recipes.csv

    If no CSV is found, the script seeds a built-in sample of ~30 diverse recipes.
"""

import os
import sys
import json
import re
import pyodbc

# ─── Config ──────────────────────────────────────────────────────────────────
CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\DOTNET;"
    "DATABASE=KhohararikDb;"
    "Trusted_Connection=yes;"
)
MAX_RECIPES = 500       # max recipes to import from CSV
RECIPES_CSV = os.path.join(os.path.dirname(__file__), "recipes.csv")

# ─── Built-in sample data ─────────────────────────────────────────────────────
SAMPLE_CATEGORIES = [
    {"name": "Vegetables", "icon": "bi bi-flower2"},
    {"name": "Meat & Poultry", "icon": "bi bi-droplet-fill"},
    {"name": "Seafood", "icon": "bi bi-water"},
    {"name": "Dairy & Eggs", "icon": "bi bi-egg-fill"},
    {"name": "Grains & Pasta", "icon": "bi bi-grid-fill"},
    {"name": "Legumes", "icon": "bi bi-circle-fill"},
    {"name": "Fruits", "icon": "bi bi-apple"},
    {"name": "Herbs & Spices", "icon": "bi bi-stars"},
    {"name": "Oils & Fats", "icon": "bi bi-droplet"},
    {"name": "Condiments", "icon": "bi bi-jar"},
]

SAMPLE_INGREDIENTS = [
    # Vegetables
    ("Tomato", 18, 150, "Vegetables"),
    ("Onion", 40, 100, "Vegetables"),
    ("Garlic", 149, 10, "Vegetables"),
    ("Carrot", 41, 100, "Vegetables"),
    ("Potato", 77, 200, "Vegetables"),
    ("Bell Pepper", 31, 100, "Vegetables"),
    ("Spinach", 23, 80, "Vegetables"),
    ("Mushroom", 22, 100, "Vegetables"),
    ("Zucchini", 17, 200, "Vegetables"),
    ("Broccoli", 55, 150, "Vegetables"),
    ("Cucumber", 16, 100, "Vegetables"),
    ("Eggplant", 25, 200, "Vegetables"),
    # Meat
    ("Chicken Breast", 165, 200, "Meat & Poultry"),
    ("Ground Beef", 250, 200, "Meat & Poultry"),
    ("Pork Chop", 242, 200, "Meat & Poultry"),
    ("Bacon", 541, 50, "Meat & Poultry"),
    ("Lamb", 294, 200, "Meat & Poultry"),
    # Seafood
    ("Salmon", 208, 200, "Seafood"),
    ("Tuna", 144, 150, "Seafood"),
    ("Shrimp", 99, 150, "Seafood"),
    # Dairy & Eggs
    ("Egg", 155, 50, "Dairy & Eggs"),
    ("Butter", 717, 30, "Dairy & Eggs"),
    ("Milk", 61, 200, "Dairy & Eggs"),
    ("Cheddar Cheese", 402, 50, "Dairy & Eggs"),
    ("Heavy Cream", 345, 100, "Dairy & Eggs"),
    ("Greek Yogurt", 59, 150, "Dairy & Eggs"),
    # Grains
    ("All-Purpose Flour", 364, 100, "Grains & Pasta"),
    ("Rice", 365, 100, "Grains & Pasta"),
    ("Spaghetti", 371, 100, "Grains & Pasta"),
    ("Bread Crumbs", 395, 50, "Grains & Pasta"),
    ("Oats", 389, 80, "Grains & Pasta"),
    # Legumes
    ("Chickpeas", 364, 150, "Legumes"),
    ("Black Beans", 339, 150, "Legumes"),
    ("Lentils", 353, 100, "Legumes"),
    # Fruits
    ("Lemon", 29, 50, "Fruits"),
    ("Apple", 52, 180, "Fruits"),
    ("Banana", 89, 120, "Fruits"),
    # Herbs & Spices
    ("Basil", 23, 5, "Herbs & Spices"),
    ("Oregano", 265, 3, "Herbs & Spices"),
    ("Cumin", 375, 3, "Herbs & Spices"),
    ("Paprika", 282, 3, "Herbs & Spices"),
    ("Salt", 0, 5, "Herbs & Spices"),
    ("Black Pepper", 251, 2, "Herbs & Spices"),
    ("Chili Flakes", 318, 2, "Herbs & Spices"),
    ("Thyme", 101, 3, "Herbs & Spices"),
    # Oils
    ("Olive Oil", 884, 15, "Oils & Fats"),
    ("Vegetable Oil", 884, 15, "Oils & Fats"),
    # Condiments
    ("Soy Sauce", 53, 30, "Condiments"),
    ("Tomato Paste", 82, 50, "Condiments"),
    ("Mustard", 66, 20, "Condiments"),
    ("Honey", 304, 30, "Condiments"),
    ("Vinegar", 18, 20, "Condiments"),
]

SAMPLE_RECIPES = [
    {
        "name": "Classic Spaghetti Bolognese",
        "description": "A hearty Italian pasta dish with rich meat sauce.",
        "instructions": "Brown the ground beef in a large pan.\nAdd chopped onion and garlic, cook until softened.\nStir in tomato paste and diced tomatoes.\nSeason with oregano, salt, and pepper. Simmer 20 min.\nCook spaghetti al dente.\nServe sauce over pasta.",
        "calories": 620,
        "prep": 15, "cook": 30, "servings": 4,
        "ingredients": [
            ("Ground Beef", 300), ("Spaghetti", 100), ("Onion", 100),
            ("Garlic", 10), ("Tomato Paste", 50), ("Oregano", 3),
            ("Olive Oil", 15), ("Salt", 5), ("Black Pepper", 2),
        ]
    },
    {
        "name": "Greek Salad",
        "description": "Fresh Mediterranean salad with crispy vegetables.",
        "instructions": "Dice tomatoes, cucumber, and bell pepper.\nSlice onion into rings.\nCombine in a bowl.\nDrizzle with olive oil and vinegar.\nSeason with salt, oregano.",
        "calories": 180,
        "prep": 10, "cook": 0, "servings": 2,
        "ingredients": [
            ("Tomato", 200), ("Cucumber", 150), ("Bell Pepper", 80),
            ("Onion", 50), ("Olive Oil", 30), ("Vinegar", 15),
            ("Oregano", 3), ("Salt", 3),
        ]
    },
    {
        "name": "Chicken Stir Fry",
        "description": "Quick Asian-style chicken with vegetables.",
        "instructions": "Slice chicken breast thinly.\nHeat oil in a wok over high heat.\nStir-fry chicken until golden.\nAdd bell pepper, broccoli, mushrooms.\nAdd soy sauce and season.\nServe hot.",
        "calories": 380,
        "prep": 10, "cook": 15, "servings": 2,
        "ingredients": [
            ("Chicken Breast", 300), ("Bell Pepper", 100), ("Broccoli", 150),
            ("Mushroom", 100), ("Soy Sauce", 30), ("Garlic", 10),
            ("Vegetable Oil", 15), ("Black Pepper", 2),
        ]
    },
    {
        "name": "Creamy Mushroom Pasta",
        "description": "Velvety pasta with sautéed mushrooms in cream sauce.",
        "instructions": "Cook spaghetti until al dente.\nSauté mushrooms with garlic in butter.\nAdd heavy cream and reduce until thickened.\nSeason with thyme, salt, pepper.\nToss with pasta and serve.",
        "calories": 540,
        "prep": 5, "cook": 20, "servings": 2,
        "ingredients": [
            ("Spaghetti", 100), ("Mushroom", 200), ("Heavy Cream", 100),
            ("Butter", 30), ("Garlic", 10), ("Thyme", 3),
            ("Salt", 5), ("Black Pepper", 2),
        ]
    },
    {
        "name": "Lemon Baked Salmon",
        "description": "Simple and healthy baked salmon with lemon.",
        "instructions": "Preheat oven to 200°C.\nPlace salmon on baking sheet.\nDrizzle with olive oil and lemon juice.\nSeason with salt, pepper, and thyme.\nBake 15-18 minutes.",
        "calories": 310,
        "prep": 5, "cook": 18, "servings": 2,
        "ingredients": [
            ("Salmon", 300), ("Lemon", 50), ("Olive Oil", 15),
            ("Thyme", 3), ("Salt", 5), ("Black Pepper", 2),
        ]
    },
    {
        "name": "Vegetable Curry",
        "description": "Aromatic Indian-style vegetable curry.",
        "instructions": "Sauté onion and garlic in oil.\nAdd cumin, paprika, chili flakes — toast 1 min.\nAdd potato, carrot, chickpeas.\nPour in 400ml water and simmer 25 min.\nFinish with spinach, season with salt.",
        "calories": 320,
        "prep": 10, "cook": 30, "servings": 3,
        "ingredients": [
            ("Potato", 300), ("Carrot", 150), ("Chickpeas", 200),
            ("Spinach", 80), ("Onion", 100), ("Garlic", 10),
            ("Cumin", 5), ("Paprika", 5), ("Chili Flakes", 2),
            ("Olive Oil", 20), ("Salt", 5),
        ]
    },
    {
        "name": "Classic Omelette",
        "description": "Fluffy French-style omelette.",
        "instructions": "Whisk 3 eggs with salt and pepper.\nMelt butter in a non-stick pan.\nPour in eggs and stir gently.\nFold when just set.\nSlide onto plate and serve.",
        "calories": 280,
        "prep": 5, "cook": 5, "servings": 1,
        "ingredients": [
            ("Egg", 150), ("Butter", 20), ("Salt", 3), ("Black Pepper", 1),
        ]
    },
    {
        "name": "Beef Tacos",
        "description": "Spicy ground beef tacos with fresh toppings.",
        "instructions": "Brown ground beef in a skillet.\nSeason with cumin, paprika, chili flakes, salt.\nWarm tortillas or use lettuce cups.\nTop with beef, tomato, onion.",
        "calories": 450,
        "prep": 10, "cook": 15, "servings": 3,
        "ingredients": [
            ("Ground Beef", 300), ("Tomato", 100), ("Onion", 80),
            ("Cumin", 5), ("Paprika", 5), ("Chili Flakes", 3), ("Salt", 4),
        ]
    },
    {
        "name": "Honey Mustard Chicken",
        "description": "Juicy chicken glazed with honey mustard.",
        "instructions": "Mix honey and mustard together.\nCoat chicken breasts in the mixture.\nSear in olive oil until golden.\nBake at 180°C for 20 min.",
        "calories": 350,
        "prep": 5, "cook": 25, "servings": 2,
        "ingredients": [
            ("Chicken Breast", 300), ("Honey", 40), ("Mustard", 30),
            ("Olive Oil", 15), ("Salt", 4), ("Black Pepper", 2),
        ]
    },
    {
        "name": "Lentil Soup",
        "description": "Hearty, warming red lentil soup.",
        "instructions": "Sauté onion and garlic in olive oil.\nAdd cumin and paprika.\nAdd lentils and 800ml water.\nSimmer 25 minutes until soft.\nBlend partially if desired.\nSeason and serve with lemon.",
        "calories": 220,
        "prep": 10, "cook": 25, "servings": 4,
        "ingredients": [
            ("Lentils", 200), ("Onion", 100), ("Garlic", 10),
            ("Cumin", 5), ("Paprika", 5), ("Olive Oil", 20),
            ("Lemon", 30), ("Salt", 5),
        ]
    },
    {
        "name": "Banana Oat Pancakes",
        "description": "Healthy 3-ingredient banana oat pancakes.",
        "instructions": "Mash 2 bananas in a bowl.\nMix in oats and eggs.\nCook small pancakes on a buttered pan 2-3 min each side.",
        "calories": 290,
        "prep": 5, "cook": 10, "servings": 2,
        "ingredients": [
            ("Banana", 240), ("Oats", 80), ("Egg", 100), ("Butter", 15),
        ]
    },
    {
        "name": "Caprese Salad",
        "description": "Classic Italian tomato and basil salad.",
        "instructions": "Slice tomatoes.\nArrange on plate.\nDrizzle olive oil.\nScatter basil leaves.\nSeason with salt and pepper.",
        "calories": 160,
        "prep": 5, "cook": 0, "servings": 2,
        "ingredients": [
            ("Tomato", 300), ("Basil", 10), ("Olive Oil", 30),
            ("Salt", 3), ("Black Pepper", 2),
        ]
    },
    {
        "name": "Garlic Shrimp",
        "description": "Quick pan-fried shrimp in garlic butter sauce.",
        "instructions": "Melt butter in a skillet.\nAdd garlic and cook 1 min.\nAdd shrimp and cook 2-3 min per side.\nSqueeze lemon and season.\nGarnish with basil.",
        "calories": 250,
        "prep": 5, "cook": 10, "servings": 2,
        "ingredients": [
            ("Shrimp", 300), ("Garlic", 15), ("Butter", 30),
            ("Lemon", 30), ("Basil", 5), ("Salt", 3),
        ]
    },
    {
        "name": "Stuffed Bell Peppers",
        "description": "Colorful peppers stuffed with rice and beef.",
        "instructions": "Cook rice.\nBrown ground beef with onion.\nMix beef with rice, season.\nHalve peppers and fill.\nBake at 180°C for 25 min.",
        "calories": 410,
        "prep": 15, "cook": 30, "servings": 4,
        "ingredients": [
            ("Bell Pepper", 400), ("Ground Beef", 250), ("Rice", 100),
            ("Onion", 80), ("Salt", 5), ("Black Pepper", 2), ("Olive Oil", 15),
        ]
    },
    {
        "name": "Avocado-Free Hummus",
        "description": "Creamy chickpea hummus.",
        "instructions": "Blend chickpeas with olive oil.\nAdd garlic, lemon juice, cumin.\nBlend smooth.\nSeason with salt.\nServe drizzled with olive oil.",
        "calories": 180,
        "prep": 10, "cook": 0, "servings": 4,
        "ingredients": [
            ("Chickpeas", 200), ("Olive Oil", 30), ("Garlic", 10),
            ("Lemon", 40), ("Cumin", 3), ("Salt", 4),
        ]
    },
]

# ─── Database helpers ─────────────────────────────────────────────────────────
def get_connection():
    try:
        return pyodbc.connect(CONNECTION_STRING)
    except pyodbc.Error as e:
        print(f"[ERROR] Cannot connect to database: {e}")
        print("Make sure (localdb)\\DOTNET is running and KhohararikDb exists.")
        sys.exit(1)

def table_has_data(conn, table):
    row = conn.execute(f"SELECT COUNT(*) FROM [{table}]").fetchone()
    return row[0] > 0

def insert_and_get_id(cur, sql, params):
    """Execute an INSERT and return the new row ID using OUTPUT INSERTED.Id."""
    cur.execute(sql, params)
    return int(cur.fetchone()[0])

def insert_category(cur, name, icon):
    return insert_and_get_id(cur,
        "INSERT INTO Categories (Name, IconClass) OUTPUT INSERTED.Id VALUES (?, ?)",
        (name, icon))

def insert_ingredient(cur, name, cal, weight, cat_id):
    return insert_and_get_id(cur,
        "INSERT INTO Ingredients (Name, CaloriesPer100g, DefaultWeight, CategoryId) "
        "OUTPUT INSERTED.Id VALUES (?, ?, ?, ?)",
        (name, cal, weight, cat_id))

def insert_recipe(cur, r):
    return insert_and_get_id(cur,
        "INSERT INTO Recipes (Name, Description, Instructions, TotalCalories, PrepTimeMinutes, CookTimeMinutes, Servings) "
        "OUTPUT INSERTED.Id VALUES (?, ?, ?, ?, ?, ?, ?)",
        (r["name"], r.get("description"), r.get("instructions"),
         r.get("calories", 0), r.get("prep"), r.get("cook"), r.get("servings")))

def insert_recipe_ingredient(cur, recipe_id, ingredient_id, weight):
    cur.execute(
        "INSERT INTO RecipeIngredients (RecipeId, IngredientId, RequiredWeight, Unit) "
        "VALUES (?, ?, ?, 'g');",
        recipe_id, ingredient_id, weight
    )

# ─── Seed sample data ─────────────────────────────────────────────────────────
def seed_sample(conn):
    print("Seeding built-in sample data...")
    cur = conn.cursor()

    # Categories
    cat_ids = {}
    for cat in SAMPLE_CATEGORIES:
        cur.execute("SELECT Id FROM Categories WHERE Name = ?", cat["name"])
        row = cur.fetchone()
        if row:
            cat_ids[cat["name"]] = row[0]
        else:
            cat_ids[cat["name"]] = insert_category(cur, cat["name"], cat["icon"])

    # Ingredients
    ing_ids = {}
    for name, cal, weight, cat_name in SAMPLE_INGREDIENTS:
        cur.execute("SELECT Id FROM Ingredients WHERE Name = ?", name)
        row = cur.fetchone()
        if row:
            ing_ids[name] = row[0]
        else:
            ing_ids[name] = insert_ingredient(cur, name, cal, weight, cat_ids[cat_name])

    conn.commit()
    print(f"  ✓ {len(cat_ids)} categories, {len(ing_ids)} ingredients")

    # Recipes
    recipe_count = 0
    for recipe in SAMPLE_RECIPES:
        cur.execute("SELECT Id FROM Recipes WHERE Name = ?", recipe["name"])
        if cur.fetchone():
            continue
        rid = insert_recipe(cur, recipe)
        for ing_name, weight in recipe["ingredients"]:
            iid = ing_ids.get(ing_name)
            if iid:
                insert_recipe_ingredient(cur, rid, iid, weight)
        recipe_count += 1

    conn.commit()
    print(f"  ✓ {recipe_count} recipes inserted")

# ─── Import from CSV (RecipeNLG / Food.com format) ───────────────────────────
def seed_from_csv(conn):
    try:
        import pandas as pd
    except ImportError:
        print("[ERROR] pandas not installed. Run: pip install pandas")
        return False

    if not os.path.exists(RECIPES_CSV):
        return False

    print(f"Importing from CSV: {RECIPES_CSV}")
    df = pd.read_csv(RECIPES_CSV, nrows=MAX_RECIPES)

    cur = conn.cursor()

    # Ensure a default "Imported" category exists
    cur.execute("SELECT Id FROM Categories WHERE Name = 'Imported'")
    row = cur.fetchone()
    default_cat_id = row[0] if row else insert_category(cur, "Imported", "bi bi-download")
    conn.commit()

    imported = 0
    for _, row in df.iterrows():
        try:
            name = str(row.get("name", row.get("title", "Unnamed Recipe")))[:200]
            if not name.strip():
                continue

            desc = str(row.get("description", ""))[:500] if pd.notna(row.get("description", "")) else None
            instructions = str(row.get("steps", row.get("directions", "")))

            cur.execute("SELECT Id FROM Recipes WHERE Name = ?", name)
            if cur.fetchone():
                continue

            rid = insert_recipe(cur, {
                "name": name,
                "description": desc,
                "instructions": instructions,
                "calories": float(row.get("calories", 0) or 0),
            })
            imported += 1

            if imported % 50 == 0:
                conn.commit()
                print(f"  ... {imported} recipes imported")

        except Exception as e:
            print(f"  [WARN] Skipped row: {e}")
            continue

    conn.commit()
    print(f"  ✓ {imported} recipes imported from CSV")
    return True

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 50)
    print("Khohararik Database Seeder")
    print("=" * 50)

    conn = get_connection()
    print("✓ Connected to KhohararikDb")

    # Always seed categories and ingredients (sample)
    seed_sample(conn)

    # Try CSV import for extra recipes
    if not seed_from_csv(conn):
        print("\nTip: To import a large dataset, place a CSV at:")
        print(f"     {RECIPES_CSV}")
        print("     (RecipeNLG or Food.com format with 'name', 'description', 'steps' columns)")

    conn.close()
    print("\n✓ Seeding complete!")
    print("\nDefault Admin Login:")
    print("  Email   : admin@khohararik.com")
    print("  Password: Admin@123!")

if __name__ == "__main__":
    main()
