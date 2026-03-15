#!/usr/bin/env python3
"""
Khohararik — Ingredient Deduplication + Image Import
=====================================================
1. Fetches the official TheMealDB ingredient list (~600 canonical names + images).
2. Normalises all ingredient names in the DB (strip adjectives like "fresh", "dried", etc.).
3. Merges duplicate/near-duplicate ingredients:
      - Updates all RecipeIngredient rows to point to the canonical ingredient
      - Deletes the redundant ingredient rows
4. Sets ingredient ImageUrl to TheMealDB's official image CDN for every matched ingredient.

Usage:
    python -m pip install requests pyodbc rapidfuzz
    python cleanup_ingredients.py
"""

import sys
import time
import re
import pyodbc
import requests

try:
    from rapidfuzz import process, fuzz
    FUZZY = True
except ImportError:
    FUZZY = False
    print("[INFO] rapidfuzz not installed — falling back to exact normalised matching.")
    print("       Run:  python -m pip install rapidfuzz  for better deduplication.")

# ─── Config ──────────────────────────────────────────────────────────────────
CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\DOTNET;"
    "DATABASE=KhohararikDb;"
    "Trusted_Connection=yes;"
)
MEALDB_INGREDIENT_LIST = "https://www.themealdb.com/api/json/v1/1/list.php?i=list"
MEALDB_IMAGE_BASE      = "https://www.themealdb.com/images/ingredients/{name}-Small.png"

# Minimum fuzzy score to consider two names the same ingredient (0-100)
FUZZY_THRESHOLD = 88

# Words that are adjectives/modifiers — stripped before comparing
STRIP_WORDS = {
    "fresh", "dried", "ground", "chopped", "sliced", "diced", "minced",
    "crushed", "grated", "shredded", "frozen", "cooked", "raw", "large",
    "small", "medium", "extra", "virgin", "light", "dark", "plain",
    "whole", "halved", "peeled", "deseeded", "boneless", "skinless",
    "unsalted", "salted", "sweet", "hot", "mild", "smoked", "canned",
    "tinned", "organic", "free-range", "natural", "ripe", "firm",
    "thick", "thin", "baby", "young", "old", "aged", "mature",
    "finely", "roughly", "lightly", "heavily", "well",
    "lean", "fat", "trimmed", "cleaned", "washed", "soft", "hard",
    "all-purpose", "self-raising", "self-rising", "plain",
    "full-fat", "low-fat", "fat-free", "reduced-fat", "skimmed",
    "uncooked", "pre-cooked", "instant", "quick", "long-grain",
    "short-grain", "basmati", "jasmine", "arborio",
    "white", "red", "green", "yellow", "black", "brown", "purple",
    "golden", "silver",
}

