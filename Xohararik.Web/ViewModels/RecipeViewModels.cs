namespace Xohararik.Web.ViewModels;

public class RecipeRecommendationResult
{
    public int RecipeId { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? ImageUrl { get; set; }
    public string? Description { get; set; }
    public double TotalCalories { get; set; }
    public double MatchScore { get; set; }
    public int MatchPercent => (int)(MatchScore * 100);
    public bool IsFullMatch => MatchScore >= 1.0;
    public List<string> MissingIngredients { get; set; } = new();
    public List<string> MatchedIngredients { get; set; } = new();
}

public class RecommendationsPageViewModel
{
    public List<RecipeRecommendationResult> Results { get; set; } = new();
    public List<string> CartIngredientNames { get; set; } = new();
    public int FullMatchCount => Results.Count(r => r.IsFullMatch);
    public int PartialMatchCount => Results.Count(r => !r.IsFullMatch);
}

public class RecipeIngredientRow
{
    public string Name { get; set; } = string.Empty;
    public int RequiredWeight { get; set; }
    public bool IsInCart { get; set; }
}

public class RecipeDetailViewModel
{
    public int RecipeId { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? ImageUrl { get; set; }
    public string? Description { get; set; }
    public string? Instructions { get; set; }
    public double TotalCalories { get; set; }
    public double MatchScore { get; set; }
    public int MatchPercent => (int)(MatchScore * 100);
    public bool IsFullMatch => MatchScore >= 1.0;
    public List<RecipeIngredientRow> Ingredients { get; set; } = new();
    public List<string> MissingIngredients => Ingredients.Where(i => !i.IsInCart).Select(i => i.Name).ToList();
}
