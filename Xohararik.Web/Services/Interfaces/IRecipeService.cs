using Xohararik.Web.Models;
using Xohararik.Web.ViewModels;

namespace Xohararik.Web.Services.Interfaces;

public interface IRecipeService
{
    Task<List<RecipeRecommendationResult>> GetRecommendationsAsync(List<int> cartIngredientIds);
    Task<RecipeDetailViewModel?> GetRecipeDetailAsync(int id, List<int> cartIngredientIds);
    Task<List<Recipe>> GetAllAsync();
    Task<Recipe?> GetByIdAsync(int id);
    Task AddAsync(Recipe recipe, List<RecipeIngredient> ingredients);
    Task UpdateAsync(Recipe recipe, List<RecipeIngredient> ingredients);
    Task DeleteAsync(int id);
}
