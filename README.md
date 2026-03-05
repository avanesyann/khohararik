# Khohararik — Recipe Recommendation System

## Setup Instructions

### Prerequisites
- .NET 8 SDK
- SQL Server (or SQL Server Express / LocalDB)
- Visual Studio 2022 or VS Code

---

### 1. Configure Connection String

Open `appsettings.json` and update the connection string:

```json
"ConnectionStrings": {
  "DefaultConnection": "Server=.;Database=XohararikDb;Trusted_Connection=True;TrustServerCertificate=True;"
}
```

Common alternatives:
- LocalDB: `Server=(localdb)\\mssqllocaldb;Database=XohararikDb;Trusted_Connection=True;`
- SQL Express: `Server=.\\SQLEXPRESS;Database=XohararikDb;Trusted_Connection=True;TrustServerCertificate=True;`

---

### 2. Install Dependencies

```bash
cd Xohararik.Web
dotnet restore
```

---

### 3. Run Migrations

```bash
dotnet ef migrations add InitialCreate
dotnet ef database update
```

This will:
- Create the `XohararikDb` database
- Create all tables (Categories, Ingredients, Recipes, RecipeIngredients)
- Seed the database with sample data (25 ingredients, 7 recipes)

---

### 4. Run the Application

```bash
dotnet run
```

Navigate to `https://localhost:5001` (or the URL shown in terminal).

---

## Project Structure

```
Xohararik.Web/
├── Controllers/
│   ├── HomeController.cs
│   ├── IngredientsController.cs
│   ├── CartController.cs
│   ├── RecipesController.cs
│   └── Admin/
│       ├── AdminIngredientsController.cs
│       └── AdminRecipesController.cs
├── Models/              ← EF Core entities
├── ViewModels/          ← What views receive
├── Services/            ← Business logic
│   └── Interfaces/
├── Data/
│   └── AppDbContext.cs  ← DB context + seed data
├── Views/
└── wwwroot/
```

## Features
- Browse ingredients by category
- Add ingredients to cart (session-based)
- Get recipe recommendations (full + partial match)
- View recipe details with step-by-step instructions
- Admin panel for managing ingredients and recipes

## Admin Panel
- `/Admin/Ingredients` — Manage ingredients
- `/Admin/Recipes` — Manage recipes
