"""
Merge duplicate categories:
  'Dairy' (17)        -> keep 'Dairy & Eggs' (4)
  'Grains' (16)       -> keep 'Grains & Pasta' (5)
  'Meat' (15)         -> keep 'Meat & Poultry' (2)
"""
import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\DOTNET;"
    "DATABASE=KhohararikDb;"
    "Trusted_Connection=yes"
)
cur = conn.cursor()

# (duplicate_id, keep_id, better_icon)
merges = [
    (17, 4,  "bi bi-egg-fill"),    # Dairy -> Dairy & Eggs
    (16, 5,  "bi bi-grid-fill"),   # Grains -> Grains & Pasta
    (15, 2,  "bi bi-droplet-fill"),# Meat -> Meat & Poultry
]

for dup_id, keep_id, icon in merges:
    cur.execute("SELECT Name FROM Categories WHERE Id=?", dup_id)
    dup_name = cur.fetchone()[0]
    cur.execute("SELECT Name FROM Categories WHERE Id=?", keep_id)
    keep_name = cur.fetchone()[0]

    # Remap ingredients
    cur.execute("UPDATE Ingredients SET CategoryId=? WHERE CategoryId=?", keep_id, dup_id)
    moved = cur.rowcount
    print(f"  Remap {moved} ingredients: '{dup_name}' -> '{keep_name}'")

    # Delete duplicate category
    cur.execute("DELETE FROM Categories WHERE Id=?", dup_id)

    # Ensure keep category has a good icon
    cur.execute("UPDATE Categories SET IconClass=? WHERE Id=?", icon, keep_id)

conn.commit()
print("\nDone. Current categories:")
cur.execute("SELECT Id, Name, IconClass FROM Categories ORDER BY Name")
for r in cur.fetchall():
    print(f"  {r[0]:2} {r[1]:<20} {r[2]}")
conn.close()
