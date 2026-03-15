#!/usr/bin/env python3
"""
Khohararik — TheMealDB Importer
================================
Fetches all available meals from TheMealDB free API (~300 recipes)
and imports them into KhohararikDb with properly linked ingredients.

Usage:
    python -m pip install requests pyodbc
    python import_themealdb.py

No API key required. Run after migrations have been applied.
"""

import re
import sys
import time
import pyodbc
import requests

# ─── Config ──────────────────────────────────────────────────────────────────
CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\DOTNET;"
    "DATABASE=KhohararikDb;"
    "Trusted_Connection=yes;"
)

BASE_URL = "https://www.themealdb.com/api/json/v1/1"
REQUEST_DELAY = 0.15  # seconds between API calls to be polite

# Maps MealDB ingredient names → our ingredient category
INGREDIENT_CATEGORY_HINTS = {
    # Vegetables
    "tomato": "Vegetables", "onion": "Vegetables", "garlic": "Vegetables",
    "carrot": "Vegetables", "potato": "Vegetables", "pepper": "Vegetables",
    "spinach": "Vegetables", "mushroom": "Vegetables", "zucchini": "Vegetables",
    "broccoli": "Vegetables", "cucumber": "Vegetables", "eggplant": "Vegetables",
    "celery": "Vegetables", "leek": "Vegetables", "cabbage": "Vegetables",
    "cauliflower": "Vegetables", "asparagus": "Vegetables", "peas": "Vegetables",
    "corn": "Vegetables", "lettuce": "Vegetables", "kale": "Vegetables",
    "beetroot": "Vegetables", "fennel": "Vegetables", "shallot": "Vegetables",
    "spring onion": "Vegetables", "courgette": "Vegetables", "aubergine": "Vegetables",
    "green beans": "Vegetables", "turnip": "Vegetables", "parsnip": "Vegetables",
    "artichoke": "Vegetables", "okra": "Vegetables",
    # Meat & Poultry
    "chicken": "Meat & Poultry", "beef": "Meat & Poultry", "pork": "Meat & Poultry",
    "lamb": "Meat & Poultry", "turkey": "Meat & Poultry", "duck": "Meat & Poultry",
    "bacon": "Meat & Poultry", "sausage": "Meat & Poultry", "ham": "Meat & Poultry",
    "mince": "Meat & Poultry", "veal": "Meat & Poultry", "venison": "Meat & Poultry",
    "chorizo": "Meat & Poultry", "pancetta": "Meat & Poultry", "prosciutto": "Meat & Poultry",
    "salami": "Meat & Poultry", "mortadella": "Meat & Poultry",
    # Seafood
    "salmon": "Seafood", "tuna": "Seafood", "shrimp": "Seafood", "prawn": "Seafood",
    "cod": "Seafood", "haddock": "Seafood", "tilapia": "Seafood", "crab": "Seafood",
    "lobster": "Seafood", "squid": "Seafood", "scallop": "Seafood", "anchovy": "Seafood",
    "clam": "Seafood", "mussel": "Seafood", "oyster": "Seafood", "halibut": "Seafood",
    "sea bass": "Seafood", "sardine": "Seafood", "mackerel": "Seafood",
    # Dairy & Eggs
    "egg": "Dairy & Eggs", "butter": "Dairy & Eggs", "milk": "Dairy & Eggs",
    "cheese": "Dairy & Eggs", "cream": "Dairy & Eggs", "yogurt": "Dairy & Eggs",
    "yoghurt": "Dairy & Eggs", "parmesan": "Dairy & Eggs", "mozzarella": "Dairy & Eggs",
    "cheddar": "Dairy & Eggs", "ricotta": "Dairy & Eggs", "feta": "Dairy & Eggs",
    "brie": "Dairy & Eggs", "gouda": "Dairy & Eggs", "mascarpone": "Dairy & Eggs",
    "sour cream": "Dairy & Eggs", "creme fraiche": "Dairy & Eggs",
    # Grains & Pasta
    "flour": "Grains & Pasta", "rice": "Grains & Pasta", "pasta": "Grains & Pasta",
    "spaghetti": "Grains & Pasta", "bread": "Grains & Pasta", "oats": "Grains & Pasta",
    "noodle": "Grains & Pasta", "couscous": "Grains & Pasta", "quinoa": "Grains & Pasta",
    "barley": "Grains & Pasta", "breadcrumb": "Grains & Pasta", "tortilla": "Grains & Pasta",
    "polenta": "Grains & Pasta", "semolina": "Grains & Pasta", "cornmeal": "Grains & Pasta",
    "penne": "Grains & Pasta", "rigatoni": "Grains & Pasta", "lasagne": "Grains & Pasta",
    "vermicelli": "Grains & Pasta", "rice noodle": "Grains & Pasta",
    # Legumes
    "chickpea": "Legumes", "lentil": "Legumes", "bean": "Legumes",
    "tofu": "Legumes", "tempeh": "Legumes", "edamame": "Legumes",
    "hummus": "Legumes", "split pea": "Legumes",
    # Fruits
    "lemon": "Fruits", "lime": "Fruits", "orange": "Fruits", "apple": "Fruits",
    "banana": "Fruits", "tomatoes": "Vegetables", "mango": "Fruits",
    "pineapple": "Fruits", "coconut": "Fruits", "avocado": "Fruits",
    "strawberry": "Fruits", "blueberry": "Fruits", "raspberry": "Fruits",
    "peach": "Fruits", "plum": "Fruits", "grape": "Fruits", "cherry": "Fruits",
    "cranberry": "Fruits", "pomegranate": "Fruits", "passion fruit": "Fruits",
    "kiwi": "Fruits", "melon": "Fruits", "watermelon": "Fruits",
    # Herbs & Spices
    "basil": "Herbs & Spices", "oregano": "Herbs & Spices", "cumin": "Herbs & Spices",
    "paprika": "Herbs & Spices", "salt": "Herbs & Spices", "pepper": "Herbs & Spices",
    "thyme": "Herbs & Spices", "rosemary": "Herbs & Spices", "parsley": "Herbs & Spices",
    "coriander": "Herbs & Spices", "chili": "Herbs & Spices", "ginger": "Herbs & Spices",
    "turmeric": "Herbs & Spices", "cinnamon": "Herbs & Spices", "nutmeg": "Herbs & Spices",
    "cardamom": "Herbs & Spices", "cloves": "Herbs & Spices", "bay leaf": "Herbs & Spices",
    "dill": "Herbs & Spices", "tarragon": "Herbs & Spices", "chive": "Herbs & Spices",
    "sage": "Herbs & Spices", "mint": "Herbs & Spices", "fennel seed": "Herbs & Spices",
    "allspice": "Herbs & Spices", "cayenne": "Herbs & Spices", "curry": "Herbs & Spices",
    "saffron": "Herbs & Spices", "star anise": "Herbs & Spices",
    # Oils & Fats
    "oil": "Oils & Fats", "lard": "Oils & Fats", "shortening": "Oils & Fats",
    "ghee": "Oils & Fats", "sesame oil": "Oils & Fats", "coconut oil": "Oils & Fats",
    # Condiments & Sauces
    "soy sauce": "Condiments", "tomato paste": "Condiments", "mustard": "Condiments",
    "honey": "Condiments", "vinegar": "Condiments", "ketchup": "Condiments",
    "worcestershire": "Condiments", "tabasco": "Condiments", "mayonnaise": "Condiments",
    "fish sauce": "Condiments", "oyster sauce": "Condiments", "hoisin": "Condiments",
    "miso": "Condiments", "tahini": "Condiments", "harissa": "Condiments",
    "sriracha": "Condiments", "hot sauce": "Condiments", "teriyaki": "Condiments",
    "pesto": "Condiments", "salsa": "Condiments", "capers": "Condiments",
    # Nuts & Seeds
    "almond": "Nuts & Seeds", "walnut": "Nuts & Seeds", "peanut": "Nuts & Seeds",
    "cashew": "Nuts & Seeds", "pecan": "Nuts & Seeds", "pistachio": "Nuts & Seeds",
    "pine nut": "Nuts & Seeds", "sesame": "Nuts & Seeds", "sunflower seed": "Nuts & Seeds",
    "pumpkin seed": "Nuts & Seeds", "chia": "Nuts & Seeds", "flaxseed": "Nuts & Seeds",
    "hazelnut": "Nuts & Seeds", "macadamia": "Nuts & Seeds",
    # Baking
    "sugar": "Baking", "baking powder": "Baking", "baking soda": "Baking",
    "yeast": "Baking", "vanilla": "Baking", "cocoa": "Baking", "chocolate": "Baking",
    "icing sugar": "Baking", "brown sugar": "Baking", "golden syrup": "Baking",
    "maple syrup": "Baking", "molasses": "Baking", "cornstarch": "Baking",
    "gelatin": "Baking", "powdered sugar": "Baking",
    # Beverages & Liquids
    "wine": "Beverages", "beer": "Beverages", "stock": "Beverages",
    "broth": "Beverages", "water": "Beverages", "juice": "Beverages",
    "coconut milk": "Beverages", "almond milk": "Beverages",
    "whiskey": "Beverages", "rum": "Beverages", "vodka": "Beverages",
    "brandy": "Beverages", "port": "Beverages",
}

