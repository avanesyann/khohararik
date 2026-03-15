"""
Add Armenian, Georgian, Russian, Ukrainian, and other Caucasian/Eastern European recipes.
Run after the main seeder.
"""

import pyodbc
import random

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\DOTNET;"
    "DATABASE=KhohararikDb;"
    "Trusted_Connection=yes"
)
cur = conn.cursor()

# ─── helpers ────────────────────────────────────────────────────────────────

def get_or_create_category(name, icon):
    cur.execute("SELECT Id FROM Categories WHERE Name=?", name)
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO Categories (Name, IconClass) OUTPUT INSERTED.Id VALUES (?,?)",
        name, icon
    )
    return int(cur.fetchone()[0])

def get_or_create_ingredient(name, calories, weight, cat_id, image_url=""):
    cur.execute("SELECT Id FROM Ingredients WHERE Name=?", name)
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO Ingredients (Name, CaloriesPer100g, DefaultWeight, CategoryId, ImageUrl) "
        "OUTPUT INSERTED.Id VALUES (?,?,?,?,?)",
        name, calories, weight, cat_id, image_url
    )
    return int(cur.fetchone()[0])

def recipe_exists(name):
    cur.execute("SELECT 1 FROM Recipes WHERE Name=?", name)
    return cur.fetchone() is not None

def add_recipe(name, description, instructions, calories, image_url, ingredient_list):
    """ingredient_list: list of (ingredient_name, calories, default_weight, category_name, icon, required_weight)"""
    if recipe_exists(name):
        print(f"  skipping (exists): {name}")
        return

    cur.execute(
        "INSERT INTO Recipes (Name, Description, Instructions, TotalCalories, ImageUrl) "
        "OUTPUT INSERTED.Id VALUES (?,?,?,?,?)",
        name, description, instructions, calories, image_url
    )
    recipe_id = int(cur.fetchone()[0])

    seen = set()
    for ing_name, ing_cal, ing_weight, cat_name, cat_icon, req_weight in ingredient_list:
        cat_id = get_or_create_category(cat_name, cat_icon)
        ing_id = get_or_create_ingredient(ing_name, ing_cal, ing_weight, cat_id)
        if ing_id in seen:
            continue
        seen.add(ing_id)
        cur.execute(
            "INSERT INTO RecipeIngredients (RecipeId, IngredientId, RequiredWeight) VALUES (?,?,?)",
            recipe_id, ing_id, req_weight
        )
    conn.commit()
    print(f"  added: {name}")


# ─── Shared category shortcuts ───────────────────────────────────────────────
VEG   = ("Vegetables",   "bi bi-leaf")
MEAT  = ("Meat",         "bi bi-egg-fried")
DAIRY = ("Dairy",        "bi bi-cup-hot")
GRAIN = ("Grains",       "bi bi-basket")
HERB  = ("Herbs & Spices","bi bi-flower1")
COND  = ("Condiments",   "bi bi-droplet-half")
LEGUM = ("Legumes",      "bi bi-circle")
NUT   = ("Nuts & Seeds", "bi bi-award")
FRUIT = ("Fruits",       "bi bi-apple")
OIL   = ("Oils & Fats",  "bi bi-droplet")
BAKE  = ("Baking",       "bi bi-cup-straw")

print("Adding Caucasian & Eastern European recipes...")

# ═══════════════════════════════════════════════════════════════════════════
# ARMENIAN RECIPES
# ═══════════════════════════════════════════════════════════════════════════

add_recipe(
    "Khorovats (Armenian BBQ)",
    "Armenian-style grilled pork or lamb skewers, marinated with onion, herbs and spices.",
    "1. Cut pork into chunks.\n2. Mix with chopped onion, salt, black pepper.\n3. Marinate overnight in the fridge.\n4. Thread onto skewers.\n5. Grill over charcoal, turning often, for 20-25 min.\n6. Serve with lavash and grilled vegetables.",
    280, "",
    [
        ("Pork",        250, 200, *MEAT,  400),
        ("Onion",        40, 100, *VEG,   200),
        ("Black Pepper",255,   5, *HERB,    5),
        ("Salt",          0,  10, *HERB,   10),
        ("Sunflower Oil",884,  30, *OIL,   30),
    ]
)

