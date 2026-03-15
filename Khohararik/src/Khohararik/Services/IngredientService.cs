using Khohararik.Data;
using Khohararik.Models;
using Khohararik.Services.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace Khohararik.Services;

public class IngredientService : IIngredientService
{
    private readonly ApplicationDbContext _db;
    public IngredientService(ApplicationDbContext db) => _db = db;

    public Task<List<Ingredient>> GetAllAsync() =>
        _db.Ingredients.Include(i => i.Category).OrderBy(i => i.Name).ToListAsync();

    public Task<List<Ingredient>> GetByCategoryAsync(int categoryId) =>
        _db.Ingredients.Include(i => i.Category)
            .Where(i => i.CategoryId == categoryId)
            .OrderBy(i => i.Name).ToListAsync();

    public Task<List<Ingredient>> SearchAsync(string? query, int? categoryId)
    {
        var q = _db.Ingredients.Include(i => i.Category).AsQueryable();
        if (categoryId.HasValue)
            q = q.Where(i => i.CategoryId == categoryId.Value);
        if (!string.IsNullOrWhiteSpace(query))
            q = q.Where(i => i.Name.Contains(query));
        return q.OrderBy(i => i.Name).ToListAsync();
    }

    public Task<Ingredient?> GetByIdAsync(int id) =>
        _db.Ingredients.Include(i => i.Category).FirstOrDefaultAsync(i => i.Id == id);

    public Task<List<Ingredient>> GetByIdsAsync(IEnumerable<int> ids) =>
        _db.Ingredients.Include(i => i.Category)
            .Where(i => ids.Contains(i.Id)).ToListAsync();

    public async Task<Ingredient> CreateAsync(Ingredient ingredient)
    {
        _db.Ingredients.Add(ingredient);
        await _db.SaveChangesAsync();
        return ingredient;
    }

    public async Task UpdateAsync(Ingredient ingredient)
    {
        _db.Ingredients.Update(ingredient);
        await _db.SaveChangesAsync();
    }

    public async Task DeleteAsync(int id)
    {
        var ing = await _db.Ingredients.FindAsync(id);
        if (ing != null) { _db.Ingredients.Remove(ing); await _db.SaveChangesAsync(); }
    }
}
