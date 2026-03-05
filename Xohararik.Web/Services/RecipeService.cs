using Microsoft.EntityFrameworkCore;
using Xohararik.Web.Data;
using Xohararik.Web.Models;
using Xohararik.Web.Services.Interfaces;
using Xohararik.Web.ViewModels;

namespace Xohararik.Web.Services;

public class RecipeService : IRecipeService
{
    private readonly AppDbContext _context;

    public RecipeService(AppDbContext context)
    {
        _context = context;
    }

    public async Task<List<RecipeRecommendationResult>> GetRecommendationsAsync(List<int> cartIngredientIds)
    {
        if (cartIngredientIds == null || cartIngredientIds.Count == 0)
            return new List<RecipeRecommendationResult>();

        var recipes = await _context.Recipes
            .Include(r => r.RecipeIngredients)
                .ThenInclude(ri => ri.Ingredient)
            .ToListAsync();

        var cartSet = new HashSet<int>(cartIngredientIds);
        var results = new List<RecipeRecommendationResult>();

        foreach (var recipe in recipes)
        {
            var requiredIds = recipe.RecipeIngredients.Select(ri => ri.IngredientId).ToList();
            if (requiredIds.Count == 0) continue;

            var matchedIngredients = recipe.RecipeIngredients
                .Where(ri => cartSet.Contains(ri.IngredientId))
                .Select(ri => ri.Ingredient.Name)
                .ToList();

            var missingIngredients = recipe.RecipeIngredients
                .Where(ri => !cartSet.Contains(ri.IngredientId))
                .Select(ri => ri.Ingredient.Name)
                .ToList();

            if (matchedIngredients.Count == 0) continue;

            results.Add(new RecipeRecommendationResult
            {
                RecipeId = recipe.Id,
                Name = recipe.Name,
                ImageUrl = recipe.ImageUrl,
                Description = recipe.Description,
                TotalCalories = recipe.TotalCalories,
                MatchScore = (double)matchedIngredients.Count / requiredIds.Count,
                MatchedIngredients = matchedIngredients,
                MissingIngredients = missingIngredients
            });
        }

        return results
            .OrderByDescending(r => r.IsFullMatch)
            .ThenByDescending(r => r.MatchScore)
            .ToList();
    }

    public async Task<RecipeDetailViewModel?> GetRecipeDetailAsync(int id, List<int> cartIngredientIds)
    {
        var recipe = await _context.Recipes
            .Include(r => r.RecipeIngredients)
                .ThenInclude(ri => ri.Ingredient)
            .FirstOrDefaultAsync(r => r.Id == id);

        if (recipe == null) return null;

        var cartSet = new HashSet<int>(cartIngredientIds);
        var matched = recipe.RecipeIngredients.Count(ri => cartSet.Contains(ri.IngredientId));
        var total = recipe.RecipeIngredients.Count;

        return new RecipeDetailViewModel
        {
            RecipeId = recipe.Id,
            Name = recipe.Name,
            ImageUrl = recipe.ImageUrl,
            Description = recipe.Description,
            Instructions = recipe.Instructions,
            TotalCalories = recipe.TotalCalories,
            MatchScore = total == 0 ? 0 : (double)matched / total,
            Ingredients = recipe.RecipeIngredients.Select(ri => new RecipeIngredientRow
            {
                Name = ri.Ingredient.Name,
                RequiredWeight = ri.RequiredWeight,
                IsInCart = cartSet.Contains(ri.IngredientId)
            }).ToList()
        };
    }

    public async Task<List<Recipe>> GetAllAsync() =>
        await _context.Recipes
            .Include(r => r.RecipeIngredients)
            .OrderBy(r => r.Name)
            .ToListAsync();

    public async Task<Recipe?> GetByIdAsync(int id) =>
        await _context.Recipes
            .Include(r => r.RecipeIngredients)
                .ThenInclude(ri => ri.Ingredient)
            .FirstOrDefaultAsync(r => r.Id == id);

    public async Task AddAsync(Recipe recipe, List<RecipeIngredient> ingredients)
    {
        _context.Recipes.Add(recipe);
        await _context.SaveChangesAsync();
        foreach (var ri in ingredients)
        {
            ri.RecipeId = recipe.Id;
            _context.RecipeIngredients.Add(ri);
        }
        await _context.SaveChangesAsync();
    }

    public async Task UpdateAsync(Recipe recipe, List<RecipeIngredient> ingredients)
    {
        _context.Recipes.Update(recipe);
        var existing = _context.RecipeIngredients.Where(ri => ri.RecipeId == recipe.Id);
        _context.RecipeIngredients.RemoveRange(existing);
        foreach (var ri in ingredients)
        {
            ri.RecipeId = recipe.Id;
            _context.RecipeIngredients.Add(ri);
        }
        await _context.SaveChangesAsync();
    }

    public async Task DeleteAsync(int id)
    {
        var recipe = await _context.Recipes.FindAsync(id);
        if (recipe != null)
        {
            _context.Recipes.Remove(recipe);
            await _context.SaveChangesAsync();
        }
    }
}