add_recipe(
    "Dolma (Armenian Stuffed Grape Leaves)",
    "Grape leaves stuffed with seasoned minced lamb and rice, simmered in broth.",
    "1. Blanch grape leaves in boiling water 2 min, drain.\n2. Mix lamb mince, rice, onion, parsley, salt, pepper, cinnamon.\n3. Place 1 tbsp filling on each leaf and roll tightly.\n4. Layer in pot; add broth to cover.\n5. Simmer covered 45 min.\n6. Serve with yoghurt.",
    210, "",
    [
        ("Grape Leaves",      40, 100, *VEG,  200),
        ("Lamb",             294, 200, *MEAT, 300),
        ("Rice",             130,  80, *GRAIN, 80),
        ("Onion",             40, 100, *VEG,  100),
        ("Parsley",           36,  20, *HERB,  20),
        ("Cinnamon",         247,   5, *HERB,   5),
        ("Black Pepper",     255,   5, *HERB,   5),
        ("Tomato Paste",      82,  30, *COND,  30),
    ]
)

add_recipe(
    "Ghapama (Armenian Stuffed Pumpkin)",
    "A festive dish — baked pumpkin filled with rice, dried fruits and nuts.",
    "1. Cut pumpkin top off and scoop seeds.\n2. Mix cooked rice, raisins, dried apricots, walnuts, honey, cinnamon.\n3. Fill pumpkin with mixture.\n4. Replace lid, bake at 180°C for 60-75 min.\n5. Serve sliced at the table.",
    240, "",
    [
        ("Pumpkin",       26, 500, *VEG,   500),
        ("Rice",         130, 150, *GRAIN, 150),
        ("Raisins",      299,  50, *FRUIT,  50),
        ("Dried Apricots",241,  50, *FRUIT,  50),
        ("Walnuts",      654,  50, *NUT,    50),
        ("Honey",        304,  40, *COND,   40),
        ("Cinnamon",     247,   5, *HERB,    5),
        ("Butter",       717,  30, *DAIRY,  30),
    ]
)

add_recipe(
    "Harissa (Armenian Wheat Porridge)",
    "Traditional Armenian slow-cooked porridge of wheat berries and chicken.",
    "1. Soak wheat berries overnight.\n2. Cook chicken until tender; shred meat.\n3. Cook soaked wheat in chicken broth on low heat 3-4 h, stirring constantly.\n4. Add shredded chicken; season with salt.\n5. Serve with butter drizzled on top.",
    320, "",
    [
        ("Wheat",        327, 200, *GRAIN, 300),
        ("Chicken",      239, 300, *MEAT,  400),
        ("Butter",       717,  40, *DAIRY,  40),
        ("Salt",           0,  10, *HERB,   10),
        ("Onion",         40, 100, *VEG,   100),
    ]
)

add_recipe(
    "Manti (Armenian Dumplings)",
    "Tiny baked lamb dumplings served with yoghurt and tomato sauce.",
    "1. Make dough from flour, water, salt; rest 30 min.\n2. Mix lamb mince, onion, salt, pepper.\n3. Roll dough thin; cut squares.\n4. Place lamb filling and pinch open-topped.\n5. Bake at 200°C 20 min until golden.\n6. Serve with yoghurt and garlic.",
    380, "",
    [
        ("Flour",        364, 300, *BAKE,  300),
        ("Lamb",         294, 250, *MEAT,  250),
        ("Onion",         40, 100, *VEG,   100),
        ("Yoghurt",       59, 100, *DAIRY, 100),
        ("Garlic",       149,  10, *VEG,   10),
        ("Butter",       717,  30, *DAIRY,  30),
        ("Tomato Paste",  82,  30, *COND,   30),
        ("Black Pepper", 255,   5, *HERB,    5),
    ]
)

add_recipe(
    "Armenian Red Bean Soup (Kchuch)",
    "Hearty Armenian stew with red kidney beans, vegetables and walnuts.",
    "1. Soak beans overnight, boil until tender.\n2. Sauté onion and garlic in oil.\n3. Add diced tomatoes, potato, carrot.\n4. Add beans; season with salt, pepper, paprika.\n5. Simmer 30 min.\n6. Stir in crushed walnuts before serving.",
    240, "",
    [
        ("Red Kidney Beans",127, 200, *LEGUM, 300),
        ("Onion",            40, 100, *VEG,   100),
        ("Garlic",          149,  10, *VEG,    10),
        ("Tomato",           18, 150, *VEG,   200),
        ("Potato",           77, 200, *VEG,   200),
        ("Carrot",           41, 100, *VEG,   100),
        ("Walnuts",         654,  50, *NUT,    50),
        ("Sunflower Oil",   884,  30, *OIL,    30),
        ("Paprika",         282,   5, *HERB,    5),
    ]
)

