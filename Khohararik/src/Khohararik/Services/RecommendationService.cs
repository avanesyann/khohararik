using Khohararik.Services.Interfaces;
using Khohararik.ViewModels;

namespace Khohararik.Services;

public class RecommendationService : IRecommendationService
{
    private readonly IRecipeService _recipeService;

    public RecommendationService(IRecipeService recipeService)
        => _recipeService = recipeService;

    public async Task<RecommendationsViewModel> GetRecommendationsAsync(CartViewModel cart, string? search = null)
    {
        var cartIngredientIds = cart.Items
            .Select(i => i.IngredientId)
            .ToHashSet();

        var recipes = await _recipeService.GetAllWithIngredientsAsync();

        // Filter by name search if provided
        if (!string.IsNullOrWhiteSpace(search))
            recipes = recipes.Where(r => r.Name.Contains(search, StringComparison.OrdinalIgnoreCase)).ToList();

        var results = recipes
            .Where(r => r.RecipeIngredients.Count > 0)
            .Select(r =>
            {
                var required = r.RecipeIngredients.Select(ri => ri.IngredientId).ToList();
                var matched = required.Count(id => cartIngredientIds.Contains(id));
                var score = (double)matched / required.Count;
                var missing = r.RecipeIngredients
                    .Where(ri => !cartIngredientIds.Contains(ri.IngredientId))
                    .Select(ri => ri.Ingredient.Name)
                    .ToList();

                return new RecipeRecommendationViewModel
                {
                    Recipe = r,
                    MatchScore = score,
                    MatchedCount = matched,
                    TotalRequired = required.Count,
                    MissingIngredients = missing
                };
            })
            .Where(r => r.MatchScore > 0)
            .OrderByDescending(r => r.MatchScore)
            .ToList();

        return new RecommendationsViewModel
        {
            Cart = cart,
            Search = search,
            FullMatches = results.Where(r => r.IsFullMatch).ToList(),
            PartialMatches = results.Where(r => !r.IsFullMatch).ToList()
        };
    }
}
