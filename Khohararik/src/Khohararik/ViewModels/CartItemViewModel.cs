namespace Khohararik.ViewModels;

public class CartItemViewModel
{
    public int IngredientId { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? ImageUrl { get; set; }
    public decimal CaloriesPer100g { get; set; }
    public decimal DefaultWeight { get; set; }
    public int Quantity { get; set; }
    public string CategoryName { get; set; } = string.Empty;

    public decimal TotalCalories => CaloriesPer100g * DefaultWeight / 100 * Quantity;
}