add_recipe(
    "Lavash Wrap with Herbs and Cheese",
    "Simple Armenian flatbread rolled with fresh herbs and white cheese.",
    "1. Lay lavash flat.\n2. Spread crumbled feta or white cheese evenly.\n3. Scatter fresh tarragon, basil, coriander, spring onion.\n4. Roll tightly and cut into pieces.\n5. Serve immediately.",
    280, "",
    [
        ("Lavash",       277, 100, *GRAIN, 100),
        ("Feta Cheese",  264, 100, *DAIRY, 100),
        ("Tarragon",      49,  10, *HERB,   10),
        ("Basil",         23,  10, *HERB,   10),
        ("Spring Onion",  32,  20, *VEG,    20),
    ]
)

add_recipe(
    "Spas (Armenian Yoghurt Soup)",
    "Creamy Armenian soup made from yoghurt, wheat and fresh herbs.",
    "1. Cook wheat in water until soft.\n2. Beat yoghurt with egg; add to wheat off heat.\n3. Return to low heat, stirring constantly until slightly thickened.\n4. Season with salt.\n5. Garnish with fried onion and dried mint.",
    180, "",
    [
        ("Yoghurt",  59, 500, *DAIRY, 500),
        ("Wheat",   327, 100, *GRAIN, 100),
        ("Egg",     155,  60, *DAIRY,  60),
        ("Onion",    40, 100, *VEG,   100),
        ("Dried Mint",70,  5, *HERB,    5),
        ("Butter",  717,  20, *DAIRY,  20),
    ]
)

# ═══════════════════════════════════════════════════════════════════════════
# GEORGIAN RECIPES
# ═══════════════════════════════════════════════════════════════════════════

add_recipe(
    "Khinkali (Georgian Soup Dumplings)",
    "Juicy Georgian spiced meat dumplings with a thick dough twist on top.",
    "1. Make stiff dough from flour, water, salt; rest 30 min.\n2. Mix minced beef and pork, onion, garlic, coriander, chilli, salt, pepper and water to make juicy filling.\n3. Roll dough, cut circles; fill and pleat tightly.\n4. Boil in salted water 12-15 min.\n5. Eat by holding the knob; bite and drink broth before eating.",
    310, "",
    [
        ("Flour",        364, 400, *BAKE,  400),
        ("Beef",         250, 200, *MEAT,  200),
        ("Pork",         250, 100, *MEAT,  100),
        ("Onion",         40, 100, *VEG,   100),
        ("Garlic",       149,  10, *VEG,    10),
        ("Coriander",     23,  10, *HERB,   10),
        ("Chilli",        40,   5, *HERB,    5),
        ("Black Pepper", 255,   5, *HERB,    5),
    ]
)

add_recipe(
    "Khachapuri (Georgian Cheese Bread)",
    "Iconic Georgian boat-shaped bread filled with melted cheese and egg.",
    "1. Make yeast dough; let rise 1 hour.\n2. Roll into oval boats; fill with crumbled sulguni cheese.\n3. Fold edges up to form boat shape.\n4. Bake 15 min at 220°C.\n5. Add egg yolk and butter to centre; bake 5 more min.\n6. Stir filling and eat immediately.",
    420, "",
    [
        ("Flour",        364, 400, *BAKE,  400),
        ("Sulguni Cheese",290, 300, *DAIRY, 300),
        ("Egg",          155,  60, *DAIRY,  60),
        ("Butter",       717,  50, *DAIRY,  50),
        ("Milk",          61, 150, *DAIRY, 150),
        ("Yeast",        325,   7, *BAKE,    7),
    ]
)

