using Microsoft.AspNetCore.Mvc;
using PropertySphere.Models;
using Raven.Client.Documents.Session;

namespace PropertySphere.Controllers;

[ApiController]
[Route("api/[controller]")]
public class LeasesController : ControllerBase
{
    private readonly IDocumentSession _session;

    public LeasesController(IDocumentSession session)
    {
        _session = session;
    }

    [HttpPost]
    public IActionResult Create([FromBody] Lease lease)
    {
        var unit = _session.Load<Unit>(lease.UnitId);
        if (unit == null)
            return NotFound("Unit not found");

        _session.Store(lease);
        
        unit.VacantFrom = null;
        
        _session.SaveChanges();
        return Ok(lease);
    }

    [HttpPut("{leaseId}/terminate")]
    public IActionResult Terminate(string leaseId)
    {
        var lease = _session.Load<Lease>(leaseId);
        if (lease == null)
            return NotFound("Lease not found");

        var unit = _session.Load<Unit>(lease.UnitId);
        if (unit == null)
            return NotFound("Unit not found");

        lease.EndDate = DateTime.Now;
        unit.VacantFrom = DateTime.Now;

        _session.SaveChanges();
        return Ok(lease);
    }

    [HttpGet("by-unit/{unitId}")]
    public IActionResult GetByUnit(string unitId)
    {
        var lease = _session.Query<Lease>()
            .Where(l => l.UnitId == unitId && l.EndDate >= DateTime.Now && l.StartDate <= DateTime.Now)
            .FirstOrDefault();

        if (lease == null)
            return NotFound();

        return Ok(lease);
    }
}
