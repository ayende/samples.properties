namespace PropertySphere.Models;

public class Lease
{
    public string? Id { get; set; }
    public string UnitId { get; set; } = string.Empty;
    public List<string> RenterIds { get; set; } = new();
    public decimal LeaseAmount { get; set; }
    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }
    public string? LegalDocumentId { get; set; }

    // Utility pricing per unit (e.g., per kWh for power, per gallon for water)
    public decimal PowerUnitPrice { get; set; } = 0.12m; // default $0.12 per kWh
    public decimal WaterUnitPrice { get; set; } = 0.005m; // default $0.005 per gallon

    public bool IsActive => DateTime.Today >= StartDate && DateTime.Today <= EndDate;
}
