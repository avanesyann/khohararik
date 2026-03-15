import pyodbc
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\DOTNET;"
    "DATABASE=KhohararikDb;"
    "Trusted_Connection=yes"
)
cur = conn.cursor()

keywords = ['Armenian','Georgian','Russian','Caucas','Dolma','Lavash','Khinkali','Plov','Borsch',
            'Khorovats','Kebab','Tolma','Ghapama','Harissa','Lahmacun','Basturma','Manti','Matzoon']
for kw in keywords:
    cur.execute(f"SELECT COUNT(*) FROM Recipes WHERE Name LIKE '%{kw}%'")
    count = cur.fetchone()[0]
    if count:
        cur.execute(f"SELECT Name FROM Recipes WHERE Name LIKE '%{kw}%'")
        print(f"\n=== {kw} ({count}) ===")
        for r in cur.fetchall():
            print(" -", r[0])

cur.execute("SELECT COUNT(*) FROM Recipes")
total = cur.fetchone()[0]
print(f"\nTotal recipes: {total}")
conn.close()
