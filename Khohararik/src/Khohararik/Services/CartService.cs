using System.Text.Json;
using Khohararik.Services.Interfaces;
using Khohararik.ViewModels;
using Microsoft.AspNetCore.Http;

namespace Khohararik.Services;

public class CartService : ICartService
{
    private const string SessionKey = "Cart";
    private readonly IHttpContextAccessor _httpContextAccessor;

    public CartService(IHttpContextAccessor httpContextAccessor)
        => _httpContextAccessor = httpContextAccessor;

    private ISession Session => _httpContextAccessor.HttpContext!.Session;

    public CartViewModel GetCart()
    {
        var json = Session.GetString(SessionKey);
        if (string.IsNullOrEmpty(json))
            return new CartViewModel();
        return JsonSerializer.Deserialize<CartViewModel>(json) ?? new CartViewModel();
    }

    private void SaveCart(CartViewModel cart)
    {
        Session.SetString(SessionKey, JsonSerializer.Serialize(cart));
    }

    public void AddItem(int ingredientId, string name, string? imageUrl,
        decimal caloriesPer100g, decimal defaultWeight, string categoryName)
    {
        var cart = GetCart();
        var existing = cart.Items.FirstOrDefault(i => i.IngredientId == ingredientId);
        if (existing != null)
        {
            existing.Quantity++;
        }
        else
        {
            cart.Items.Add(new CartItemViewModel
            {
                IngredientId = ingredientId,
                Name = name,
                ImageUrl = imageUrl,
                CaloriesPer100g = caloriesPer100g,
                DefaultWeight = defaultWeight,
                CategoryName = categoryName,
                Quantity = 1
            });
        }
        SaveCart(cart);
    }

    public void RemoveItem(int ingredientId)
    {
        var cart = GetCart();
        cart.Items.RemoveAll(i => i.IngredientId == ingredientId);
        SaveCart(cart);
    }

    public void UpdateQuantity(int ingredientId, int quantity)
    {
        var cart = GetCart();
        var item = cart.Items.FirstOrDefault(i => i.IngredientId == ingredientId);
        if (item != null)
        {
            if (quantity <= 0) cart.Items.Remove(item);
            else item.Quantity = quantity;
        }
        SaveCart(cart);
    }

    public void ClearCart()
    {
        Session.Remove(SessionKey);
    }

    public int GetItemCount()
    {
        return GetCart().TotalItems;
    }
}
