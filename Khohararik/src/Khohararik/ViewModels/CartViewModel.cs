namespace Khohararik.ViewModels;

public class CartViewModel
{
    public List<CartItemViewModel> Items { get; set; } = new();
    public decimal TotalCalories => Items.Sum(i => i.TotalCalories);
    public int TotalItems => Items.Sum(i => i.Quantity);
}
