using Khohararik.Models;
using Khohararik.Services.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;

namespace Khohararik.Areas.Admin.Controllers;

[Area("Admin")]
[Authorize(Roles = "Admin")]
public class IngredientsController : Controller
{
    private readonly IIngredientService _ingredientService;
    private readonly ICategoryService _categoryService;
    private readonly IWebHostEnvironment _env;

    public IngredientsController(IIngredientService ingredientService,
        ICategoryService categoryService, IWebHostEnvironment env)
    {
        _ingredientService = ingredientService;
        _categoryService = categoryService;
        _env = env;
    }

    public async Task<IActionResult> Index()
        => View(await _ingredientService.GetAllAsync());

    public async Task<IActionResult> Create()
    {
        ViewBag.Categories = new SelectList(await _categoryService.GetAllAsync(), "Id", "Name");
        return View(new Ingredient());
    }

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> Create(Ingredient ingredient, IFormFile? imageFile)
    {
        if (!ModelState.IsValid)
        {
            ViewBag.Categories = new SelectList(await _categoryService.GetAllAsync(), "Id", "Name");
            return View(ingredient);
        }

        if (imageFile != null && imageFile.Length > 0)
            ingredient.ImageUrl = await SaveImageAsync(imageFile, "ingredients");

        await _ingredientService.CreateAsync(ingredient);
        TempData["Success"] = "Ingredient created.";
        return RedirectToAction(nameof(Index));
    }

    public async Task<IActionResult> Edit(int id)
    {
        var ing = await _ingredientService.GetByIdAsync(id);
        if (ing == null) return NotFound();
        ViewBag.Categories = new SelectList(await _categoryService.GetAllAsync(), "Id", "Name", ing.CategoryId);
        return View(ing);
    }

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> Edit(Ingredient ingredient, IFormFile? imageFile)
    {
        if (!ModelState.IsValid)
        {
            ViewBag.Categories = new SelectList(await _categoryService.GetAllAsync(), "Id", "Name");
            return View(ingredient);
        }

        if (imageFile != null && imageFile.Length > 0)
            ingredient.ImageUrl = await SaveImageAsync(imageFile, "ingredients");

        await _ingredientService.UpdateAsync(ingredient);
        TempData["Success"] = "Ingredient updated.";
        return RedirectToAction(nameof(Index));
    }

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> Delete(int id)
    {
        await _ingredientService.DeleteAsync(id);
        TempData["Success"] = "Ingredient deleted.";
        return RedirectToAction(nameof(Index));
    }

    private async Task<string> SaveImageAsync(IFormFile file, string folder)
    {
        var uploads = Path.Combine(_env.WebRootPath, "images", folder);
        Directory.CreateDirectory(uploads);
        var fileName = Guid.NewGuid() + Path.GetExtension(file.FileName);
        var path = Path.Combine(uploads, fileName);
        using var stream = new FileStream(path, FileMode.Create);
        await file.CopyToAsync(stream);
        return $"/images/{folder}/{fileName}";
    }
}