add_recipe(
    "Chakhokhbili (Georgian Chicken in Tomato Herb Sauce)",
    "Aromatic Georgian braised chicken with tomatoes, onion and fresh herbs.",
    "1. Brown chicken pieces in a dry pot.\n2. Add sliced onion; cook 10 min.\n3. Add chopped tomatoes, garlic, paprika, coriander, fenugreek.\n4. Braise covered 40 min.\n5. Finish with fresh coriander, parsley and basil.",
    260, "",
    [
        ("Chicken",      239, 600, *MEAT,  600),
        ("Tomato",        18, 400, *VEG,   400),
        ("Onion",         40, 200, *VEG,   200),
        ("Garlic",       149,  15, *VEG,    15),
        ("Coriander",     23,  15, *HERB,   15),
        ("Parsley",       36,  15, *HERB,   15),
        ("Basil",         23,  10, *HERB,   10),
        ("Paprika",      282,   5, *HERB,    5),
        ("Sunflower Oil", 884, 30, *OIL,    30),
    ]
)

add_recipe(
    "Lobiani (Georgian Bean-Filled Bread)",
    "Soft Georgian flatbread stuffed with spiced kidney beans.",
    "1. Make yeast dough; let rise 1 hour.\n2. Mash cooked kidney beans with fried onion, salt and pepper.\n3. Divide dough; press flat, add filling, seal and re-flatten.\n4. Cook on dry pan or bake 10 min each side.\n5. Brush with butter and serve hot.",
    360, "",
    [
        ("Flour",             364, 400, *BAKE,  400),
        ("Red Kidney Beans",  127, 300, *LEGUM, 300),
        ("Onion",              40, 150, *VEG,   150),
        ("Butter",            717,  40, *DAIRY,  40),
        ("Yeast",             325,   7, *BAKE,    7),
        ("Black Pepper",      255,   5, *HERB,    5),
    ]
)

add_recipe(
    "Satsivi (Georgian Chicken in Walnut Sauce)",
    "Celebratory Georgian dish — poached chicken in rich walnut and spice sauce.",
    "1. Poach whole chicken until tender; reserve broth.\n2. Blend walnuts, garlic, onion, coriander, turmeric, cayenne.\n3. Add warm broth to form sauce consistency.\n4. Slice chicken; pour sauce over and refrigerate overnight.\n5. Serve cold with bread.",
    430, "",
    [
        ("Chicken",     239, 700, *MEAT,  700),
        ("Walnuts",     654, 200, *NUT,   200),
        ("Garlic",      149,  15, *VEG,    15),
        ("Onion",        40, 100, *VEG,   100),
        ("Coriander",    23,  10, *HERB,   10),
        ("Turmeric",    312,   5, *HERB,    5),
        ("Cayenne",     318,   3, *HERB,    3),
        ("White Wine Vinegar",20,30,*COND, 30),
    ]
)

# ═══════════════════════════════════════════════════════════════════════════
# RUSSIAN RECIPES
# ═══════════════════════════════════════════════════════════════════════════

add_recipe(
    "Beef Stroganoff",
    "Classic Russian beef strips in creamy sour cream and mushroom sauce.",
    "1. Slice beef into thin strips.\n2. Sauté onion until soft; add mushrooms.\n3. Brown beef quickly in hot oil; remove.\n4. Deglaze with beef stock; add mustard and sour cream.\n5. Return beef; simmer 5 min.\n6. Serve over egg noodles.",
    380, "",
    [
        ("Beef",         250, 400, *MEAT,  400),
        ("Mushrooms",     22, 200, *VEG,   200),
        ("Onion",         40, 100, *VEG,   100),
        ("Sour Cream",   193, 150, *DAIRY, 150),
        ("Mustard",       66,  20, *COND,   20),
        ("Butter",       717,  30, *DAIRY,  30),
        ("Egg Noodles",  138, 200, *GRAIN, 200),
    ]
)

add_recipe(
    "Pelmeni (Russian Meat Dumplings)",
    "Thin-doughed Russian dumplings stuffed with minced pork and beef.",
    "1. Combine flour, eggs, water, salt into stiff dough; rest 30 min.\n2. Mix pork and beef mince with grated onion, salt, pepper.\n3. Roll dough thin; stamp circles.\n4. Fill with meat, fold and pinch.\n5. Boil in salted water 8-10 min.\n6. Serve with sour cream or butter.",
    320, "",
    [
        ("Flour",        364, 350, *BAKE,  350),
        ("Pork",         250, 150, *MEAT,  150),
        ("Beef",         250, 150, *MEAT,  150),
        ("Egg",          155,  60, *DAIRY,  60),
        ("Onion",         40, 100, *VEG,   100),
        ("Sour Cream",   193, 100, *DAIRY, 100),
        ("Black Pepper", 255,   5, *HERB,    5),
    ]
)

