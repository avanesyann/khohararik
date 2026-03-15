using Khohararik.Data;
using Khohararik.Models;
using Khohararik.Services.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace Khohararik.Services;

public class RecipeService : IRecipeService
{
    private readonly ApplicationDbContext _db;
    public RecipeService(ApplicationDbContext db) => _db = db;

    public Task<List<Recipe>> GetAllAsync() =>
        _db.Recipes.OrderBy(r => r.Name).ToListAsync();

    public Task<Recipe?> GetByIdAsync(int id) =>
        _db.Recipes.FindAsync(id).AsTask()!;

    public Task<Recipe?> GetByIdWithIngredientsAsync(int id) =>
        _db.Recipes
            .Include(r => r.RecipeIngredients)
                .ThenInclude(ri => ri.Ingredient)
                    .ThenInclude(i => i.Category)
            .FirstOrDefaultAsync(r => r.Id == id);

    public Task<List<Recipe>> GetAllWithIngredientsAsync() =>
        _db.Recipes
            .Include(r => r.RecipeIngredients)
                .ThenInclude(ri => ri.Ingredient)
            .OrderBy(r => r.Name)
            .ToListAsync();

    public async Task<Recipe> CreateAsync(Recipe recipe, Dictionary<int, decimal> ingredientWeights)
    {
        _db.Recipes.Add(recipe);
        await _db.SaveChangesAsync();

        foreach (var (ingredientId, weight) in ingredientWeights)
        {
            _db.RecipeIngredients.Add(new RecipeIngredient
            {
                RecipeId = recipe.Id,
                IngredientId = ingredientId,
                RequiredWeight = weight
            });
        }
        await _db.SaveChangesAsync();
        return recipe;
    }

    public async Task UpdateAsync(Recipe recipe, Dictionary<int, decimal> ingredientWeights)
    {
        _db.Recipes.Update(recipe);

        // Replace all recipe ingredients
        var existing = _db.RecipeIngredients.Where(ri => ri.RecipeId == recipe.Id);
        _db.RecipeIngredients.RemoveRange(existing);

        foreach (var (ingredientId, weight) in ingredientWeights)
        {
            _db.RecipeIngredients.Add(new RecipeIngredient
            {
                RecipeId = recipe.Id,
                IngredientId = ingredientId,
                RequiredWeight = weight
            });
        }
        await _db.SaveChangesAsync();
    }

    public async Task DeleteAsync(int id)
    {
        var recipe = await _db.Recipes.FindAsync(id);
        if (recipe != null) { _db.Recipes.Remove(recipe); await _db.SaveChangesAsync(); }
    }
}
