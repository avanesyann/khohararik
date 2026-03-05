using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Xohararik.Web.Models;
using Xohararik.Web.Services.Interfaces;
using Xohararik.Web.ViewModels;

namespace Xohararik.Web.Controllers.Admin;

[Route("Admin/Ingredients")]
public class AdminIngredientsController : Controller
{
    private readonly IIngredientService _ingredientService;
    private readonly IWebHostEnvironment _env;

    public AdminIngredientsController(IIngredientService ingredientService, IWebHostEnvironment env)
    {
        _ingredientService = ingredientService;
        _env = env;
    }

    [Route("")]
    [Route("Index")]
    public async Task<IActionResult> Index()
    {
        var ingredients = await _ingredientService.GetAllAsync();
        return View(ingredients);
    }

    [Route("Create")]
    public async Task<IActionResult> Create()
    {
        var vm = new IngredientFormViewModel
        {
            Categories = (await _ingredientService.GetCategoriesAsync())
                .Select(c => new SelectListItem(c.Name, c.Id.ToString())).ToList()
        };
        return View(vm);
    }

    [HttpPost]
    [Route("Create")]
    public async Task<IActionResult> Create(IngredientFormViewModel vm)
    {
        if (!ModelState.IsValid)
        {
            vm.Categories = (await _ingredientService.GetCategoriesAsync())
                .Select(c => new SelectListItem(c.Name, c.Id.ToString())).ToList();
            return View(vm);
        }

        var imageUrl = vm.ImageUrl;
        if (vm.ImageFile != null)
            imageUrl = await SaveImageAsync(vm.ImageFile, "ingredients");

        await _ingredientService.AddAsync(new Ingredient
        {
            Name = vm.Name,
            CaloriesPer100g = vm.CaloriesPer100g,
            DefaultWeight = vm.DefaultWeight,
            CategoryId = vm.CategoryId,
            ImageUrl = imageUrl
        });

        TempData["Success"] = "Ingredient created successfully.";
        return RedirectToAction("Index");
    }

    [Route("Edit/{id}")]
    public async Task<IActionResult> Edit(int id)
    {
        var ingredient = await _ingredientService.GetByIdAsync(id);
        if (ingredient == null) return NotFound();

        var vm = new IngredientFormViewModel
        {
            Id = ingredient.Id,
            Name = ingredient.Name,
            CaloriesPer100g = ingredient.CaloriesPer100g,
            DefaultWeight = ingredient.DefaultWeight,
            CategoryId = ingredient.CategoryId,
            ImageUrl = ingredient.ImageUrl,
            Categories = (await _ingredientService.GetCategoriesAsync())
                .Select(c => new SelectListItem(c.Name, c.Id.ToString())).ToList()
        };
        return View(vm);
    }

    [HttpPost]
    [Route("Edit/{id}")]
    public async Task<IActionResult> Edit(int id, IngredientFormViewModel vm)
    {
        if (!ModelState.IsValid)
        {
            vm.Categories = (await _ingredientService.GetCategoriesAsync())
                .Select(c => new SelectListItem(c.Name, c.Id.ToString())).ToList();
            return View(vm);
        }

        var imageUrl = vm.ImageUrl;
        if (vm.ImageFile != null)
            imageUrl = await SaveImageAsync(vm.ImageFile, "ingredients");

        await _ingredientService.UpdateAsync(new Ingredient
        {
            Id = id,
            Name = vm.Name,
            CaloriesPer100g = vm.CaloriesPer100g,
            DefaultWeight = vm.DefaultWeight,
            CategoryId = vm.CategoryId,
            ImageUrl = imageUrl
        });

        TempData["Success"] = "Ingredient updated successfully.";
        return RedirectToAction("Index");
    }

    [HttpPost]
    [Route("Delete/{id}")]
    public async Task<IActionResult> Delete(int id)
    {
        await _ingredientService.DeleteAsync(id);
        TempData["Success"] = "Ingredient deleted.";
        return RedirectToAction("Index");
    }

    private async Task<string> SaveImageAsync(IFormFile file, string folder)
    {
        var uploadsPath = Path.Combine(_env.WebRootPath, "images", folder);
        Directory.CreateDirectory(uploadsPath);
        var fileName = $"{Guid.NewGuid()}{Path.GetExtension(file.FileName)}";
        var filePath = Path.Combine(uploadsPath, fileName);
        using var stream = new FileStream(filePath, FileMode.Create);
        await file.CopyToAsync(stream);
        return $"/images/{folder}/{fileName}";
    }
}
