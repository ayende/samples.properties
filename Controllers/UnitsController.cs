using Microsoft.AspNetCore.Mvc;
using PropertySphere.Models;
using Raven.Client.Documents.Session;

namespace PropertySphere.Controllers;

[ApiController]
[Route("api/[controller]")]
public class UnitsController : ControllerBase
{
    private readonly IDocumentSession _session;

    public UnitsController(IDocumentSession session)
    {
        _session = session;
    }

    [HttpGet("by-property/{*propertyId}")]
    public IActionResult GetByProperty(string propertyId)
    {
        var units = _session.Query<Unit>()
            .Where(u => u.PropertyId == propertyId)
            .ToList();
        return Ok(units);
    }

    [HttpPost]
    public IActionResult Create([FromBody] Unit unit)
    {
        if (string.IsNullOrWhiteSpace(unit.PropertyId) || string.IsNullOrWhiteSpace(unit.UnitNumber))
        {
            return BadRequest("PropertyId and UnitNumber are required");
        }
        unit.Id = $"{unit.PropertyId}/{unit.UnitNumber}";
        _session.Store(unit);
        _session.SaveChanges();
        return Ok(unit);
    }
}
