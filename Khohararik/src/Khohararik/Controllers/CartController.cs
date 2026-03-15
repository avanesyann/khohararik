using Khohararik.Services.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace Khohararik.Controllers;

public class CartController : Controller
{
    private readonly ICartService _cartService;

    public CartController(ICartService cartService) => _cartService = cartService;

    public IActionResult Index()
    {
        var cart = _cartService.GetCart();
        return View(cart);
    }

    [HttpPost]
    public IActionResult Remove(int id)
    {
        _cartService.RemoveItem(id);
        if (Request.Headers["X-Requested-With"] == "XMLHttpRequest")
            return Json(new { success = true, count = _cartService.GetItemCount() });
        return RedirectToAction(nameof(Index));
    }

    [HttpPost]
    public IActionResult UpdateQuantity(int id, int quantity)
    {
        _cartService.UpdateQuantity(id, quantity);
        if (Request.Headers["X-Requested-With"] == "XMLHttpRequest")
            return Json(new { success = true, count = _cartService.GetItemCount() });
        return RedirectToAction(nameof(Index));
    }

    [HttpPost]
    public IActionResult Clear()
    {
        _cartService.ClearCart();
        return RedirectToAction(nameof(Index));
    }

    [HttpGet]
    public IActionResult Count()
    {
        return Json(new { count = _cartService.GetItemCount() });
    }
}