add_recipe(
    "Borscht (Ukrainian/Russian Beet Soup)",
    "Vibrant, hearty beet soup with cabbage, vegetables and sour cream.",
    "1. Boil beef bones for broth 1.5 h.\n2. Add potato and carrot; cook 15 min.\n3. Sauté onion, beetroot, and tomato paste in oil.\n4. Add shredded cabbage and sauté mix to pot.\n5. Season with salt, sugar, vinegar.\n6. Serve with sour cream and rye bread.",
    210, "",
    [
        ("Beet",          43, 300, *VEG,   300),
        ("Cabbage",       25, 300, *VEG,   300),
        ("Potato",        77, 200, *VEG,   200),
        ("Carrot",        41, 100, *VEG,   100),
        ("Onion",         40, 100, *VEG,   100),
        ("Beef",         250, 300, *MEAT,  300),
        ("Tomato Paste",  82,  40, *COND,   40),
        ("Sour Cream",   193, 100, *DAIRY, 100),
        ("Sunflower Oil", 884, 30, *OIL,    30),
    ]
)

add_recipe(
    "Olivier Salad (Russian Potato Salad)",
    "Russia's beloved New Year salad — potato, pickles, peas and sausage in mayo.",
    "1. Boil potato, carrot and eggs until cooked; cool and dice.\n2. Dice pickles and sausage.\n3. Mix all with canned peas and mayonnaise.\n4. Season with salt and pepper.\n5. Chill 1 hour before serving.",
    310, "",
    [
        ("Potato",     77, 300, *VEG,   300),
        ("Carrot",     41, 100, *VEG,   100),
        ("Egg",       155, 120, *DAIRY, 120),
        ("Pickle",     11, 100, *COND,  100),
        ("Peas",      81, 100, *LEGUM, 100),
        ("Sausage",   301, 150, *MEAT,  150),
        ("Mayonnaise",680, 100, *COND,  100),
    ]
)

add_recipe(
    "Shchi (Russian Cabbage Soup)",
    "Classic Russian soup with cabbage, potato and beef, slow-simmered for depth.",
    "1. Simmer beef with onion and bay leaf 1.5 h.\n2. Add potato, carrot, cook 15 min.\n3. Add shredded cabbage and tomato paste.\n4. Season with salt and pepper; simmer 20 more min.\n5. Serve with sour cream and bread.",
    190, "",
    [
        ("Cabbage",      25, 400, *VEG,   400),
        ("Potato",       77, 200, *VEG,   200),
        ("Carrot",       41, 100, *VEG,   100),
        ("Onion",        40, 100, *VEG,   100),
        ("Beef",        250, 300, *MEAT,  300),
        ("Tomato Paste", 82,  30, *COND,   30),
        ("Sour Cream",  193, 100, *DAIRY, 100),
        ("Bay Leaf",    313,   2, *HERB,    2),
    ]
)

add_recipe(
    "Solyanka (Russian Meat Soup)",
    "Rich, sour-salty Russian soup with mixed meats, pickles and olives.",
    "1. Make broth with beef.\n2. Add diced sausage, ham, smoked sausage.\n3. Add sliced pickles, tomato paste, onion.\n4. Simmer 20 min.\n5. Finish with olives, lemon slice, dill.\n6. Serve with sour cream.",
    340, "",
    [
        ("Beef",         250, 200, *MEAT,  200),
        ("Sausage",      301, 100, *MEAT,  100),
        ("Pickle",        11, 150, *COND,  150),
        ("Onion",         40, 100, *VEG,   100),
        ("Tomato Paste",  82,  40, *COND,   40),
        ("Olives",       115,  50, *COND,   50),
        ("Sour Cream",   193,  80, *DAIRY,  80),
        ("Lemon",         29,  30, *FRUIT,  30),
    ]
)

