using Khohararik.Models;

namespace Khohararik.ViewModels;

public class RecipeRecommendationViewModel
{
    public Recipe Recipe { get; set; } = null!;
    public double MatchScore { get; set; }         // 0.0 – 1.0
    public int MatchedCount { get; set; }
    public int TotalRequired { get; set; }
    public bool IsFullMatch => MatchScore >= 1.0;
    public List<string> MissingIngredients { get; set; } = new();

    public int MatchPercent => (int)Math.Round(MatchScore * 100);
}
