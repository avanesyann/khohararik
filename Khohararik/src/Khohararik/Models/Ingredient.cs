using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Microsoft.AspNetCore.Mvc.ModelBinding.Validation;

namespace Khohararik.Models;

public class Ingredient
{
    public int Id { get; set; }

    [Required, MaxLength(150)]
    public string Name { get; set; } = string.Empty;

    [Column(TypeName = "decimal(8,2)")]
    public decimal CaloriesPer100g { get; set; }

    /// <summary>Default serving weight in grams</summary>
    [Column(TypeName = "decimal(8,2)")]
    public decimal DefaultWeight { get; set; } = 100;

    public string? ImageUrl { get; set; }

    public int CategoryId { get; set; }
    [ValidateNever]
    public Category Category { get; set; } = null!;

    [ValidateNever]
    public ICollection<RecipeIngredient> RecipeIngredients { get; set; } = new List<RecipeIngredient>();
}
