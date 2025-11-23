using Raven.Client.Documents.Indexes;
using PropertySphere.Models;

namespace PropertySphere.Indexes;

public class ServiceRequests_ByStatusAndLocation : AbstractIndexCreationTask<ServiceRequest, ServiceRequests_ByStatusAndLocation.Result>
{
    public class Result
    {
        public string? Id { get; set; }
        public string Status { get; set; } = string.Empty;
        public DateTime OpenedAt { get; set; }
        public string UnitId { get; set; } = string.Empty;
        public string? PropertyId { get; set; }
        public object? Location { get; set; }
        public string Type { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
    }

    public ServiceRequests_ByStatusAndLocation()
    {
        Map = requests =>
            from sr in requests
            let property = LoadDocument<Property>(sr.PropertyId)
            select new Result
            {
                Id = sr.Id,
                Status = sr.Status,
                OpenedAt = sr.OpenedAt,
                UnitId = sr.UnitId,
                PropertyId = sr.PropertyId,
                Location =  CreateSpatialField(property.Latitude, property.Longitude),
                Type = sr.Type,
                Description = sr.Description
            };
    }
}
