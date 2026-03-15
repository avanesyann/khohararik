using Khohararik.Models;
using Khohararik.Services.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;

namespace Khohararik.Areas.Admin.Controllers;

[Area("Admin")]
[Authorize(Roles = "Admin")]
public class RecipesController : Controller
{
    private readonly IRecipeService _recipeService;
    private readonly IIngredientService _ingredientService;
    private readonly IWebHostEnvironment _env;

    public RecipesController(IRecipeService recipeService,
        IIngredientService ingredientService, IWebHostEnvironment env)
    {
        _recipeService = recipeService;
        _ingredientService = ingredientService;
        _env = env;
    }

    public async Task<IActionResult> Index()
        => View(await _recipeService.GetAllWithIngredientsAsync());

    public async Task<IActionResult> Create()
    {
        ViewBag.Ingredients = await _ingredientService.GetAllAsync();
        return View(new Recipe());
    }

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> Create(Recipe recipe, IFormFile? imageFile,
        int[]? selectedIngredients, decimal[]? ingredientWeights)
    {
        if (!ModelState.IsValid)
        {
            ViewBag.Ingredients = await _ingredientService.GetAllAsync();
            return View(recipe);
        }

        if (imageFile != null && imageFile.Length > 0)
            recipe.ImageUrl = await SaveImageAsync(imageFile);

        var weights = BuildWeightDictionary(selectedIngredients, ingredientWeights);
        await _recipeService.CreateAsync(recipe, weights);
        TempData["Success"] = "Recipe created.";
        return RedirectToAction(nameof(Index));
    }

    public async Task<IActionResult> Edit(int id)
    {
        var recipe = await _recipeService.GetByIdWithIngredientsAsync(id);
        if (recipe == null) return NotFound();
        ViewBag.Ingredients = await _ingredientService.GetAllAsync();
        ViewBag.RecipeIngredients = recipe.RecipeIngredients
            .ToDictionary(ri => ri.IngredientId, ri => ri.RequiredWeight);
        return View(recipe);
    }

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> Edit(Recipe recipe, IFormFile? imageFile,
        int[]? selectedIngredients, decimal[]? ingredientWeights)
    {
        if (!ModelState.IsValid)
        {
            ViewBag.Ingredients = await _ingredientService.GetAllAsync();
            return View(recipe);
        }

        if (imageFile != null && imageFile.Length > 0)
            recipe.ImageUrl = await SaveImageAsync(imageFile);

        var weights = BuildWeightDictionary(selectedIngredients, ingredientWeights);
        await _recipeService.UpdateAsync(recipe, weights);
        TempData["Success"] = "Recipe updated.";
        return RedirectToAction(nameof(Index));
    }

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> Delete(int id)
    {
        await _recipeService.DeleteAsync(id);
        TempData["Success"] = "Recipe deleted.";
        return RedirectToAction(nameof(Index));
    }

    private Dictionary<int, decimal> BuildWeightDictionary(int[]? ids, decimal[]? weights)
    {
        var dict = new Dictionary<int, decimal>();
        if (ids == null) return dict;
        for (int i = 0; i < ids.Length; i++)
        {
            var w = (weights != null && i < weights.Length) ? weights[i] : 100m;
            if (w > 0) dict[ids[i]] = w;
        }
        return dict;
    }

    private async Task<string> SaveImageAsync(IFormFile file)
    {
        var uploads = Path.Combine(_env.WebRootPath, "images", "recipes");
        Directory.CreateDirectory(uploads);
        var fileName = Guid.NewGuid() + Path.GetExtension(file.FileName);
        var path = Path.Combine(uploads, fileName);
        using var stream = new FileStream(path, FileMode.Create);
        await file.CopyToAsync(stream);
        return $"/images/recipes/{fileName}";
    }
}
