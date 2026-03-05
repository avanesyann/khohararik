using Microsoft.AspNetCore.Mvc;
using Xohararik.Web.Services.Interfaces;

namespace Xohararik.Web.Controllers;

public class IngredientsController : Controller
{
    private readonly IIngredientService _ingredientService;

    public IngredientsController(IIngredientService ingredientService)
    {
        _ingredientService = ingredientService;
    }

    public async Task<IActionResult> Index(string? category, string? search)
    {
        var vm = await _ingredientService.GetIngredientsPageAsync(category, search);
        return View(vm);
    }
}
