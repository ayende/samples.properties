using Microsoft.AspNetCore.Mvc;
using PropertySphere.Models;
using PropertySphere.Indexes;
using Raven.Client.Documents.Session;
using Raven.Client.Documents.Linq;
using Raven.Client.Documents;
using Raven.Client.Documents.Indexes.Spatial;

namespace PropertySphere.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DebtItemsController : ControllerBase
{
    private readonly IDocumentSession _session;

    public DebtItemsController(IDocumentSession session)
    {
        _session = session;
    }

    [HttpGet("missing")]
    public IActionResult GetMissing([FromQuery] string? boundsWkt)
    {
        var query = _session.Query<DebtItems_Outstanding.Result, DebtItems_Outstanding>()
            .Where(d => d.AmountOutstanding > 0);

        if (!string.IsNullOrWhiteSpace(boundsWkt))
        {
            query = query.Spatial(r => r.Location, crit => crit.RelatesToShape(boundsWkt, SpatialRelation.Within));
        }

        var debts = query
            .Include(d => d.RenterIds)
            .Include(d => d.PropertyId)
            .OrderBy(d => d.DueDate)
            .Take(10)
            .ToList();

        
        var output = debts.Select(debt => new
        {
            debt.DebtId,
            debt.Type,
            debt.Description,
            debt.AmountDue,
            debt.AmountPaid,
            debt.DueDate,
            PropertyName = debt.PropertyId != null ? _session.Load<Property>(debt.PropertyId)?.Name : null,
            UnitNumber = debt.UnitId != null ? debt.UnitId.Split('/').LastOrDefault() : null,
            Renters = debt.RenterIds.Select(_session.Load<Renter>) // already included
                .Select(r => new { r!.Id, r.FirstName, r.LastName })
                .ToList()
        });

        return Ok(output);
    }

    [HttpPost("charge-rent")]
    public IActionResult ChargeRent()
    {
        var activeLeases = _session.Query<Lease>()
            .Where(l => l.EndDate >= DateTime.Now && l.StartDate <= DateTime.Now)
            .ToList();

        var nextMonth = DateTime.Now.AddMonths(1);
        var dueDate = new DateTime(nextMonth.Year, nextMonth.Month, 1);

        foreach (var lease in activeLeases)
        {
            var debtItem = new DebtItem
            {
                LeaseId = lease.Id,
                Type = "Rent",
                Description = $"Rent for {nextMonth:MMMM yyyy}",
                AmountDue = lease.LeaseAmount,
                AmountPaid = 0,
                DueDate = dueDate
            };
            _session.Store(debtItem);
        }

        _session.SaveChanges();
        return Ok(new { Message = $"Created rent charges for {activeLeases.Count} active leases" });
    }


    [HttpPost("fee/{renterId}")]
    public IActionResult CreateFee(string renterId, [FromBody] DebtItem debtItem)
    {
        var renter = _session.Load<Renter>(renterId);
        if (renter == null)
            return NotFound("Renter not found");

        debtItem.RenterId = renterId;
        debtItem.AmountPaid = 0;
        
        _session.Store(debtItem);
        _session.SaveChanges();
        return Ok(debtItem);
    }
}
