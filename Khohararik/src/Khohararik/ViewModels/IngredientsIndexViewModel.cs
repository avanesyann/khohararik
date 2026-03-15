using Khohararik.Models;
using Khohararik.ViewModels;

namespace Khohararik.ViewModels;

public class IngredientsIndexViewModel
{
    public List<Category> Categories { get; set; } = new();
    public List<Ingredient> Ingredients { get; set; } = new();
    public int? SelectedCategoryId { get; set; }
    public string? Search { get; set; }
    public CartViewModel Cart { get; set; } = new();
}
