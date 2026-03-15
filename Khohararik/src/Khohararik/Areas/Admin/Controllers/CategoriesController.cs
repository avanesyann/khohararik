using Khohararik.Models;
using Khohararik.Services.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace Khohararik.Areas.Admin.Controllers;

[Area("Admin")]
[Authorize(Roles = "Admin")]
public class CategoriesController : Controller
{
    private readonly ICategoryService _categoryService;
    public CategoriesController(ICategoryService categoryService) => _categoryService = categoryService;

    public async Task<IActionResult> Index() => View(await _categoryService.GetAllAsync());

    public IActionResult Create() => View(new Category());

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> Create(Category category)
    {
        if (!ModelState.IsValid) return View(category);
        await _categoryService.CreateAsync(category);
        TempData["Success"] = "Category created.";
        return RedirectToAction(nameof(Index));
    }

    public async Task<IActionResult> Edit(int id)
    {
        var cat = await _categoryService.GetByIdAsync(id);
        if (cat == null) return NotFound();
        return View(cat);
    }

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> Edit(Category category)
    {
        if (!ModelState.IsValid) return View(category);
        await _categoryService.UpdateAsync(category);
        TempData["Success"] = "Category updated.";
        return RedirectToAction(nameof(Index));
    }

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> Delete(int id)
    {
        await _categoryService.DeleteAsync(id);
        TempData["Success"] = "Category deleted.";
        return RedirectToAction(nameof(Index));
    }
}
