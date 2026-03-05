using Microsoft.EntityFrameworkCore;
using Xohararik.Web.Models;

namespace Xohararik.Web.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<Category> Categories => Set<Category>();
    public DbSet<Ingredient> Ingredients => Set<Ingredient>();
    public DbSet<Recipe> Recipes => Set<Recipe>();
    public DbSet<RecipeIngredient> RecipeIngredients => Set<RecipeIngredient>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Composite PK for join table
        modelBuilder.Entity<RecipeIngredient>()
            .HasKey(ri => new { ri.RecipeId, ri.IngredientId });

        modelBuilder.Entity<RecipeIngredient>()
            .HasOne(ri => ri.Recipe)
            .WithMany(r => r.RecipeIngredients)
            .HasForeignKey(ri => ri.RecipeId);

        modelBuilder.Entity<RecipeIngredient>()
            .HasOne(ri => ri.Ingredient)
            .WithMany(i => i.RecipeIngredients)
            .HasForeignKey(ri => ri.IngredientId);

        // Seed Categories
        modelBuilder.Entity<Category>().HasData(
            new Category { Id = 1, Name = "Vegetables", IconClass = "bi bi-flower1" },
            new Category { Id = 2, Name = "Meat", IconClass = "bi bi-egg-fried" },
            new Category { Id = 3, Name = "Dairy", IconClass = "bi bi-cup-straw" },
            new Category { Id = 4, Name = "Grains", IconClass = "bi bi-basket" },
            new Category { Id = 5, Name = "Spices", IconClass = "bi bi-stars" },
            new Category { Id = 6, Name = "Fruits", IconClass = "bi bi-apple" }
        );

        // Seed Ingredients
        modelBuilder.Entity<Ingredient>().HasData(
            // Vegetables
            new Ingredient { Id = 1, Name = "Tomato", CaloriesPer100g = 18, DefaultWeight = 150, CategoryId = 1, ImageUrl = "/images/ingredients/tomato.png" },
            new Ingredient { Id = 2, Name = "Onion", CaloriesPer100g = 40, DefaultWeight = 100, CategoryId = 1, ImageUrl = "/images/ingredients/onion.png" },
            new Ingredient { Id = 3, Name = "Garlic", CaloriesPer100g = 149, DefaultWeight = 10, CategoryId = 1, ImageUrl = "/images/ingredients/garlic.png" },
            new Ingredient { Id = 4, Name = "Carrot", CaloriesPer100g = 41, DefaultWeight = 100, CategoryId = 1, ImageUrl = "/images/ingredients/carrot.png" },
            new Ingredient { Id = 5, Name = "Potato", CaloriesPer100g = 77, DefaultWeight = 200, CategoryId = 1, ImageUrl = "/images/ingredients/potato.png" },
            new Ingredient { Id = 6, Name = "Bell Pepper", CaloriesPer100g = 31, DefaultWeight = 120, CategoryId = 1, ImageUrl = "/images/ingredients/bellpepper.png" },
            new Ingredient { Id = 7, Name = "Cucumber", CaloriesPer100g = 16, DefaultWeight = 150, CategoryId = 1, ImageUrl = "/images/ingredients/cucumber.png" },
            new Ingredient { Id = 8, Name = "Spinach", CaloriesPer100g = 23, DefaultWeight = 80, CategoryId = 1, ImageUrl = "/images/ingredients/spinach.png" },
            // Meat
            new Ingredient { Id = 9, Name = "Chicken Breast", CaloriesPer100g = 165, DefaultWeight = 200, CategoryId = 2, ImageUrl = "/images/ingredients/chicken.png" },
            new Ingredient { Id = 10, Name = "Ground Beef", CaloriesPer100g = 250, DefaultWeight = 200, CategoryId = 2, ImageUrl = "/images/ingredients/beef.png" },
            new Ingredient { Id = 11, Name = "Lamb", CaloriesPer100g = 294, DefaultWeight = 200, CategoryId = 2, ImageUrl = "/images/ingredients/lamb.png" },
            new Ingredient { Id = 12, Name = "Pork", CaloriesPer100g = 242, DefaultWeight = 200, CategoryId = 2, ImageUrl = "/images/ingredients/pork.png" },
            // Dairy
            new Ingredient { Id = 13, Name = "Egg", CaloriesPer100g = 155, DefaultWeight = 60, CategoryId = 3, ImageUrl = "/images/ingredients/egg.png" },
            new Ingredient { Id = 14, Name = "Milk", CaloriesPer100g = 61, DefaultWeight = 250, CategoryId = 3, ImageUrl = "/images/ingredients/milk.png" },
            new Ingredient { Id = 15, Name = "Butter", CaloriesPer100g = 717, DefaultWeight = 30, CategoryId = 3, ImageUrl = "/images/ingredients/butter.png" },
            new Ingredient { Id = 16, Name = "Cheese", CaloriesPer100g = 402, DefaultWeight = 50, CategoryId = 3, ImageUrl = "/images/ingredients/cheese.png" },
            // Grains
            new Ingredient { Id = 17, Name = "Rice", CaloriesPer100g = 130, DefaultWeight = 150, CategoryId = 4, ImageUrl = "/images/ingredients/rice.png" },
            new Ingredient { Id = 18, Name = "Pasta", CaloriesPer100g = 158, DefaultWeight = 150, CategoryId = 4, ImageUrl = "/images/ingredients/pasta.png" },
            new Ingredient { Id = 19, Name = "Bread", CaloriesPer100g = 265, DefaultWeight = 60, CategoryId = 4, ImageUrl = "/images/ingredients/bread.png" },
            new Ingredient { Id = 20, Name = "Flour", CaloriesPer100g = 364, DefaultWeight = 100, CategoryId = 4, ImageUrl = "/images/ingredients/flour.png" },
            // Spices
            new Ingredient { Id = 21, Name = "Salt", CaloriesPer100g = 0, DefaultWeight = 5, CategoryId = 5, ImageUrl = "/images/ingredients/salt.png" },
            new Ingredient { Id = 22, Name = "Black Pepper", CaloriesPer100g = 255, DefaultWeight = 3, CategoryId = 5, ImageUrl = "/images/ingredients/pepper.png" },
            new Ingredient { Id = 23, Name = "Paprika", CaloriesPer100g = 282, DefaultWeight = 5, CategoryId = 5, ImageUrl = "/images/ingredients/paprika.png" },
            new Ingredient { Id = 24, Name = "Olive Oil", CaloriesPer100g = 884, DefaultWeight = 15, CategoryId = 5, ImageUrl = "/images/ingredients/oliveoil.png" },
            // Fruits
            new Ingredient { Id = 25, Name = "Lemon", CaloriesPer100g = 29, DefaultWeight = 80, CategoryId = 6, ImageUrl = "/images/ingredients/lemon.png" }
        );

        // Seed Recipes
        modelBuilder.Entity<Recipe>().HasData(
            new Recipe { Id = 1, Name = "Classic Omelette", Description = "A fluffy egg omelette with cheese.", Instructions = "1. Beat eggs with salt and pepper.\n2. Melt butter in pan.\n3. Pour egg mixture, add cheese.\n4. Fold and serve.", TotalCalories = 350, ImageUrl = "/images/recipes/omelette.png" },
            new Recipe { Id = 2, Name = "Spaghetti Bolognese", Description = "Classic Italian pasta with rich meat sauce.", Instructions = "1. Brown ground beef with onion and garlic.\n2. Add tomatoes, simmer 20 min.\n3. Cook pasta al dente.\n4. Combine and serve.", TotalCalories = 650, ImageUrl = "/images/recipes/bolognese.png" },
            new Recipe { Id = 3, Name = "Greek Salad", Description = "Fresh vegetables with cheese and olive oil.", Instructions = "1. Chop tomatoes, cucumber, pepper.\n2. Add cheese and olives.\n3. Drizzle with olive oil, season.", TotalCalories = 220, ImageUrl = "/images/recipes/greeksalad.png" },
            new Recipe { Id = 4, Name = "Chicken Rice Bowl", Description = "Tender chicken over steamed rice.", Instructions = "1. Season chicken with paprika and salt.\n2. Pan-fry until cooked.\n3. Serve over steamed rice.", TotalCalories = 520, ImageUrl = "/images/recipes/chickenrice.png" },
            new Recipe { Id = 5, Name = "Beef Stew", Description = "Hearty beef and vegetable stew.", Instructions = "1. Brown beef pieces.\n2. Add carrots, potatoes, onion.\n3. Cover with water, simmer 1hr.\n4. Season and serve.", TotalCalories = 480, ImageUrl = "/images/recipes/beefstew.png" },
            new Recipe { Id = 6, Name = "Mashed Potatoes", Description = "Creamy buttery mashed potatoes.", Instructions = "1. Boil potatoes until soft.\n2. Drain and mash with butter and milk.\n3. Season with salt and pepper.", TotalCalories = 210, ImageUrl = "/images/recipes/mashedpotatoes.png" },
            new Recipe { Id = 7, Name = "Lamb Khorovats", Description = "Armenian-style grilled lamb.", Instructions = "1. Marinate lamb with onion, lemon, salt, pepper.\n2. Grill on skewers over charcoal.\n3. Serve with vegetables.", TotalCalories = 580, ImageUrl = "/images/recipes/khorovats.png" }
        );

        // Seed RecipeIngredients
        modelBuilder.Entity<RecipeIngredient>().HasData(
            // Classic Omelette
            new RecipeIngredient { RecipeId = 1, IngredientId = 13, RequiredWeight = 180 }, // 3 eggs
            new RecipeIngredient { RecipeId = 1, IngredientId = 15, RequiredWeight = 15 },  // butter
            new RecipeIngredient { RecipeId = 1, IngredientId = 16, RequiredWeight = 30 },  // cheese
            new RecipeIngredient { RecipeId = 1, IngredientId = 21, RequiredWeight = 3 },   // salt
            new RecipeIngredient { RecipeId = 1, IngredientId = 22, RequiredWeight = 2 },   // pepper
            // Spaghetti Bolognese
            new RecipeIngredient { RecipeId = 2, IngredientId = 10, RequiredWeight = 200 }, // ground beef
            new RecipeIngredient { RecipeId = 2, IngredientId = 18, RequiredWeight = 150 }, // pasta
            new RecipeIngredient { RecipeId = 2, IngredientId = 1, RequiredWeight = 200 },  // tomato
            new RecipeIngredient { RecipeId = 2, IngredientId = 2, RequiredWeight = 80 },   // onion
            new RecipeIngredient { RecipeId = 2, IngredientId = 3, RequiredWeight = 10 },   // garlic
            new RecipeIngredient { RecipeId = 2, IngredientId = 21, RequiredWeight = 5 },   // salt
            // Greek Salad
            new RecipeIngredient { RecipeId = 3, IngredientId = 1, RequiredWeight = 200 },  // tomato
            new RecipeIngredient { RecipeId = 3, IngredientId = 7, RequiredWeight = 150 },  // cucumber
            new RecipeIngredient { RecipeId = 3, IngredientId = 6, RequiredWeight = 100 },  // bell pepper
            new RecipeIngredient { RecipeId = 3, IngredientId = 16, RequiredWeight = 80 },  // cheese
            new RecipeIngredient { RecipeId = 3, IngredientId = 24, RequiredWeight = 20 },  // olive oil
            // Chicken Rice Bowl
            new RecipeIngredient { RecipeId = 4, IngredientId = 9, RequiredWeight = 200 },  // chicken
            new RecipeIngredient { RecipeId = 4, IngredientId = 17, RequiredWeight = 150 }, // rice
            new RecipeIngredient { RecipeId = 4, IngredientId = 23, RequiredWeight = 5 },   // paprika
            new RecipeIngredient { RecipeId = 4, IngredientId = 21, RequiredWeight = 5 },   // salt
            new RecipeIngredient { RecipeId = 4, IngredientId = 24, RequiredWeight = 15 },  // olive oil
            // Beef Stew
            new RecipeIngredient { RecipeId = 5, IngredientId = 10, RequiredWeight = 300 }, // ground beef
            new RecipeIngredient { RecipeId = 5, IngredientId = 4, RequiredWeight = 150 },  // carrot
            new RecipeIngredient { RecipeId = 5, IngredientId = 5, RequiredWeight = 300 },  // potato
            new RecipeIngredient { RecipeId = 5, IngredientId = 2, RequiredWeight = 100 },  // onion
            new RecipeIngredient { RecipeId = 5, IngredientId = 21, RequiredWeight = 5 },   // salt
            new RecipeIngredient { RecipeId = 5, IngredientId = 22, RequiredWeight = 3 },   // pepper
            // Mashed Potatoes
            new RecipeIngredient { RecipeId = 6, IngredientId = 5, RequiredWeight = 400 },  // potato
            new RecipeIngredient { RecipeId = 6, IngredientId = 15, RequiredWeight = 30 },  // butter
            new RecipeIngredient { RecipeId = 6, IngredientId = 14, RequiredWeight = 100 }, // milk
            new RecipeIngredient { RecipeId = 6, IngredientId = 21, RequiredWeight = 5 },   // salt
            // Lamb Khorovats
            new RecipeIngredient { RecipeId = 7, IngredientId = 11, RequiredWeight = 400 }, // lamb
            new RecipeIngredient { RecipeId = 7, IngredientId = 2, RequiredWeight = 100 },  // onion
            new RecipeIngredient { RecipeId = 7, IngredientId = 25, RequiredWeight = 30 },  // lemon
            new RecipeIngredient { RecipeId = 7, IngredientId = 21, RequiredWeight = 5 },   // salt
            new RecipeIngredient { RecipeId = 7, IngredientId = 22, RequiredWeight = 3 }    // pepper
        );
    }
}
