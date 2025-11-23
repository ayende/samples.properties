namespace PropertySphere.Models;

public class Property
{
    public string? Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Address { get; set; } = string.Empty;
    public int TotalUnits { get; set; }
    public double Latitude { get; set; }
    public double Longitude { get; set; }
}
