using Xohararik.Web.ViewModels;

namespace Xohararik.Web.Services.Interfaces;

public interface ICartService
{
    List<CartItem> GetCart();
    void AddItem(CartItem item);
    void RemoveItem(int ingredientId);
    void UpdateQuantity(int ingredientId, int quantity);
    void ClearCart();
    int GetCartCount();
}