# Manual override merges: key is the name to REMOVE, value is the name to KEEP
# These handle cases where normalisation alone won't catch the duplicate
MANUAL_MERGES = {
    "extra virgin olive oil":   "olive oil",
    "light olive oil":          "olive oil",
    "virgin olive oil":         "olive oil",
    "vegetable stock":          "vegetable broth",
    "chicken stock":            "chicken broth",
    "beef stock":               "beef broth",
    "sea salt":                 "salt",
    "kosher salt":              "salt",
    "table salt":               "salt",
    "black pepper":             "pepper",
    "ground black pepper":      "pepper",
    "white pepper":             "pepper",
    "spring onions":            "spring onion",
    "green onion":              "spring onion",
    "scallion":                 "spring onion",
    "bell peppers":             "bell pepper",
    "red bell pepper":          "bell pepper",
    "green bell pepper":        "bell pepper",
    "yellow bell pepper":       "bell pepper",
    "cherry tomatoes":          "tomato",
    "plum tomatoes":            "tomato",
    "tinned tomatoes":          "tomato",
    "canned tomatoes":          "tomato",
    "tomatoes":                 "tomato",
    "eggs":                     "egg",
    "large eggs":               "egg",
    "egg yolks":                "egg",
    "egg whites":               "egg",
    "cloves garlic":            "garlic",
    "garlic cloves":            "garlic",
    "garlic powder":            "garlic",
    "onions":                   "onion",
    "red onion":                "onion",
    "white onion":              "onion",
    "yellow onion":             "onion",
    "mushrooms":                "mushroom",
    "button mushrooms":         "mushroom",
    "chestnut mushrooms":       "mushroom",
    "potatoes":                 "potato",
    "sweet potatoes":           "potato",
    "carrots":                  "carrot",
    "all purpose flour":        "flour",
    "plain flour":              "flour",
    "self-raising flour":       "flour",
    "bread flour":              "flour",
    "wholemeal flour":          "flour",
    "double cream":             "heavy cream",
    "whipping cream":           "heavy cream",
    "single cream":             "heavy cream",
    "creme fraiche":            "sour cream",
    "greek yogurt":             "yogurt",
    "greek yoghurt":            "yogurt",
    "natural yoghurt":          "yogurt",
    "plain yogurt":             "yogurt",
    "shrimps":                  "shrimp",
    "prawns":                   "shrimp",
    "king prawns":              "shrimp",
    "parmesan cheese":          "parmesan",
    "parmigiano":               "parmesan",
    "mozzarella cheese":        "mozzarella",
    "cheddar cheese":           "cheddar",
    "feta cheese":              "feta",
    "soy sauce":                "soy sauce",
    "dark soy sauce":           "soy sauce",
    "light soy sauce":          "soy sauce",
    "lime juice":               "lime",
    "lemon juice":              "lemon",
    "orange juice":             "orange",
    "sunflower oil":            "vegetable oil",
    "rapeseed oil":             "vegetable oil",
    "canola oil":               "vegetable oil",
    "groundnut oil":            "vegetable oil",
    "corn oil":                 "vegetable oil",
    "coriander leaves":         "coriander",
    "fresh coriander":          "coriander",
    "cilantro":                 "coriander",
    "fresh parsley":            "parsley",
    "flat-leaf parsley":        "parsley",
    "fresh basil":              "basil",
    "fresh thyme":              "thyme",
    "fresh rosemary":           "rosemary",
    "fresh mint":               "mint",
    "fresh dill":               "dill",
    "chilli":                   "chili",
    "chilli flakes":            "chili flakes",
    "red chilli":               "chili",
    "green chilli":             "chili",
    "chilli powder":            "chili powder",
    "cayenne pepper":           "cayenne",
    "smoked paprika":           "paprika",
    "sweet paprika":            "paprika",
    "hot paprika":              "paprika",
    "ground cumin":             "cumin",
    "ground coriander":         "coriander",
    "ground cinnamon":          "cinnamon",
    "ground ginger":            "ginger",
    "ground turmeric":          "turmeric",
    "ground nutmeg":            "nutmeg",
    "basmati rice":             "rice",
    "long grain rice":          "rice",
    "jasmine rice":             "rice",
    "white rice":               "rice",
    "brown rice":               "rice",
    "spaghetti pasta":          "spaghetti",
    "pasta spaghetti":          "spaghetti",
    "penne pasta":              "penne",
    "rigatoni pasta":           "rigatoni",
    "tagliatelle":              "pasta",
    "linguine":                 "pasta",
    "fettuccine":               "pasta",
    "balsamic vinegar":         "vinegar",
    "white wine vinegar":       "vinegar",
    "red wine vinegar":         "vinegar",
    "apple cider vinegar":      "vinegar",
    "white wine":               "wine",
    "red wine":                 "wine",
    "dry white wine":           "wine",
    "unsalted butter":          "butter",
    "salted butter":            "butter",
    "unsweetened cocoa":        "cocoa",
    "cocoa powder":             "cocoa",
    "dark chocolate":           "chocolate",
    "milk chocolate":           "chocolate",
    "caster sugar":             "sugar",
    "granulated sugar":         "sugar",
    "icing sugar":              "sugar",
    "brown sugar":              "sugar",
    "powdered sugar":           "sugar",
    "superfine sugar":          "sugar",
    "demerara sugar":           "sugar",
    "vanilla extract":          "vanilla",
    "vanilla essence":          "vanilla",
    "vanilla bean":             "vanilla",
    "baking soda":              "bicarbonate of soda",
    "bicarb":                   "bicarbonate of soda",
    "almond flour":             "almonds",
    "flaked almonds":           "almonds",
    "sliced almonds":           "almonds",
    "ground almonds":           "almonds",
    "peanut butter":            "peanuts",
    "sesame seeds":             "sesame",
    "sesame seed":              "sesame",
    "tahini paste":             "tahini",
    "chick peas":               "chickpeas",
    "garbanzo beans":           "chickpeas",
    "kidney beans":             "beans",
    "black beans":              "beans",
    "cannellini beans":         "beans",
    "butter beans":             "beans",
    "haricot beans":            "beans",
    "courgette":                "zucchini",
    "aubergine":                "eggplant",
    "pak choi":                 "bok choy",
    "pak choy":                 "bok choy",
    "spring greens":            "spinach",
    "baby spinach":             "spinach",
}

