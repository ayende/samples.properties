namespace PropertySphere.Models;

public class ServiceRequest
{
    public string? Id { get; set; }
    public string UnitId { get; set; } = string.Empty;
    public string? PropertyId { get; set; }
    public string RenterId { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Status { get; set; } = "Open";
    public DateTime OpenedAt { get; set; }
    public DateTime? ClosedAt { get; set; }
}
