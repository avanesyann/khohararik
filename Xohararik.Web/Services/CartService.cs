using System.Text.Json;
using Xohararik.Web.Services.Interfaces;
using Xohararik.Web.ViewModels;

namespace Xohararik.Web.Services;

public class CartService : ICartService
{
    private readonly IHttpContextAccessor _httpContextAccessor;
    private const string CartKey = "xohararik_cart";

    public CartService(IHttpContextAccessor httpContextAccessor)
    {
        _httpContextAccessor = httpContextAccessor;
    }

    private ISession Session => _httpContextAccessor.HttpContext!.Session;

    public List<CartItem> GetCart()
    {
        var json = Session.GetString(CartKey);
        if (string.IsNullOrEmpty(json)) return new List<CartItem>();
        return JsonSerializer.Deserialize<List<CartItem>>(json) ?? new List<CartItem>();
    }

    public void AddItem(CartItem item)
    {
        var cart = GetCart();
        var existing = cart.FirstOrDefault(i => i.IngredientId == item.IngredientId);
        if (existing != null)
            existing.Quantity += item.Quantity;
        else
            cart.Add(item);
        SaveCart(cart);
    }

    public void RemoveItem(int ingredientId)
    {
        var cart = GetCart();
        cart.RemoveAll(i => i.IngredientId == ingredientId);
        SaveCart(cart);
    }

    public void UpdateQuantity(int ingredientId, int quantity)
    {
        var cart = GetCart();
        var item = cart.FirstOrDefault(i => i.IngredientId == ingredientId);
        if (item == null) return;
        if (quantity <= 0)
            cart.Remove(item);
        else
            item.Quantity = quantity;
        SaveCart(cart);
    }

    public void ClearCart()
    {
        Session.Remove(CartKey);
    }

    public int GetCartCount()
    {
        return GetCart().Sum(i => i.Quantity);
    }

    private void SaveCart(List<CartItem> cart)
    {
        Session.SetString(CartKey, JsonSerializer.Serialize(cart));
    }
}
