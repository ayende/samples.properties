using Microsoft.AspNetCore.Mvc;
using PropertySphere.Models;
using Raven.Client.Documents.Session;

namespace PropertySphere.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DataGenerationController : ControllerBase
{
    private readonly IDocumentSession _session;

    public DataGenerationController(IDocumentSession session)
    {
        _session = session;
    }

    [HttpPost("generate-data")]
    public IActionResult GenerateData()
    {
        var random = new Random();

        var properties = new List<Property>
        {
            new Property { Name = "The Willow Apartments", Address = "123 Maple Street, Springfield, IL", TotalUnits = 4, Latitude = 39.7817, Longitude = -89.6501 },
            new Property { Name = "Oak Ridge Complex", Address = "456 Oak Avenue, Portland, OR", TotalUnits = 3, Latitude = 45.5152, Longitude = -122.6784 },
            new Property { Name = "Sunset Towers", Address = "789 Sunset Blvd, Los Angeles, CA", TotalUnits = 3, Latitude = 34.0522, Longitude = -118.2437 }
        };

        foreach (var prop in properties)
        {
            _session.Store(prop);
        }
        _session.SaveChanges();

        var units = new List<Unit>
        {
            new Unit { Id = $"{properties[0].Id}/101", PropertyId = properties[0].Id!, UnitNumber = "101", VacantFrom = null },
            new Unit { Id = $"{properties[0].Id}/102", PropertyId = properties[0].Id!, UnitNumber = "102", VacantFrom = null },
            new Unit { Id = $"{properties[0].Id}/201", PropertyId = properties[0].Id!, UnitNumber = "201", VacantFrom = DateTime.Today.AddDays(-15) },
            new Unit { Id = $"{properties[0].Id}/202", PropertyId = properties[0].Id!, UnitNumber = "202", VacantFrom = null },
            new Unit { Id = $"{properties[1].Id}/1A", PropertyId = properties[1].Id!, UnitNumber = "1A", VacantFrom = null },
            new Unit { Id = $"{properties[1].Id}/1B", PropertyId = properties[1].Id!, UnitNumber = "1B", VacantFrom = null },
            new Unit { Id = $"{properties[1].Id}/2A", PropertyId = properties[1].Id!, UnitNumber = "2A", VacantFrom = DateTime.Today.AddDays(-5) },
            new Unit { Id = $"{properties[2].Id}/301", PropertyId = properties[2].Id!, UnitNumber = "301", VacantFrom = null },
            new Unit { Id = $"{properties[2].Id}/302", PropertyId = properties[2].Id!, UnitNumber = "302", VacantFrom = null },
            new Unit { Id = $"{properties[2].Id}/303", PropertyId = properties[2].Id!, UnitNumber = "303", VacantFrom = null }
        };

        foreach (var unit in units)
        {
            _session.Store(unit);
        }
        _session.SaveChanges();

        var renters = new List<Renter>
        {
            new Renter { FirstName = "John", LastName = "Doe", TelegramChatId = "123456789", ContactEmail = "john.doe@email.com", ContactPhone = "555-0101" },
            new Renter { FirstName = "Jane", LastName = "Smith", TelegramChatId = "987654321", ContactEmail = "jane.smith@email.com", ContactPhone = "555-0102" },
            new Renter { FirstName = "Michael", LastName = "Johnson", TelegramChatId = null, ContactEmail = "m.johnson@email.com", ContactPhone = "555-0103" },
            new Renter { FirstName = "Emily", LastName = "Williams", TelegramChatId = "456789123", ContactEmail = "emily.w@email.com", ContactPhone = "555-0104" },
            new Renter { FirstName = "David", LastName = "Brown", TelegramChatId = null, ContactEmail = "d.brown@email.com", ContactPhone = "555-0105" },
            new Renter { FirstName = "Sarah", LastName = "Davis", TelegramChatId = "789123456", ContactEmail = "sarah.davis@email.com", ContactPhone = "555-0106" },
            new Renter { FirstName = "Robert", LastName = "Miller", TelegramChatId = null, ContactEmail = "r.miller@email.com", ContactPhone = "555-0107" },
            new Renter { FirstName = "Lisa", LastName = "Wilson", TelegramChatId = "321654987", ContactEmail = "lisa.wilson@email.com", ContactPhone = "555-0108" },
            new Renter { FirstName = "James", LastName = "Moore", TelegramChatId = null, ContactEmail = "j.moore@email.com", ContactPhone = "555-0109" },
            new Renter { FirstName = "Jennifer", LastName = "Taylor", TelegramChatId = "654987321", ContactEmail = "jen.taylor@email.com", ContactPhone = "555-0110" },
            new Renter { FirstName = "William", LastName = "Anderson", TelegramChatId = null, ContactEmail = "w.anderson@email.com", ContactPhone = "555-0111" },
            new Renter { FirstName = "Amanda", LastName = "Thomas", TelegramChatId = "147258369", ContactEmail = "amanda.t@email.com", ContactPhone = "555-0112" },
            new Renter { FirstName = "Christopher", LastName = "Jackson", TelegramChatId = null, ContactEmail = "c.jackson@email.com", ContactPhone = "555-0113" },
            new Renter { FirstName = "Jessica", LastName = "White", TelegramChatId = "963852741", ContactEmail = "jessica.white@email.com", ContactPhone = "555-0114" },
            new Renter { FirstName = "Daniel", LastName = "Harris", TelegramChatId = null, ContactEmail = "d.harris@email.com", ContactPhone = "555-0115" }
        };

        foreach (var renter in renters)
        {
            _session.Store(renter);
        }
        _session.SaveChanges();

        var leases = new List<Lease>
        {
            new Lease { UnitId = units[0].Id!, RenterIds = new List<string> { renters[0].Id!, renters[1].Id! }, LeaseAmount = 1500, StartDate = DateTime.Today.AddMonths(-6), EndDate = DateTime.Today.AddMonths(6) },
            new Lease { UnitId = units[1].Id!, RenterIds = new List<string> { renters[2].Id! }, LeaseAmount = 1200, StartDate = DateTime.Today.AddMonths(-3), EndDate = DateTime.Today.AddMonths(9) },
            new Lease { UnitId = units[3].Id!, RenterIds = new List<string> { renters[3].Id!, renters[4].Id! }, LeaseAmount = 1800, StartDate = DateTime.Today.AddMonths(-12), EndDate = DateTime.Today.AddMonths(0) },
            new Lease { UnitId = units[4].Id!, RenterIds = new List<string> { renters[5].Id!, renters[6].Id! }, LeaseAmount = 1600, StartDate = DateTime.Today.AddMonths(-8), EndDate = DateTime.Today.AddMonths(4) },
            new Lease { UnitId = units[5].Id!, RenterIds = new List<string> { renters[7].Id! }, LeaseAmount = 1400, StartDate = DateTime.Today.AddMonths(-4), EndDate = DateTime.Today.AddMonths(8) },
            new Lease { UnitId = units[7].Id!, RenterIds = new List<string> { renters[8].Id!, renters[9].Id! }, LeaseAmount = 2200, StartDate = DateTime.Today.AddMonths(-10), EndDate = DateTime.Today.AddMonths(2) },
            new Lease { UnitId = units[8].Id!, RenterIds = new List<string> { renters[10].Id!, renters[11].Id!, renters[12].Id! }, LeaseAmount = 2500, StartDate = DateTime.Today.AddMonths(-2), EndDate = DateTime.Today.AddMonths(10) }
        };

        foreach (var lease in leases)
        {
            _session.Store(lease);
            var unit = _session.Load<Unit>(lease.UnitId);
            if (unit != null)
                unit.VacantFrom = null;
        }
        _session.SaveChanges();

        // Generate 3 months of utility usage data for occupied units (hourly readings)
        var occupiedUnits = units.Where(u => u.VacantFrom == null).ToList();
        var usageRecordsGenerated = 0;

        foreach (var unit in occupiedUnits)
        {
            // Generate hourly readings for the past 3 months
            var hoursToGenerate = 90 * 24; // 90 days * 24 hours

            for (int hour = hoursToGenerate; hour >= 0; hour--)
            {
                var timestamp = DateTime.Today.AddHours(-hour);

                // Power usage: random between 0.8-2.1 kWh per hour (typical apartment usage)
                // Higher usage during day hours (8am-10pm), lower at night
                var hourOfDay = timestamp.Hour;
                var isActiveHours = hourOfDay >= 8 && hourOfDay <= 22;
                var basePower = isActiveHours ? random.Next(12, 25) / 10.0 : random.Next(5, 12) / 10.0;
                _session.TimeSeriesFor(unit.Id!, "Power").Append(timestamp, basePower);

                // Water usage: random between 2-6 gallons per hour
                // Higher usage during morning (6am-9am) and evening (6pm-10pm)
                var isMorningPeak = hourOfDay >= 6 && hourOfDay <= 9;
                var isEveningPeak = hourOfDay >= 18 && hourOfDay <= 22;
                var baseWater = (isMorningPeak || isEveningPeak) ? random.Next(35, 70) / 10.0 : random.Next(10, 30) / 10.0;
                _session.TimeSeriesFor(unit.Id!, "Water").Append(timestamp, baseWater);

                usageRecordsGenerated += 2;
            }
        }
        _session.SaveChanges();

        var debtItems = new List<DebtItem>();
        foreach (var lease in leases)
        {
            for (int i = 0; i < 3; i++)
            {
                var monthOffset = -i;
                var dueDate = new DateTime(DateTime.Today.Year, DateTime.Today.Month, 1).AddMonths(monthOffset);
                var isPaid = i > 0 || random.Next(0, 3) > 0;
                var unitForLease = units.FirstOrDefault(u => u.Id == lease.UnitId);
                var propertyIdForLease = unitForLease?.PropertyId;
                var primaryRenterId = lease.RenterIds.FirstOrDefault();

                debtItems.Add(new DebtItem
                {
                    LeaseId = lease.Id,
                    UnitId = lease.UnitId,
                    RenterId = primaryRenterId,
                    PropertyId = propertyIdForLease,
                    RenterIds = lease.RenterIds.ToList(),
                    Type = "Rent",
                    Description = $"Rent for {dueDate:MMMM yyyy}",
                    AmountDue = lease.LeaseAmount,
                    AmountPaid = isPaid ? lease.LeaseAmount : (i == 0 ? 0 : lease.LeaseAmount * 0.5m),
                    DueDate = dueDate
                });
            }

            if (random.Next(0, 2) == 0)
            {
                var unitForLease = units.FirstOrDefault(u => u.Id == lease.UnitId);
                var propertyIdForLease = unitForLease?.PropertyId;
                var primaryRenterId = lease.RenterIds.FirstOrDefault();
                debtItems.Add(new DebtItem
                {
                    LeaseId = lease.Id,
                    UnitId = lease.UnitId,
                    RenterId = primaryRenterId,
                    PropertyId = propertyIdForLease,
                    RenterIds = lease.RenterIds.ToList(),
                    Type = "Utility",
                    Description = $"Electricity - {DateTime.Today.AddMonths(-1):MMMM yyyy}",
                    AmountDue = random.Next(80, 200),
                    AmountPaid = random.Next(0, 2) == 0 ? 0 : random.Next(80, 200),
                    DueDate = DateTime.Today.AddDays(random.Next(-30, 10))
                });
            }
        }

        // Guest fee for a specific renter; attach to their current lease/property if available
        var guestRenter = renters[0];
        var rentersLease = leases.FirstOrDefault(l => l.RenterIds.Contains(guestRenter.Id!));
        var rentersUnit = rentersLease != null ? units.FirstOrDefault(u => u.Id == rentersLease.UnitId) : null;
        debtItems.Add(new DebtItem
        {
            LeaseId = rentersLease?.Id,
            UnitId = rentersLease?.UnitId,
            RenterId = guestRenter.Id,
            PropertyId = rentersUnit?.PropertyId,
            RenterIds = new List<string> { guestRenter.Id! },
            Type = "Guest Fee",
            Description = "Additional guest - Nov 2025",
            AmountDue = 150,
            AmountPaid = 0,
            DueDate = DateTime.Today.AddDays(-5)
        });

        foreach (var debt in debtItems)
        {
            _session.Store(debt);
        }
        _session.SaveChanges();

        var payments = new List<Payment>();
        var paidDebts = debtItems.Where(d => d.AmountPaid > 0).Take(5).ToList();

        foreach (var debt in paidDebts)
        {
            payments.Add(new Payment
            {
                PaymentDate = DateTime.Today.AddDays(random.Next(-60, -1)),
                TotalAmountReceived = debt.AmountPaid,
                PaymentMethods = new List<PaymentMethod>
                {
                    new PaymentMethod { Method = random.Next(0, 2) == 0 ? "Card" : "Check", Amount = debt.AmountPaid, Details = random.Next(0, 2) == 0 ? "VISA ****1234" : $"Check #{random.Next(1000, 9999)}" }
                },
                Allocation = new List<PaymentAllocation>
                {
                    new PaymentAllocation { DebtItemId = debt.Id!, AmountApplied = debt.AmountPaid }
                }
            });
        }

        foreach (var payment in payments)
        {
            _session.Store(payment);
        }
        _session.SaveChanges();

        var serviceRequests = new List<ServiceRequest>
        {
            new ServiceRequest { UnitId = units[0].Id!, PropertyId = units[0].PropertyId, RenterId = renters[0].Id!, Type = "Plumbing", Description = "Kitchen sink is leaking", Status = "Open", OpenedAt = DateTime.Today.AddDays(-2) },
            new ServiceRequest { UnitId = units[1].Id!, PropertyId = units[1].PropertyId, RenterId = renters[2].Id!, Type = "Electrical", Description = "Living room outlet not working", Status = "Scheduled", OpenedAt = DateTime.Today.AddDays(-5) },
            new ServiceRequest { UnitId = units[3].Id!, PropertyId = units[3].PropertyId, RenterId = renters[3].Id!, Type = "Package", Description = "Package delivery notification", Status = "Open", OpenedAt = DateTime.Today.AddHours(-6) },
            new ServiceRequest { UnitId = units[4].Id!, PropertyId = units[4].PropertyId, RenterId = renters[5].Id!, Type = "Maintenance", Description = "Heating not working properly", Status = "In Progress", OpenedAt = DateTime.Today.AddDays(-7) },
            new ServiceRequest { UnitId = units[7].Id!, PropertyId = units[7].PropertyId, RenterId = renters[8].Id!, Type = "Domestic", Description = "Noise complaint from neighbors", Status = "Closed", OpenedAt = DateTime.Today.AddDays(-10), ClosedAt = DateTime.Today.AddDays(-8) },
            new ServiceRequest { UnitId = units[8].Id!, PropertyId = units[8].PropertyId, RenterId = renters[10].Id!, Type = "Other", Description = "Request for parking space assignment", Status = "Open", OpenedAt = DateTime.Today.AddDays(-1) }
        };

        foreach (var request in serviceRequests)
        {
            _session.Store(request);
        }
        _session.SaveChanges();

        return Ok(new
        {
            Message = "Demo data generated successfully",
            Properties = properties.Count,
            Units = units.Count,
            Renters = renters.Count,
            Leases = leases.Count,
            DebtItems = debtItems.Count,
            Payments = payments.Count,
            ServiceRequests = serviceRequests.Count,
            UtilityRecords = usageRecordsGenerated
        });
    }
}
