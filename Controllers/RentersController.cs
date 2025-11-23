using Microsoft.AspNetCore.Mvc;
using PropertySphere.Models;
using Raven.Client.Documents.Session;

namespace PropertySphere.Controllers;

[ApiController]
[Route("api/[controller]")]
public class RentersController : ControllerBase
{
    private readonly IDocumentSession _session;

    public RentersController(IDocumentSession session)
    {
        _session = session;
    }

    [HttpGet("{renterId}")]
    public IActionResult GetById(string renterId)
    {
        var renter = _session.Load<Renter>(renterId);
        if (renter == null)
            return NotFound();
        return Ok(renter);
    }

    [HttpPost]
    public IActionResult Create([FromBody] Renter renter)
    {
        _session.Store(renter);
        _session.SaveChanges();
        return Ok(renter);
    }
}
