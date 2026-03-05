using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Xohararik.Web.Models;
using Xohararik.Web.Services.Interfaces;
using Xohararik.Web.ViewModels;

namespace Xohararik.Web.Controllers.Admin;

[Route("Admin/Recipes")]
public class AdminRecipesController : Controller
{
    private readonly IRecipeService _recipeService;
    private readonly IIngredientService _ingredientService;
    private readonly IWebHostEnvironment _env;

    public AdminRecipesController(IRecipeService recipeService, IIngredientService ingredientService, IWebHostEnvironment env)
    {
        _recipeService = recipeService;
        _ingredientService = ingredientService;
        _env = env;
    }

    [Route("")]
    [Route("Index")]
    public async Task<IActionResult> Index()
    {
        var recipes = await _recipeService.GetAllAsync();
        return View(recipes);
    }

    [Route("Create")]
    public async Task<IActionResult> Create()
    {
        var allIngredients = await _ingredientService.GetAllAsync();
        var vm = new RecipeFormViewModel
        {
            IngredientRows = allIngredients.Select(i => new RecipeIngredientFormRow
            {
                IngredientId = i.Id,
                IngredientName = i.Name,
                RequiredWeight = i.DefaultWeight,
                IsSelected = false
            }).ToList()
        };
        return View(vm);
    }

    [HttpPost]
    [Route("Create")]
    public async Task<IActionResult> Create(RecipeFormViewModel vm)
    {
        if (!ModelState.IsValid) return View(vm);

        var imageUrl = vm.ImageUrl;
        if (vm.ImageFile != null)
            imageUrl = await SaveImageAsync(vm.ImageFile, "recipes");

        var recipe = new Recipe
        {
            Name = vm.Name,
            Description = vm.Description,
            Instructions = vm.Instructions,
            TotalCalories = vm.TotalCalories,
            ImageUrl = imageUrl
        };

        var ingredients = vm.IngredientRows
            .Where(r => r.IsSelected)
            .Select(r => new RecipeIngredient
            {
                IngredientId = r.IngredientId,
                RequiredWeight = r.RequiredWeight
            }).ToList();

        await _recipeService.AddAsync(recipe, ingredients);
        TempData["Success"] = "Recipe created successfully.";
        return RedirectToAction("Index");
    }

    [Route("Edit/{id}")]
    public async Task<IActionResult> Edit(int id)
    {
        var recipe = await _recipeService.GetByIdAsync(id);
        if (recipe == null) return NotFound();

        var allIngredients = await _ingredientService.GetAllAsync();
        var selectedIds = recipe.RecipeIngredients.ToDictionary(ri => ri.IngredientId, ri => ri.RequiredWeight);

        var vm = new RecipeFormViewModel
        {
            Id = recipe.Id,
            Name = recipe.Name,
            Description = recipe.Description,
            Instructions = recipe.Instructions,
            TotalCalories = recipe.TotalCalories,
            ImageUrl = recipe.ImageUrl,
            IngredientRows = allIngredients.Select(i => new RecipeIngredientFormRow
            {
                IngredientId = i.Id,
                IngredientName = i.Name,
                RequiredWeight = selectedIds.ContainsKey(i.Id) ? selectedIds[i.Id] : i.DefaultWeight,
                IsSelected = selectedIds.ContainsKey(i.Id)
            }).ToList()
        };

        return View(vm);
    }

    [HttpPost]
    [Route("Edit/{id}")]
    public async Task<IActionResult> Edit(int id, RecipeFormViewModel vm)
    {
        if (!ModelState.IsValid) return View(vm);

        var imageUrl = vm.ImageUrl;
        if (vm.ImageFile != null)
            imageUrl = await SaveImageAsync(vm.ImageFile, "recipes");

        var recipe = new Recipe
        {
            Id = id,
            Name = vm.Name,
            Description = vm.Description,
            Instructions = vm.Instructions,
            TotalCalories = vm.TotalCalories,
            ImageUrl = imageUrl
        };

        var ingredients = vm.IngredientRows
            .Where(r => r.IsSelected)
            .Select(r => new RecipeIngredient
            {
                IngredientId = r.IngredientId,
                RequiredWeight = r.RequiredWeight
            }).ToList();

        await _recipeService.UpdateAsync(recipe, ingredients);
        TempData["Success"] = "Recipe updated successfully.";
        return RedirectToAction("Index");
    }

    [HttpPost]
    [Route("Delete/{id}")]
    public async Task<IActionResult> Delete(int id)
    {
        await _recipeService.DeleteAsync(id);
        TempData["Success"] = "Recipe deleted.";
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
