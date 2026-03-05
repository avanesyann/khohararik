namespace Xohararik.Web.ViewModels;

public class CartViewModel
{
    public List<CartItem> Items { get; set; } = new();
    public int TotalItems => Items.Sum(i => i.Quantity);
    public double TotalCalories => Items.Sum(i => (i.CaloriesPer100g * i.DefaultWeight * i.Quantity) / 100.0);
}
