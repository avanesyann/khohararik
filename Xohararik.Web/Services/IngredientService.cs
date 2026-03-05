using Microsoft.EntityFrameworkCore;
using Xohararik.Web.Data;
using Xohararik.Web.Models;
using Xohararik.Web.Services.Interfaces;
using Xohararik.Web.ViewModels;

namespace Xohararik.Web.Services;

public class IngredientService : IIngredientService
{
    private readonly AppDbContext _context;

    public IngredientService(AppDbContext context)
    {
        _context = context;
    }

    public async Task<IngredientsPageViewModel> GetIngredientsPageAsync(string? category, string? search)
    {
        var query = _context.Ingredients.Include(i => i.Category).AsQueryable();

        if (!string.IsNullOrWhiteSpace(category))
            query = query.Where(i => i.Category.Name == category);

        if (!string.IsNullOrWhiteSpace(search))
            query = query.Where(i => i.Name.Contains(search));

        var ingredients = await query.OrderBy(i => i.Category.Name).ThenBy(i => i.Name).ToListAsync();
        var categories = await _context.Categories.Select(c => c.Name).ToListAsync();

        return new IngredientsPageViewModel
        {
            Ingredients = ingredients.Select(i => new IngredientCardViewModel
            {
                Id = i.Id,
                Name = i.Name,
                CaloriesPer100g = i.CaloriesPer100g,
                DefaultWeight = i.DefaultWeight,
                ImageUrl = i.ImageUrl,
                CategoryName = i.Category.Name
            }).ToList(),
            Categories = categories,
            SelectedCategory = category,
            SearchQuery = search
        };
    }

    public async Task<Ingredient?> GetByIdAsync(int id) =>
        await _context.Ingredients.Include(i => i.Category).FirstOrDefaultAsync(i => i.Id == id);

    public async Task<List<Ingredient>> GetAllAsync() =>
        await _context.Ingredients.Include(i => i.Category).OrderBy(i => i.Name).ToListAsync();

    public async Task<List<Category>> GetCategoriesAsync() =>
        await _context.Categories.OrderBy(c => c.Name).ToListAsync();

    public async Task AddAsync(Ingredient ingredient)
    {
        _context.Ingredients.Add(ingredient);
        await _context.SaveChangesAsync();
    }

    public async Task UpdateAsync(Ingredient ingredient)
    {
        _context.Ingredients.Update(ingredient);
        await _context.SaveChangesAsync();
    }

    public async Task DeleteAsync(int id)
    {
        var ingredient = await _context.Ingredients.FindAsync(id);
        if (ingredient != null)
        {
            _context.Ingredients.Remove(ingredient);
            await _context.SaveChangesAsync();
        }
    }
}
