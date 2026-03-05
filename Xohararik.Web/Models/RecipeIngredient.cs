namespace Xohararik.Web.Models;

public class RecipeIngredient
{
    public int RecipeId { get; set; }
    public Recipe Recipe { get; set; } = null!;

    public int IngredientId { get; set; }
    public Ingredient Ingredient { get; set; } = null!;

    public int RequiredWeight { get; set; } // grams needed for the recipe
}
