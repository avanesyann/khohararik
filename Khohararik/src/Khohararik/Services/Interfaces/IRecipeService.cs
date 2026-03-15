using Khohararik.Models;

namespace Khohararik.Services.Interfaces;

public interface IRecipeService
{
    Task<List<Recipe>> GetAllAsync();
    Task<Recipe?> GetByIdAsync(int id);
    Task<Recipe?> GetByIdWithIngredientsAsync(int id);
    Task<List<Recipe>> GetAllWithIngredientsAsync();
    Task<Recipe> CreateAsync(Recipe recipe, Dictionary<int, decimal> ingredientWeights);
    Task UpdateAsync(Recipe recipe, Dictionary<int, decimal> ingredientWeights);
    Task DeleteAsync(int id);
}
