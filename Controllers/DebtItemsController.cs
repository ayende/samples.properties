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
            .Where(l => l.EndDate >= DateTime.Today && l.StartDate <= DateTime.Today)
            .ToList();

        var nextMonth = DateTime.Today.AddMonths(1);
        var dueDate = new DateTime(nextMonth.Year, nextMonth.Month, 1);

        var currentMonth = DateTime.Today;
        var monthStart = new DateTime(currentMonth.Year, currentMonth.Month, 1);
        var monthEnd = monthStart.AddMonths(1).AddDays(-1);

        var totalRentCharges = 0;
        var totalUtilityCharges = 0;

        foreach (var lease in activeLeases)
        {
            var unit = _session.Load<Unit>(lease.UnitId);
            if (unit == null) continue;

            // Create rent charge
            var rentDebtItem = new DebtItem
            {
                LeaseId = lease.Id,
                UnitId = lease.UnitId,
                PropertyId = unit.PropertyId,
                RenterIds = lease.RenterIds,
                RenterId = lease.RenterIds.FirstOrDefault(),
                Type = "Rent",
                Description = $"Rent for {nextMonth:MMMM yyyy}",
                AmountDue = lease.LeaseAmount,
                AmountPaid = 0,
                DueDate = dueDate
            };
            _session.Store(rentDebtItem);
            totalRentCharges++;

            // Calculate utility charges for the current month
            var powerUsage = _session.TimeSeriesFor(lease.UnitId, "Power")
                .Get(monthStart, monthEnd)?
                .Sum(e => e.Value) ?? 0;

            var waterUsage = _session.TimeSeriesFor(lease.UnitId, "Water")
                .Get(monthStart, monthEnd)?
                .Sum(e => e.Value) ?? 0;

            if (powerUsage > 0)
            {
                var powerCharge = (decimal)powerUsage * lease.PowerUnitPrice;
                var powerDebtItem = new DebtItem
                {
                    LeaseId = lease.Id,
                    UnitId = lease.UnitId,
                    PropertyId = unit.PropertyId,
                    RenterIds = lease.RenterIds,
                    RenterId = lease.RenterIds.FirstOrDefault(),
                    Type = "Utility",
                    Description = $"Electricity - {currentMonth:MMMM yyyy} ({powerUsage:F1} kWh)",
                    AmountDue = Math.Round(powerCharge, 2),
                    AmountPaid = 0,
                    DueDate = dueDate
                };
                _session.Store(powerDebtItem);
                totalUtilityCharges++;
            }

            if (waterUsage > 0)
            {
                var waterCharge = (decimal)waterUsage * lease.WaterUnitPrice;
                var waterDebtItem = new DebtItem
                {
                    LeaseId = lease.Id,
                    UnitId = lease.UnitId,
                    PropertyId = unit.PropertyId,
                    RenterIds = lease.RenterIds,
                    RenterId = lease.RenterIds.FirstOrDefault(),
                    Type = "Utility",
                    Description = $"Water - {currentMonth:MMMM yyyy} ({waterUsage:F1} gallons)",
                    AmountDue = Math.Round(waterCharge, 2),
                    AmountPaid = 0,
                    DueDate = dueDate
                };
                _session.Store(waterDebtItem);
                totalUtilityCharges++;
            }
        }

        _session.SaveChanges();
        return Ok(new
        {
            Message = $"Created {totalRentCharges} rent charges and {totalUtilityCharges} utility charges",
            RentCharges = totalRentCharges,
            UtilityCharges = totalUtilityCharges
        });
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
