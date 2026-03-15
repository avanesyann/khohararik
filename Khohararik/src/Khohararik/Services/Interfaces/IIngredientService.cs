using Khohararik.Models;

namespace Khohararik.Services.Interfaces;

public interface IIngredientService
{
    Task<List<Ingredient>> GetAllAsync();
    Task<List<Ingredient>> GetByCategoryAsync(int categoryId);
    Task<List<Ingredient>> SearchAsync(string? query, int? categoryId);
    Task<Ingredient?> GetByIdAsync(int id);
    Task<List<Ingredient>> GetByIdsAsync(IEnumerable<int> ids);
    Task<Ingredient> CreateAsync(Ingredient ingredient);
    Task UpdateAsync(Ingredient ingredient);
    Task DeleteAsync(int id);
}
