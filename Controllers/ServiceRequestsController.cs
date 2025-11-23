using Microsoft.AspNetCore.Mvc;
using PropertySphere.Models;
using PropertySphere.Indexes;
using Raven.Client.Documents.Session;
using Raven.Client.Documents.Indexes.Spatial;
using Raven.Client.Documents.Linq;
using Raven.Client.Documents;

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
        var docQuery = _session.Advanced.DocumentQuery<ServiceRequests_ByStatusAndLocation.Result, ServiceRequests_ByStatusAndLocation>()
            .WhereEquals("Status", status);

        if (!string.IsNullOrWhiteSpace(boundsWkt))
        {
            docQuery = docQuery.RelatesToShape("Location", boundsWkt, SpatialRelation.Within);
        }

        docQuery = docQuery.OrderByDescending("OpenedAt")
            .Take(10);

        var results = docQuery.ToList();

        return Ok(results);
    }

    [HttpPost]
    public IActionResult Create([FromBody] ServiceRequest request)
    {
        request.OpenedAt = DateTime.Now;
        request.Status = "Open";
        _session.Store(request);
        _session.SaveChanges();
        return Ok(request);
    }

    [HttpPut("{requestId}/status")]
    public IActionResult UpdateStatus(string requestId, [FromBody] UpdateStatusRequest updateRequest)
    {
        var request = _session.Load<ServiceRequest>(requestId);
        if (request == null)
            return NotFound();

        request.Status = updateRequest.Status;
        
        if (updateRequest.Status == "Closed" || updateRequest.Status == "Canceled")
        {
            request.ClosedAt = DateTime.Now;
        }

        _session.SaveChanges();
        return Ok(request);
    }
}

public class UpdateStatusRequest
{
    public string Status { get; set; } = string.Empty;
}
