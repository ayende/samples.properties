namespace PropertySphere.Models;

public class DebtItem
{
    public string? Id { get; set; }
    public string? LeaseId { get; set; }
    public string? RenterId { get; set; }
    public string? PropertyId { get; set; }
    public string? UnitId { get; set; }
    public List<string> RenterIds { get; set; } = new();
    public string Type { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public decimal AmountDue { get; set; }
    public decimal AmountPaid { get; set; }
    public DateTime DueDate { get; set; }

}
