using System.ComponentModel.DataAnnotations;

namespace Khohararik.Models;

public class Category
{
    public int Id { get; set; }

    [Required, MaxLength(100)]
    public string Name { get; set; } = string.Empty;

    public string? IconClass { get; set; } // e.g. "bi bi-egg-fried"

    public ICollection<Ingredient> Ingredients { get; set; } = new List<Ingredient>();
}
