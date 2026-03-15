using Khohararik.ViewModels;

namespace Khohararik.Services.Interfaces;

public interface ICartService
{
    CartViewModel GetCart();
    void AddItem(int ingredientId, string name, string? imageUrl, decimal caloriesPer100g, decimal defaultWeight, string categoryName);
    void RemoveItem(int ingredientId);
    void UpdateQuantity(int ingredientId, int quantity);
    void ClearCart();
    int GetItemCount();
}
