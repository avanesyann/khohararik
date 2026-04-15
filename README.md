# 🥘 Khohararik — Recipe Recommendation System

A full-stack ASP.NET Core MVC web application that works like an online store — users browse ingredients, add them to a cart, and receive recipe recommendations based on what they selected.

---

## 🚀 Quick Start

### Prerequisites
- .NET 9 SDK
- SQL Server / LocalDB (`(localdb)\DOTNET`)
- Python 3.8+ (for database seeding)
- PowerShell 7+

### 1. Clone & Build
```bash
cd src/Khohararik
dotnet restore
dotnet build
```

### 2. Apply Migrations
```bash
dotnet ef database update
```
This creates **KhohararikDb** on `(localdb)\DOTNET` with all tables.

### 3. Seed the Database
```bash
python scripts/seed_database.py
```
Seeds **10 categories**, **52 ingredients**, **15 recipes**, and creates the admin user.

> **To import a large real-world dataset:** Download [RecipeNLG](https://recipenlg.cs.put.poznan.pl/) or the [Food.com Kaggle dataset](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions), place the CSV at `scripts/recipes.csv`, then re-run the seeder.

### 4. Run the App
```bash
dotnet run
```
Open → **http://localhost:5000**

---

## 🔑 Default Admin Credentials

| Field    | Value                     |
|----------|---------------------------|
| Email    | `admin@khohararik.com`    |
| Password | `Admin@123!`              |
| URL      | http://localhost:5000/Admin |

---

## 🏗️ Architecture

```
src/Khohararik/
├── Controllers/            # Public controllers
│   ├── HomeController
│   ├── IngredientsController
│   ├── CartController
│   └── RecipesController
├── Areas/Admin/            # Admin area (requires Admin role)
│   └── Controllers/
│       ├── HomeController
│       ├── CategoriesController
│       ├── IngredientsController
│       └── RecipesController
├── Services/               # Business logic layer
│   ├── Interfaces/         # ICartService, IRecipeService, etc.
│   ├── CategoryService
│   ├── IngredientService
│   ├── RecipeService
│   ├── CartService         # Session-based cart
│   └── RecommendationService  # LINQ match algorithm
├── Models/                 # EF Core domain entities
├── ViewModels/             # View-specific models
├── Data/
│   ├── ApplicationDbContext
│   └── DbSeeder            # Seeds roles + admin user
└── Views/                  # Razor views (Bootstrap 5)
```

---

## 🧠 Recommendation Algorithm

```csharp
// For each recipe, compare its ingredients with cart contents:
matchScore = matchedIngredients / totalRequiredIngredients

// Sort order:
// 1. Full matches (score == 1.0) first
// 2. Then partial matches sorted by score descending
```

Implemented in `RecommendationService.GetRecommendationsAsync()` using LINQ.

---

## 🗃️ Database Schema

| Table              | Key Fields                                          |
|--------------------|-----------------------------------------------------|
| `Categories`       | Id, Name, IconClass                                 |
| `Ingredients`      | Id, Name, CaloriesPer100g, DefaultWeight, CategoryId |
| `Recipes`          | Id, Name, Description, Instructions, TotalCalories  |
| `RecipeIngredients`| RecipeId (FK), IngredientId (FK), RequiredWeight    |
| `AspNetUsers`      | ASP.NET Identity users                              |
| `AspNetRoles`      | Admin, User roles                                   |

---

## 🔮 Future Extensions

The codebase is structured for easy addition of:
- **User authentication** (Identity scaffolding already in place)
- **Personalized recommendations** (attach userId to cart/favorites)
- **Favorite recipes** (add `UserFavorites` table)
- **REST API** (controllers can be split into API controllers easily)
- **React / mobile frontend** (services layer is fully decoupled)

---

## 📦 Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Backend   | ASP.NET Core 9 MVC                  |
| ORM       | Entity Framework Core 9             |
| Database  | MSSQL (LocalDB / SQL Server)        |
| Auth      | ASP.NET Identity + Roles            |
| Frontend  | Razor Views + Bootstrap 5           |
| Icons     | Bootstrap Icons                     |
| Seeding   | Python 3 + pyodbc                   |

---

## 📜 License

Distributed under the MIT License. See [`LICENSE`](https://github.com/avanesyann/khohararik/blob/main/LICENSE) for more information.