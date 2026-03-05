using Microsoft.AspNetCore.Mvc;
using Xohararik.Web.Services.Interfaces;
using Xohararik.Web.ViewModels;

namespace Xohararik.Web.Controllers;

public class RecipesController : Controller
{
    private readonly IRecipeService _recipeService;
    private readonly ICartService _cartService;

    public RecipesController(IRecipeService recipeService, ICartService cartService)
    {
        _recipeService = recipeService;
        _cartService = cartService;
    }

    public async Task<IActionResult> Recommendations()
    {
        var cart = _cartService.GetCart();

        if (cart.Count == 0)
        {
            TempData["Warning"] = "Your cart is empty. Add some ingredients first!";
            return RedirectToAction("Index", "Ingredients");
        }

        var cartIngredientIds = cart.Select(i => i.IngredientId).ToList();
        var results = await _recipeService.GetRecommendationsAsync(cartIngredientIds);

        var vm = new RecommendationsPageViewModel
        {
            Results = results,
            CartIngredientNames = cart.Select(i => i.Name).ToList()
        };

        return View(vm);
    }

    public async Task<IActionResult> Details(int id)
    {
        var cart = _cartService.GetCart();
        var cartIngredientIds = cart.Select(i => i.IngredientId).ToList();

        var vm = await _recipeService.GetRecipeDetailAsync(id, cartIngredientIds);
        if (vm == null) return NotFound();

        return View(vm);
    }
}
