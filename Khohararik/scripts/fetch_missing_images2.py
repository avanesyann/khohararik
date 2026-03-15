"""Second pass: try alternate/simplified names for the remaining no-image recipes."""
import pyodbc, time, requests

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\DOTNET;"
    "DATABASE=KhohararikDb;"
    "Trusted_Connection=yes"
)
cur = conn.cursor()
HEADERS = {"User-Agent": "Khohararik/1.0"}

# Manual overrides for recipes we know exist on TheMealDB or Wikipedia
manual = {
    "Classic Spaghetti Bolognese": "https://www.themealdb.com/images/media/meals/sutysw1468247942.jpg",
    "Chicken Stir Fry":           "https://www.themealdb.com/images/media/meals/1529444113.jpg",
    "Creamy Mushroom Pasta":       "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Pasta-with-mushrooms.jpg/480px-Pasta-with-mushrooms.jpg",
    "Lemon Baked Salmon":          "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Salmon-raw.jpg/480px-Salmon-raw.jpg",
    "Vegetable Curry":             "https://www.themealdb.com/images/media/meals/spswqs1511558635.jpg",
    "Classic Omelette":            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Omelette.jpg/480px-Omelette.jpg",
    "Beef Tacos":                  "https://www.themealdb.com/images/media/meals/c7fdgl1687180998.jpg",
    "Honey Mustard Chicken":       "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Roast_chicken.jpg/480px-Roast_chicken.jpg",
    "Lentil Soup":                 "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Lentil_soup.jpg/480px-Lentil_soup.jpg",
    "Banana Oat Pancakes":         "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Bowl_of_oatmeal_with_maple_syrup_%2814713880491%29.jpg/480px-Bowl_of_oatmeal_with_maple_syrup_%2814713880491%29.jpg",
    "Caprese Salad":               "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Caprese_salad_at_Ristorante_La_Grotta%2C_Sorrento.jpg/480px-Caprese_salad_at_Ristorante_La_Grotta%2C_Sorrento.jpg",
    "Avocado-Free Hummus":         "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Hummus_from_The_Nile.jpg/480px-Hummus_from_The_Nile.jpg",
    "Manti (Armenian Dumplings)":  "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Manti_by_Zeynep.jpg/480px-Manti_by_Zeynep.jpg",
    "Armenian Red Bean Soup (Kchuch)": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Bean_soup.jpg/480px-Bean_soup.jpg",
    "Lavash Wrap with Herbs and Cheese": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Lavash.jpg/480px-Lavash.jpg",
    "Spas (Armenian Yoghurt Soup)": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Spas_%28soup%29.jpg/480px-Spas_%28soup%29.jpg",
    "Azerbaijani Plov (Saffron Rice)": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Azerbaijani_plov.jpg/480px-Azerbaijani_plov.jpg",
    "Lentil Soup (Mercimek Çorbası)": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Lentil_soup.jpg/480px-Lentil_soup.jpg",
}

cur.execute("SELECT Id, Name FROM Recipes WHERE ImageUrl IS NULL OR ImageUrl = ''")
missing = {name: rid for rid, name in cur.fetchall()}
print(f"{len(missing)} still missing images")

found = 0
for name, recipe_id in missing.items():
    img = manual.get(name, "")
    if img:
        cur.execute("UPDATE Recipes SET ImageUrl=? WHERE Id=?", img, recipe_id)
        conn.commit()
        print(f"  ✓ {name}")
        found += 1
    else:
        print(f"  ✗ {name}")

print(f"\nApplied {found} manual images")
cur.execute("SELECT COUNT(*) FROM Recipes WHERE ImageUrl IS NULL OR ImageUrl = ''")
print(f"Still missing: {cur.fetchone()[0]}")
conn.close()
