using Khohararik.Services.Interfaces;
using Khohararik.ViewModels;
using Microsoft.AspNetCore.Mvc;

namespace Khohararik.Controllers;

public class IngredientsController : Controller
{
    private readonly IIngredientService _ingredientService;
    private readonly ICategoryService _categoryService;
    private readonly ICartService _cartService;

    public IngredientsController(IIngredientService ingredientService,
        ICategoryService categoryService, ICartService cartService)
    {
        _ingredientService = ingredientService;
        _categoryService = categoryService;
        _cartService = cartService;
    }

    public async Task<IActionResult> Index(int? categoryId, string? search)
    {
        var vm = new IngredientsIndexViewModel
        {
            Categories = await _categoryService.GetAllAsync(),
            Ingredients = await _ingredientService.SearchAsync(search, categoryId),
            SelectedCategoryId = categoryId,
            Search = search,
            Cart = _cartService.GetCart()
        };
        return View(vm);
    }

    [HttpPost]
    public async Task<IActionResult> AddToCart(int id)
    {
        var ingredient = await _ingredientService.GetByIdAsync(id);
        if (ingredient == null) return NotFound();

        _cartService.AddItem(
            ingredient.Id,
            ingredient.Name,
            ingredient.ImageUrl,
            ingredient.CaloriesPer100g,
            ingredient.DefaultWeight,
            ingredient.Category.Name);

        if (Request.Headers["X-Requested-With"] == "XMLHttpRequest")
            return Json(new { success = true, count = _cartService.GetItemCount() });

        return RedirectToAction(nameof(Index));
    }
}
