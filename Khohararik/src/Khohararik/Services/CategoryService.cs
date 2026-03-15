using Khohararik.Data;
using Khohararik.Models;
using Khohararik.Services.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace Khohararik.Services;

public class CategoryService : ICategoryService
{
    private readonly ApplicationDbContext _db;
    public CategoryService(ApplicationDbContext db) => _db = db;

    public Task<List<Category>> GetAllAsync() =>
        _db.Categories.OrderBy(c => c.Name).ToListAsync();

    public Task<Category?> GetByIdAsync(int id) =>
        _db.Categories.FindAsync(id).AsTask()!;

    public async Task<Category> CreateAsync(Category category)
    {
        _db.Categories.Add(category);
        await _db.SaveChangesAsync();
        return category;
    }

    public async Task UpdateAsync(Category category)
    {
        _db.Categories.Update(category);
        await _db.SaveChangesAsync();
    }

    public async Task DeleteAsync(int id)
    {
        var cat = await _db.Categories.FindAsync(id);
        if (cat != null) { _db.Categories.Remove(cat); await _db.SaveChangesAsync(); }
    }
}
