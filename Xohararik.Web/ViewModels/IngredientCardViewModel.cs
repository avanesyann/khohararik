namespace Xohararik.Web.ViewModels;

public class IngredientCardViewModel
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public double CaloriesPer100g { get; set; }
    public int DefaultWeight { get; set; }
    public string? ImageUrl { get; set; }
    public string CategoryName { get; set; } = string.Empty;
}

public class IngredientsPageViewModel
{
    public List<IngredientCardViewModel> Ingredients { get; set; } = new();
    public List<string> Categories { get; set; } = new();
    public string? SelectedCategory { get; set; }
    public string? SearchQuery { get; set; }
}
