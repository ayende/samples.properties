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
    
    public bool IsActive => DateTime.Now >= StartDate && DateTime.Now <= EndDate;
}
