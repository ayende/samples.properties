using Microsoft.AspNetCore.Mvc;
using PropertySphere.Models;
using Raven.Client.Documents.Session;

namespace PropertySphere.Controllers;

[ApiController]
[Route("api/[controller]")]
public class PaymentsController : ControllerBase
{
    private readonly IDocumentSession _session;

    public PaymentsController(IDocumentSession session)
    {
        _session = session;
    }

    [HttpPost]
    public IActionResult Create([FromBody] Payment payment)
    {
        _session.Store(payment);
        _session.Load<DebtItem>( // preload debt items
            payment.Allocation.Select(x => x.DebtItemId));

        foreach (var allocation in payment.Allocation)
        {
            var debtItem = _session.Load<DebtItem>(allocation.DebtItemId);
            if (debtItem == null)
            {
                return BadRequest($"Debt item not found: {allocation.DebtItemId}");
            }

            debtItem.AmountPaid += allocation.AmountApplied;
        }

        _session.SaveChanges();
        return Ok(payment);
    }
}
