using Microsoft.AspNetCore.Mvc;
using Xohararik.Web.Services.Interfaces;
using Xohararik.Web.ViewModels;

namespace Xohararik.Web.Controllers;

public class CartController : Controller
{
    private readonly ICartService _cartService;
    private readonly IIngredientService _ingredientService;

    public CartController(ICartService cartService, IIngredientService ingredientService)
    {
        _cartService = cartService;
        _ingredientService = ingredientService;
    }

    public IActionResult Index()
    {
        var vm = new CartViewModel { Items = _cartService.GetCart() };
        return View(vm);
    }

    [HttpPost]
    public async Task<IActionResult> Add(int ingredientId, int quantity = 1)
    {
        var ingredient = await _ingredientService.GetByIdAsync(ingredientId);
        if (ingredient == null) return NotFound();

        _cartService.AddItem(new CartItem
        {
            IngredientId = ingredient.Id,
            Name = ingredient.Name,
            Quantity = quantity,
            ImageUrl = ingredient.ImageUrl,
            CaloriesPer100g = ingredient.CaloriesPer100g,
            DefaultWeight = ingredient.DefaultWeight
        });

        TempData["Success"] = $"{ingredient.Name} added to cart!";
        return RedirectToAction("Index", "Ingredients");
    }

    [HttpPost]
    public IActionResult Remove(int ingredientId)
    {
        _cartService.RemoveItem(ingredientId);
        return RedirectToAction("Index");
    }

    [HttpPost]
    public IActionResult UpdateQuantity(int ingredientId, int quantity)
    {
        _cartService.UpdateQuantity(ingredientId, quantity);
        return RedirectToAction("Index");
    }

    [HttpPost]
    public IActionResult Clear()
    {
        _cartService.ClearCart();
        return RedirectToAction("Index");
    }

    // AJAX endpoint for cart count in navbar
    [HttpGet]
    public IActionResult Count()
    {
        return Json(new { count = _cartService.GetCartCount() });
    }
}
