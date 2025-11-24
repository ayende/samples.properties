using Microsoft.AspNetCore.Mvc;
using PropertySphere.Models;
using Raven.Client.Documents;
using Raven.Client.Documents.Session;
using Raven.Client.Documents.Indexes.Spatial;
using Raven.Client.Documents.Linq;

namespace PropertySphere.Controllers;

[ApiController]
[Route("api/[controller]")]
public class PropertiesController : ControllerBase
{
    private readonly IDocumentSession _session;

    public PropertiesController(IDocumentSession session)
    {
        _session = session;
    }

    [HttpGet]
    public IActionResult GetAll([FromQuery] string? boundsWkt)
    {
        IQueryable<Property> query = _session.Query<Property>();

        if (!string.IsNullOrWhiteSpace(boundsWkt))
        {
            query = query.Spatial(factory => factory.Point(p => p.Latitude, p => p.Longitude),
                crit => crit.RelatesToShape(boundsWkt, SpatialRelation.Within));
        }

        var properties = query.ToList();

        var propertyIds = properties.Select(p => p.Id!).ToList();
        var units = _session.Query<Unit>()
                .Where(u => u.PropertyId.In(propertyIds))
                .ToList();

        var unitsByProperty = units.GroupBy(u => u.PropertyId)
            .ToDictionary(g => g.Key, g => g.ToList());

        var result = properties.Select(p => new
        {
            p.Id,
            p.Name,
            p.Address,
            p.TotalUnits,
            p.Latitude,
            p.Longitude,
            Units = unitsByProperty.GetValueOrDefault(p.Id!) ?? []
        });

        return Ok(result);
    }

    [HttpPost]
    public IActionResult Create([FromBody] Property property)
    {
        _session.Store(property);
        _session.SaveChanges();
        return Ok(property);
    }
}
