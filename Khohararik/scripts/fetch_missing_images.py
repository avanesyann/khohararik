"""
Try to fetch images for recipes that have no ImageUrl.
- First try TheMealDB search by name
- For manually added Caucasian recipes not on TheMealDB, use Wikimedia Commons thumbnails
"""
import pyodbc, time, requests

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\DOTNET;"
    "DATABASE=KhohararikDb;"
    "Trusted_Connection=yes"
)
cur = conn.cursor()

cur.execute("SELECT Id, Name FROM Recipes WHERE ImageUrl IS NULL OR ImageUrl = '' ORDER BY Id")
missing = cur.fetchall()
print(f"{len(missing)} recipes need images")

HEADERS = {"User-Agent": "Khohararik/1.0"}

def themealdb_image(name):
    try:
        r = requests.get(f"https://www.themealdb.com/api/json/v1/1/search.php?s={requests.utils.quote(name)}", timeout=8, headers=HEADERS)
        data = r.json()
        if data.get("meals"):
            return data["meals"][0].get("strMealThumb", "")
    except Exception:
        pass
    return ""

def wikipedia_image(name):
    """Try Wikipedia API to get a thumbnail image."""
    try:
        r = requests.get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(name.replace(" ", "_")),
            timeout=8, headers=HEADERS
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("thumbnail", {}).get("source", "")
            # Upscale to 480px
            if img:
                img = img.replace("/320px-", "/480px-").replace("/200px-", "/480px-")
            return img
    except Exception:
        pass
    return ""

found = 0
for recipe_id, name in missing:
    # 1. Try TheMealDB
    img = themealdb_image(name)
    if not img:
        # 2. Try simplified name
        short = name.split("(")[0].strip()
        if short != name:
            img = themealdb_image(short)
    if not img:
        # 3. Try Wikipedia
        img = wikipedia_image(name)
    if not img:
        short = name.split("(")[0].strip()
        img = wikipedia_image(short)

    if img:
        cur.execute("UPDATE Recipes SET ImageUrl=? WHERE Id=?", img, recipe_id)
        conn.commit()
        print(f"  ✓ {name}: {img[:70]}")
        found += 1
    else:
        print(f"  ✗ {name}: no image found")
    time.sleep(0.2)

print(f"\nFound images for {found}/{len(missing)} recipes")
conn.close()
