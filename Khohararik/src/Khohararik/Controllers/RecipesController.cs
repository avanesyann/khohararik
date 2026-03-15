using Khohararik.Services.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace Khohararik.Controllers;

public class RecipesController : Controller
{
    private readonly IRecipeService _recipeService;
    private readonly ICartService _cartService;
    private readonly IRecommendationService _recommendationService;

    public RecipesController(IRecipeService recipeService, ICartService cartService,
        IRecommendationService recommendationService)
    {
        _recipeService = recipeService;
        _cartService = cartService;
        _recommendationService = recommendationService;
    }

    public async Task<IActionResult> Recommendations(string? search)
    {
        var cart = _cartService.GetCart();
        var vm = await _recommendationService.GetRecommendationsAsync(cart, search);
        return View(vm);
    }

    public async Task<IActionResult> Details(int id)
    {
        var cart = _cartService.GetCart();
        var cartIds = cart.Items.Select(i => i.IngredientId).ToHashSet();

        var recipe = await _recipeService.GetByIdWithIngredientsAsync(id);
        if (recipe == null) return NotFound();

        ViewBag.CartIngredientIds = cartIds;
        return View(recipe);
    }

    public async Task<IActionResult> Index()
    {
        var recipes = await _recipeService.GetAllAsync();
        return View(recipes);
    }
}