add_recipe(
    "Plov (Uzbek/Russian Rice Pilaf)",
    "Fragrant rice pilaf with lamb, carrot and aromatic spices.",
    "1. Heat oil in a kazan or heavy pot.\n2. Brown lamb; add sliced onion.\n3. Add julienned carrot; cook 10 min.\n4. Add rice; pour in hot water 2:1 ratio.\n5. Add garlic head, cumin, barberries.\n6. Cook covered on low heat 25 min without stirring.",
    400, "",
    [
        ("Lamb",       294, 400, *MEAT,  400),
        ("Rice",       130, 400, *GRAIN, 400),
        ("Carrot",      41, 300, *VEG,   300),
        ("Onion",       40, 200, *VEG,   200),
        ("Garlic",     149,  30, *VEG,    30),
        ("Cumin",      375,   5, *HERB,    5),
        ("Sunflower Oil",884, 80, *OIL,   80),
    ]
)

add_recipe(
    "Blini (Russian Crepes)",
    "Thin Russian pancakes served with sour cream, caviar or jam.",
    "1. Whisk eggs, milk, flour, sugar, salt and melted butter.\n2. Rest batter 30 min.\n3. Pour thin layer into hot buttered pan.\n4. Cook 1 min per side.\n5. Serve with sour cream, jam or smoked salmon.",
    230, "",
    [
        ("Flour",      364, 200, *BAKE,  200),
        ("Egg",        155, 120, *DAIRY, 120),
        ("Milk",        61, 400, *DAIRY, 400),
        ("Butter",     717,  50, *DAIRY,  50),
        ("Sugar",      387,  20, *BAKE,   20),
        ("Sour Cream", 193, 100, *DAIRY, 100),
    ]
)

# ═══════════════════════════════════════════════════════════════════════════
# AZERBAIJANI RECIPES
# ═══════════════════════════════════════════════════════════════════════════

add_recipe(
    "Azerbaijani Plov (Saffron Rice)",
    "Festive Azerbaijani layered rice dish with saffron, dried fruits and lamb.",
    "1. Soak rice 2 h; par-boil 7 min; drain.\n2. Melt butter in pot; layer lavash on bottom (kazmag).\n3. Add rice in layers with saffron water.\n4. Cook covered on low heat 40 min.\n5. Serve rice golden-side up with lamb and dried fruit garnish.",
    450, "",
    [
        ("Rice",         130, 400, *GRAIN, 400),
        ("Lamb",         294, 300, *MEAT,  300),
        ("Butter",       717,  80, *DAIRY,  80),
        ("Saffron",      310,   1, *HERB,    1),
        ("Dried Apricots",241, 50, *FRUIT,  50),
        ("Raisins",      299,  50, *FRUIT,  50),
        ("Lavash",       277, 100, *GRAIN, 100),
    ]
)

add_recipe(
    "Dushbara (Azerbaijani Tiny Dumplings)",
    "Miniature lamb dumplings in a tangy sour broth, a traditional Azerbaijani dish.",
    "1. Make firm dough; rest 30 min.\n2. Mix lamb mince with onion, saffron, salt, pepper.\n3. Roll dough very thin; cut tiny squares (3cm).\n4. Fill and fold each into small triangles.\n5. Boil in broth 10 min.\n6. Serve with dried mint and vinegar.",
    290, "",
    [
        ("Flour",      364, 300, *BAKE,  300),
        ("Lamb",       294, 250, *MEAT,  250),
        ("Onion",       40, 100, *VEG,   100),
        ("Saffron",    310,   1, *HERB,    1),
        ("Dried Mint",  70,   5, *HERB,    5),
        ("White Wine Vinegar",20,20,*COND,20),
        ("Black Pepper",255,  5, *HERB,    5),
    ]
)

# ═══════════════════════════════════════════════════════════════════════════
# UKRAINIAN RECIPES
# ═══════════════════════════════════════════════════════════════════════════

add_recipe(
    "Varenyky (Ukrainian Dumplings)",
    "Boiled dumplings filled with potato and cheese, served with sour cream.",
    "1. Make soft dough from flour, egg, water, salt.\n2. Mash boiled potatoes with cottage cheese, fried onion.\n3. Roll dough; cut circles.\n4. Fill and pinch shut.\n5. Boil in salted water 5 min.\n6. Serve with fried onion, butter and sour cream.",
    340, "",
    [
        ("Flour",       364, 350, *BAKE,  350),
        ("Potato",       77, 400, *VEG,   400),
        ("Cottage Cheese",98,150, *DAIRY, 150),
        ("Onion",        40, 150, *VEG,   150),
        ("Egg",         155,  60, *DAIRY,  60),
        ("Butter",      717,  50, *DAIRY,  50),
        ("Sour Cream",  193, 100, *DAIRY, 100),
    ]
)

