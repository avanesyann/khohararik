namespace Xohararik.Web.ViewModels;

public class CartItem
{
    public int IngredientId { get; set; }
    public string Name { get; set; } = string.Empty;
    public int Quantity { get; set; } = 1;
    public string? ImageUrl { get; set; }
    public double CaloriesPer100g { get; set; }
    public int DefaultWeight { get; set; }
}
