namespace PropertySphere.Models;

public class Unit
{
    public string? Id { get; set; }
    public string PropertyId { get; set; } = string.Empty;
    public string UnitNumber { get; set; } = string.Empty;
    public DateTime? VacantFrom { get; set; }
}
