using Microsoft.AspNetCore.Mvc;

namespace Xohararik.Web.Controllers;

public class HomeController : Controller
{
    public IActionResult Index() => View();
}