add_recipe(
    "Chicken Kyiv",
    "Golden crumbed chicken breast stuffed with herbed garlic butter.",
    "1. Pound chicken breasts flat.\n2. Place herbed butter in centre; roll and seal.\n3. Freeze 30 min.\n4. Coat in flour, beaten egg, then breadcrumbs.\n5. Deep fry at 180°C for 12-15 min.\n6. Serve with potato wedges.",
    520, "",
    [
        ("Chicken",        239, 400, *MEAT,  400),
        ("Butter",         717, 100, *DAIRY, 100),
        ("Garlic",         149,  15, *VEG,    15),
        ("Parsley",         36,  15, *HERB,   15),
        ("Egg",            155, 120, *DAIRY, 120),
        ("Breadcrumbs",    395, 100, *BAKE,  100),
        ("Flour",          364,  50, *BAKE,   50),
        ("Sunflower Oil",  884, 200, *OIL,   200),
    ]
)

# ═══════════════════════════════════════════════════════════════════════════
# TURKISH / MIDDLE EASTERN (popular in the region)
# ═══════════════════════════════════════════════════════════════════════════

add_recipe(
    "Adana Kebab",
    "Spicy hand-minced lamb kebab on wide skewers, grilled over charcoal.",
    "1. Finely mince lamb with lamb fat by hand or processor.\n2. Add red pepper flakes, cumin, salt, onion juice.\n3. Knead vigorously 10 min.\n4. Shape onto flat skewers.\n5. Grill over charcoal 10-12 min.\n6. Serve on lavash with grilled tomato and onion salad.",
    350, "",
    [
        ("Lamb",         294, 500, *MEAT,  500),
        ("Red Pepper Flakes",282,10,*HERB,  10),
        ("Cumin",        375,   5, *HERB,    5),
        ("Onion",         40, 100, *VEG,   100),
        ("Lavash",       277, 100, *GRAIN, 100),
        ("Tomato",        18, 150, *VEG,   150),
    ]
)

add_recipe(
    "Lentil Soup (Mercimek Çorbası)",
    "Simple, nourishing red lentil soup common across Turkey and the Caucasus.",
    "1. Sauté onion and garlic in oil.\n2. Add red lentils, carrot, potato.\n3. Cover with water; simmer 25 min.\n4. Blend smooth.\n5. Season with cumin and paprika.\n6. Drizzle with butter and chilli.",
    220, "",
    [
        ("Red Lentils",  116, 200, *LEGUM, 200),
        ("Onion",         40, 100, *VEG,   100),
        ("Carrot",        41, 100, *VEG,   100),
        ("Potato",        77, 100, *VEG,   100),
        ("Garlic",       149,  10, *VEG,    10),
        ("Cumin",        375,   5, *HERB,    5),
        ("Paprika",      282,   5, *HERB,    5),
        ("Butter",       717,  20, *DAIRY,  20),
        ("Olive Oil",    884,  30, *OIL,    30),
    ]
)

add_recipe(
    "Muhammara (Roasted Red Pepper Walnut Dip)",
    "Levantine/Turkish smoky red pepper and walnut spread, popular in the Caucasus.",
    "1. Roast red peppers until charred; peel.\n2. Blend with walnuts, breadcrumbs, garlic, lemon, olive oil, cumin, chilli.\n3. Season with salt; adjust texture with olive oil.\n4. Serve with bread.",
    370, "",
    [
        ("Red Pepper",    31, 200, *VEG,   200),
        ("Walnuts",      654, 100, *NUT,   100),
        ("Breadcrumbs",  395,  40, *BAKE,   40),
        ("Garlic",       149,  10, *VEG,    10),
        ("Lemon",         29,  30, *FRUIT,  30),
        ("Olive Oil",    884,  40, *OIL,    40),
        ("Cumin",        375,   5, *HERB,    5),
        ("Chilli",        40,   5, *HERB,    5),
    ]
)

print("\nDone! Caucasian & Eastern European recipes added.")
cur.execute("SELECT COUNT(*) FROM Recipes")
print(f"Total recipes in DB: {cur.fetchone()[0]}")
conn.close()