# ─── Helpers ─────────────────────────────────────────────────────────────────
def normalise(name: str) -> str:
    """Lowercase, strip adjectives, collapse whitespace."""
    n = name.lower().strip()
    # Remove punctuation except hyphens
    n = re.sub(r"[().,\"']", "", n)
    # Remove each strip word as a standalone word
    for w in STRIP_WORDS:
        n = re.sub(rf"\b{re.escape(w)}\b", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def get_connection():
    try:
        return pyodbc.connect(CONNECTION_STRING)
    except pyodbc.Error as e:
        print(f"[ERROR] Cannot connect: {e}")
        sys.exit(1)


# ─── Step 1: Fetch TheMealDB canonical ingredient list + images ───────────────
def fetch_mealdb_ingredients():
    print("📡 Fetching TheMealDB canonical ingredient list...")
    try:
        r = requests.get(MEALDB_INGREDIENT_LIST, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"  [WARN] Could not fetch ingredient list: {e}")
        return {}

    # Build dict: normalised_name -> (official_name, image_url)
    mapping = {}
    for item in data.get("meals", []):
        official = (item.get("strIngredient") or "").strip()
        if not official:
            continue
        image_url = MEALDB_IMAGE_BASE.format(name=official.replace(" ", "%20"))
        norm = normalise(official)
        mapping[norm] = (official, image_url)

    print(f"   ✓ {len(mapping)} canonical ingredients loaded")
    return mapping


# ─── Step 2: Load all DB ingredients ─────────────────────────────────────────
def load_db_ingredients(cur):
    cur.execute("SELECT Id, Name FROM Ingredients ORDER BY Id")
    return {row[0]: row[1] for row in cur.fetchall()}


# ─── Step 3: Build merge plan ─────────────────────────────────────────────────
def build_merge_plan(db_ingredients, mealdb_map):
    """
    Returns dict: { ingredient_id_to_delete -> ingredient_id_to_keep }
    """
    # id -> normalised name
    normed = {iid: normalise(name) for iid, name in db_ingredients.items()}

    # name -> canonical id (lowest id wins when there are true duplicates)
    canonical_by_norm: dict[str, int] = {}
    for iid, norm in sorted(normed.items()):
        if norm not in canonical_by_norm:
            canonical_by_norm[norm] = iid

    # Apply manual merges: for each rule, find source and target ids
    # name_lower -> id
    lower_to_id = {n.lower(): iid for iid, n in db_ingredients.items()}
    
    manual_plan: dict[int, int] = {}
    for src_name, tgt_name in MANUAL_MERGES.items():
        src_id = lower_to_id.get(src_name)
        tgt_id = lower_to_id.get(tgt_name)
        if src_id and tgt_id and src_id != tgt_id:
            manual_plan[src_id] = tgt_id
        # Also try normalised lookup
        if not src_id:
            src_norm = normalise(src_name)
            src_id = canonical_by_norm.get(src_norm)
        if not tgt_id:
            tgt_norm = normalise(tgt_name)
            tgt_id = canonical_by_norm.get(tgt_norm)
        if src_id and tgt_id and src_id != tgt_id:
            manual_plan[src_id] = tgt_id

    # Exact-normalised duplicates
    norm_plan: dict[int, int] = {}
    seen: dict[str, int] = {}
    for iid, norm in sorted(normed.items()):
        if norm in seen:
            norm_plan[iid] = seen[norm]
        else:
            seen[norm] = iid

    # Fuzzy duplicates
    fuzzy_plan: dict[int, int] = {}
    if FUZZY:
        remaining_ids = [iid for iid in db_ingredients if iid not in norm_plan and iid not in manual_plan]
        remaining_norms = {iid: normed[iid] for iid in remaining_ids}
        norm_list = list(remaining_norms.values())
        id_list   = list(remaining_norms.keys())
        checked = set()

        for i, (iid, norm) in enumerate(remaining_norms.items()):
            if iid in checked:
                continue
            matches = process.extract(norm, norm_list, scorer=fuzz.token_sort_ratio,
                                      score_cutoff=FUZZY_THRESHOLD, limit=10)
            for match_norm, score, idx in matches:
                match_id = id_list[idx]
                if match_id == iid or match_id in checked:
                    continue
                # keep the lower id (earlier / more complete name)
                keep, drop = (iid, match_id) if iid < match_id else (match_id, iid)
                if drop not in norm_plan and drop not in manual_plan:
                    fuzzy_plan[drop] = keep
                    checked.add(drop)
            checked.add(iid)

    # Merge all plans; manual takes priority
    combined = {**fuzzy_plan, **norm_plan, **manual_plan}

    # Resolve chains: if A->B and B->C, make A->C
    def resolve(iid, depth=0):
        if depth > 20:
            return iid
        target = combined.get(iid)
        if target is None or target == iid:
            return iid
        return resolve(target, depth + 1)

    resolved = {src: resolve(tgt) for src, tgt in combined.items() if resolve(tgt) != src}
    # Remove self-references
    resolved = {k: v for k, v in resolved.items() if k != v}

    return resolved


# ─── Step 4: Apply merges in DB ───────────────────────────────────────────────
def apply_merges(cur, merge_plan, db_ingredients):
    if not merge_plan:
        print("  No duplicates found.")
        return 0

    merged = 0
    for drop_id, keep_id in merge_plan.items():
        drop_name = db_ingredients.get(drop_id, f"#{drop_id}")
        keep_name = db_ingredients.get(keep_id, f"#{keep_id}")

        # Update RecipeIngredients — but avoid creating a duplicate PK
        # Get all recipe IDs that already use keep_id (to skip those)
        cur.execute("SELECT RecipeId FROM RecipeIngredients WHERE IngredientId = ?", keep_id)
        already_kept = {row[0] for row in cur.fetchall()}

        cur.execute("SELECT RecipeId, RequiredWeight, Unit FROM RecipeIngredients WHERE IngredientId = ?", drop_id)
        rows = cur.fetchall()

        for recipe_id, weight, unit in rows:
            if recipe_id in already_kept:
                # Recipe already has the canonical ingredient — just delete the duplicate row
                cur.execute("DELETE FROM RecipeIngredients WHERE RecipeId = ? AND IngredientId = ?",
                            recipe_id, drop_id)
            else:
                # Remap to canonical ingredient
                cur.execute(
                    "UPDATE RecipeIngredients SET IngredientId = ? WHERE RecipeId = ? AND IngredientId = ?",
                    keep_id, recipe_id, drop_id
                )
                already_kept.add(recipe_id)

        # Delete the duplicate ingredient
        cur.execute("DELETE FROM Ingredients WHERE Id = ?", drop_id)
        print(f"  ✂ merged: '{drop_name}' → '{keep_name}'")
        merged += 1

    return merged


# ─── Step 5: Assign ingredient images ─────────────────────────────────────────
def assign_images(cur, db_ingredients, mealdb_map):
    # Reload after merges
    cur.execute("SELECT Id, Name, ImageUrl FROM Ingredients")
    rows = cur.fetchall()

    updated = 0
    for iid, name, existing_url in rows:
        if existing_url:  # already has an image, skip
            continue

        norm = normalise(name)

        # Exact normalised match
        match = mealdb_map.get(norm)

        # Fuzzy match if exact fails
        if match is None and FUZZY:
            mdb_norms = list(mealdb_map.keys())
            results = process.extractOne(norm, mdb_norms, scorer=fuzz.token_sort_ratio,
                                         score_cutoff=82)
            if results:
                match = mealdb_map[results[0]]

        if match:
            official_name, image_url = match
            cur.execute("UPDATE Ingredients SET ImageUrl = ? WHERE Id = ?", image_url, iid)
            updated += 1

    return updated


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 58)
    print("  Khohararik — Ingredient Cleanup + Image Import")
    print("=" * 58)

    conn = get_connection()
    cur = conn.cursor()
    print("✓ Connected to KhohararikDb\n")

    # Step 1: TheMealDB canonical list
    mealdb_map = fetch_mealdb_ingredients()

    # Step 2: Load DB
    print("\n📋 Loading ingredients from database...")
    db_ingredients = load_db_ingredients(cur)
    print(f"   {len(db_ingredients)} ingredients found")

    # Step 3: Build merge plan
    print("\n🔍 Building deduplication plan...")
    merge_plan = build_merge_plan(db_ingredients, mealdb_map)
    print(f"   {len(merge_plan)} duplicates identified")

    # Step 4: Apply merges
    print("\n✂️  Merging duplicates...")
    merged = apply_merges(cur, merge_plan, db_ingredients)
    conn.commit()
    print(f"   ✓ {merged} ingredients merged")

    # Step 5: Assign images
    print("\n🖼️  Assigning ingredient images...")
    db_ingredients = load_db_ingredients(cur)  # reload after merges
    updated = assign_images(cur, db_ingredients, mealdb_map)
    conn.commit()
    print(f"   ✓ {updated} ingredient images assigned")

    # Final count
    cur.execute("SELECT COUNT(*) FROM Ingredients")
    final_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    print(f"\n{'=' * 58}")
    print(f"  ✅ Done!")
    print(f"     Duplicates removed   : {merged}")
    print(f"     Images assigned      : {updated}")
    print(f"     Ingredients in DB    : {final_count}")
    print(f"{'=' * 58}")
    print("\nRestart the app to see the changes.")


if __name__ == "__main__":
    main()
