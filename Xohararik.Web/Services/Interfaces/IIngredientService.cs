using Xohararik.Web.Models;
using Xohararik.Web.ViewModels;

namespace Xohararik.Web.Services.Interfaces;

public interface IIngredientService
{
    Task<IngredientsPageViewModel> GetIngredientsPageAsync(string? category, string? search);
    Task<Ingredient?> GetByIdAsync(int id);
    Task<List<Ingredient>> GetAllAsync();
    Task<List<Category>> GetCategoriesAsync();
    Task AddAsync(Ingredient ingredient);
    Task UpdateAsync(Ingredient ingredient);
    Task DeleteAsync(int id);
}