CALORIES_DEFAULTS = {
    "Vegetables": 35, "Meat & Poultry": 220, "Seafood": 150,
    "Dairy & Eggs": 120, "Grains & Pasta": 360, "Legumes": 340,
    "Fruits": 60, "Herbs & Spices": 50, "Oils & Fats": 880,
    "Condiments": 80, "Nuts & Seeds": 580, "Baking": 380,
    "Beverages": 20, "Other": 100,
}

# ─── API helpers ──────────────────────────────────────────────────────────────
def api_get(path):
    try:
        r = requests.get(BASE_URL + path, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  [WARN] API error {path}: {e}")
        return None

# ─── DB helpers ───────────────────────────────────────────────────────────────
def get_connection():
    try:
        return pyodbc.connect(CONNECTION_STRING)
    except pyodbc.Error as e:
        print(f"[ERROR] Cannot connect: {e}")
        sys.exit(1)

def ensure_category(cur, name):
    cur.execute("SELECT Id FROM Categories WHERE Name = ?", name)
    row = cur.fetchone()
    if row:
        return row[0]
    icons = {
        "Vegetables": "bi bi-flower2", "Meat & Poultry": "bi bi-droplet-fill",
        "Seafood": "bi bi-water", "Dairy & Eggs": "bi bi-egg-fill",
        "Grains & Pasta": "bi bi-grid-fill", "Legumes": "bi bi-circle-fill",
        "Fruits": "bi bi-apple", "Herbs & Spices": "bi bi-stars",
        "Oils & Fats": "bi bi-droplet", "Condiments": "bi bi-jar",
        "Nuts & Seeds": "bi bi-dot", "Baking": "bi bi-cup-hot-fill",
        "Beverages": "bi bi-cup-straw", "Other": "bi bi-box",
    }
    cur.execute(
        "INSERT INTO Categories (Name, IconClass) OUTPUT INSERTED.Id VALUES (?, ?)",
        (name, icons.get(name, "bi bi-box"))
    )
    return int(cur.fetchone()[0])

def ensure_ingredient(cur, name, category_name, cat_id_cache):
    # normalise
    name = name.strip().title()
    cur.execute("SELECT Id FROM Ingredients WHERE Name = ?", name)
    row = cur.fetchone()
    if row:
        return row[0]

    cat_name = guess_category(name)
    if cat_name not in cat_id_cache:
        cat_id_cache[cat_name] = ensure_category(cur, cat_name)
    cat_id = cat_id_cache[cat_name]
    calories = CALORIES_DEFAULTS.get(cat_name, 100)

    cur.execute(
        "INSERT INTO Ingredients (Name, CaloriesPer100g, DefaultWeight, CategoryId) "
        "OUTPUT INSERTED.Id VALUES (?, ?, ?, ?)",
        (name, calories, 100, cat_id)
    )
    return int(cur.fetchone()[0])

def guess_category(name):
    name_lower = name.lower()
    for keyword, cat in INGREDIENT_CATEGORY_HINTS.items():
        if keyword in name_lower:
            return cat
    return "Other"

def parse_weight(measure_str):
    """Convert measure string to approximate grams."""
    if not measure_str or not measure_str.strip():
        return 100
    m = measure_str.strip().lower()
    # Extract leading number
    num_match = re.match(r"([0-9]+(?:[./][0-9]+)?)", m)
    if not num_match:
        return 100
    try:
        raw = num_match.group(1)
        if "/" in raw:
            a, b = raw.split("/")
            num = float(a) / float(b)
        else:
            num = float(raw)
    except:
        return 100

    if "kg" in m:       return int(num * 1000)
    if "lb" in m:       return int(num * 453)
    if "oz" in m:       return int(num * 28)
    if "cup" in m:      return int(num * 240)
    if "tbsp" in m or "tablespoon" in m: return int(num * 15)
    if "tsp" in m or "teaspoon" in m:    return int(num * 5)
    if "ml" in m or "l" in m:            return int(num)
    if "g" in m:        return int(num)
    # Default: assume g
    return max(int(num), 1)

# ─── Main import ──────────────────────────────────────────────────────────────
def fetch_all_meal_ids():
    """Get all meal IDs by iterating every letter A-Z."""
    ids = set()
    for letter in "abcdefghijklmnopqrstuvwxyz":
        data = api_get(f"/search.php?f={letter}")
        time.sleep(REQUEST_DELAY)
        if data and data.get("meals"):
            for m in data["meals"]:
                ids.add(m["idMeal"])
    return list(ids)

def import_meal(meal, conn, cur, cat_id_cache):
    name = (meal.get("strMeal") or "").strip()[:200]
    if not name:
        return False

    # Skip if already in DB
    cur.execute("SELECT Id FROM Recipes WHERE Name = ?", name)
    if cur.fetchone():
        return False

    instructions = (meal.get("strInstructions") or "").strip()
    description = ""
    if meal.get("strCategory") and meal.get("strArea"):
        description = f"{meal['strArea']} {meal['strCategory']} recipe."
    elif meal.get("strCategory"):
        description = f"{meal['strCategory']} recipe."

    image_url = meal.get("strMealThumb") or None

    cur.execute(
        "INSERT INTO Recipes (Name, Description, Instructions, TotalCalories, ImageUrl, Servings) "
        "OUTPUT INSERTED.Id VALUES (?, ?, ?, ?, ?, ?)",
        (name, description, instructions, 0, image_url, 4)
    )
    recipe_id = int(cur.fetchone()[0])

    # Extract up to 20 ingredients (skip duplicates per recipe)
    seen_ing_ids = set()
    for i in range(1, 21):
        ing_name = (meal.get(f"strIngredient{i}") or "").strip()
        measure = (meal.get(f"strMeasure{i}") or "").strip()
        if not ing_name:
            continue
        try:
            ing_id = ensure_ingredient(cur, ing_name, None, cat_id_cache)
            if ing_id in seen_ing_ids:
                continue  # skip duplicate ingredient in same recipe
            seen_ing_ids.add(ing_id)
            weight = parse_weight(measure)
            cur.execute(
                "INSERT INTO RecipeIngredients (RecipeId, IngredientId, RequiredWeight, Unit) "
                "VALUES (?, ?, ?, 'g')",
                (recipe_id, ing_id, weight)
            )
        except Exception as e:
            print(f"    [WARN] Ingredient '{ing_name}': {e}")

    return True

def main():
    print("=" * 55)
    print("  Khohararik — TheMealDB Importer")
    print("=" * 55)

    conn = get_connection()
    cur = conn.cursor()
    print("✓ Connected to KhohararikDb")

    # Cache category ids to avoid repeated lookups
    cat_id_cache = {}
    cur.execute("SELECT Id, Name FROM Categories")
    for row in cur.fetchall():
        cat_id_cache[row[1]] = row[0]

    print("\n📡 Fetching all meal IDs from TheMealDB...")
    meal_ids = fetch_all_meal_ids()
    print(f"   Found {len(meal_ids)} meals to import\n")

    imported = 0
    skipped = 0
    errors = 0

    for idx, meal_id in enumerate(meal_ids, 1):
        data = api_get(f"/lookup.php?i={meal_id}")
        time.sleep(REQUEST_DELAY)

        if not data or not data.get("meals"):
            errors += 1
            continue

        meal = data["meals"][0]
        try:
            result = import_meal(meal, conn, cur, cat_id_cache)
            if result:
                imported += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  [ERROR] Meal {meal_id}: {e}")
            conn.rollback()
            errors += 1
            continue

        if imported % 25 == 0 and imported > 0:
            conn.commit()
            print(f"  ✓ {imported} imported, {skipped} skipped, {errors} errors")

    conn.commit()
    cur.close()
    conn.close()

    print(f"\n{'='*55}")
    print(f"  ✅ Done!")
    print(f"     Recipes imported : {imported}")
    print(f"     Skipped (exist)  : {skipped}")
    print(f"     Errors           : {errors}")
    print(f"{'='*55}")
    print("\nIngredients and categories were auto-created from meal data.")
    print("Restart the app to see all new recipes.")

if __name__ == "__main__":
    main()
