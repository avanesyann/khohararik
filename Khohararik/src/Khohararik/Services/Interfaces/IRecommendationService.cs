using Khohararik.ViewModels;

namespace Khohararik.Services.Interfaces;

public interface IRecommendationService
{
    Task<RecommendationsViewModel> GetRecommendationsAsync(CartViewModel cart, string? search = null);
}
