using System.ComponentModel.DataAnnotations.Schema;

namespace Khohararik.Models;

public class RecipeIngredient
{
    public int RecipeId { get; set; }
    public Recipe Recipe { get; set; } = null!;

    public int IngredientId { get; set; }
    public Ingredient Ingredient { get; set; } = null!;

    [Column(TypeName = "decimal(8,2)")]
    public decimal RequiredWeight { get; set; } = 100;

    public string? Unit { get; set; } // e.g. "g", "ml", "pcs"
}
