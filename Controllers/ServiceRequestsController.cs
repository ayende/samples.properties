using Microsoft.AspNetCore.Mvc;
using PropertySphere.Models;
using PropertySphere.Indexes;
using Raven.Client.Documents.Session;
using Raven.Client.Documents.Indexes.Spatial;
using Raven.Client.Documents.Linq;
using Raven.Client.Documents;
using Raven.Client.Documents.Queries;

namespace PropertySphere.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ServiceRequestsController : ControllerBase
{
    private readonly IDocumentSession _session;

    public ServiceRequestsController(IDocumentSession session)
    {
        _session = session;
    }


    [HttpGet("status/{status}")]
    public IActionResult GetByStatus(string status, [FromQuery] string? boundsWkt)
    {
        var docQuery = _session.Query<ServiceRequests_ByStatusAndLocation.Result, ServiceRequests_ByStatusAndLocation>()
            .Where(x => x.Status == status)
            .OrderByDescending(x => x.OpenedAt)
            .Take(10);

        if (!string.IsNullOrWhiteSpace(boundsWkt))
        {
            docQuery = docQuery.Spatial(x => x.Location, spatial => spatial.Within(boundsWkt));
        }

        var results = docQuery.Select(x => new
        {
            x.Id,
            x.Status,
            x.OpenedAt,
            x.UnitId,
            x.PropertyId,
            x.Type,
            x.Description,
            PropertyName = RavenQuery.Load<Property>(x.PropertyId).Name,
            UnitNumber = RavenQuery.Load<Unit>(x.UnitId).UnitNumber
        }).ToList();

        return Ok(results);
    }

    [HttpPost]
    public IActionResult Create([FromBody] ServiceRequest request)
    {
        request.OpenedAt = DateTime.Today;
        request.Status = "Open";
        _session.Store(request);
        _session.SaveChanges();
        return Ok(request);
    }

    [HttpPut("status/{*requestId}")]
    public IActionResult UpdateStatus(string requestId, [FromBody] UpdateStatusRequest updateRequest)
    {
        var request = _session.Load<ServiceRequest>(requestId);
        if (request == null)
            return NotFound();

        request.Status = updateRequest.Status;

        if (updateRequest.Status == "Closed" || updateRequest.Status == "Canceled")
        {
            request.ClosedAt = DateTime.Today;
        }
        _session.SaveChanges();
        return Ok(request);
    }
}

public class UpdateStatusRequest
{
    public string Status { get; set; } = string.Empty;
}
