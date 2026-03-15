import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\DOTNET;"
    "DATABASE=KhohararikDb;"
    "Trusted_Connection=yes"
)
cur = conn.cursor()

# Check current state
cur.execute("SELECT Id, Name, IconClass FROM Categories WHERE Name = 'Condiments'")
row = cur.fetchone()
if row:
    print(f"Found: id={row[0]}, name={row[1]}, icon='{row[2]}'")
    if not row[2]:
        cur.execute("UPDATE Categories SET IconClass = 'bi bi-droplet-half' WHERE Id = ?", row[0])
        conn.commit()
        print("Updated icon to 'bi bi-droplet-half'")
    else:
        print("Icon already set, no change needed")
else:
    print("Condiments category not found")

conn.close()
