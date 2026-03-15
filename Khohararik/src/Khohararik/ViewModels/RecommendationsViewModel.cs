using Khohararik.ViewModels;

namespace Khohararik.ViewModels;

public class RecommendationsViewModel
{
    public List<RecipeRecommendationViewModel> FullMatches { get; set; } = new();
    public List<RecipeRecommendationViewModel> PartialMatches { get; set; } = new();
    public CartViewModel Cart { get; set; } = new();
    public string? Search { get; set; }
}
