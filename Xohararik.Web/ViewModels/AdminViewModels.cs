using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc.Rendering;

namespace Xohararik.Web.ViewModels;

public class IngredientFormViewModel
{
    public int Id { get; set; }

    [Required] public string Name { get; set; } = string.Empty;
    [Range(0, 9999)] public double CaloriesPer100g { get; set; }
    [Range(1, 5000)] public int DefaultWeight { get; set; } = 100;
    public string? ImageUrl { get; set; }
    public IFormFile? ImageFile { get; set; }

    [Required] public int CategoryId { get; set; }
    public List<SelectListItem> Categories { get; set; } = new();
}

public class RecipeFormViewModel
{
    public int Id { get; set; }

    [Required] public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? Instructions { get; set; }
    [Range(0, 99999)] public double TotalCalories { get; set; }
    public string? ImageUrl { get; set; }
    public IFormFile? ImageFile { get; set; }

    public List<RecipeIngredientFormRow> IngredientRows { get; set; } = new();
    public List<SelectListItem> AllIngredients { get; set; } = new();
}

public class RecipeIngredientFormRow
{
    public int IngredientId { get; set; }
    public string IngredientName { get; set; } = string.Empty;
    public int RequiredWeight { get; set; }
    public bool IsSelected { get; set; }
}
