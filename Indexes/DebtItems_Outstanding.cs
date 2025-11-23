using Raven.Client.Documents.Indexes;
using PropertySphere.Models;

namespace PropertySphere.Indexes;

public class DebtItems_Outstanding : AbstractIndexCreationTask<DebtItem, DebtItems_Outstanding.Result>
{
    public class Result
    {
        public string? LeaseId { get; set; }
        public string? RenterId { get; set; }
        public string? PropertyId { get; set; }
        public string? UnitId { get; set; }
        public List<string> RenterIds { get; set; } = [];
        public string Type { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public decimal AmountDue { get; set; }
        public decimal AmountPaid { get; set; }
        public decimal AmountOutstanding { get; set; }
        public DateTime DueDate { get; set; }
        public object? Location { get; set; }
        public string? DebtId { get; internal set; }
    }

    public DebtItems_Outstanding()
    {
        Map = debts =>
            from debt in debts
            let property = LoadDocument<Property>(debt.PropertyId)
            let amountOutstanding = debt.AmountDue - debt.AmountPaid
            select new Result
            {
                DebtId = debt.Id,
                LeaseId = debt.LeaseId,
                RenterId = debt.RenterId,
                PropertyId = debt.PropertyId,
                UnitId = debt.UnitId,
                RenterIds = debt.RenterIds,
                Type = debt.Type,
                Description = debt.Description,
                AmountDue = debt.AmountDue,
                AmountPaid = debt.AmountPaid,
                AmountOutstanding = amountOutstanding,
                DueDate = debt.DueDate,
                Location = property != null ? CreateSpatialField(property.Latitude, property.Longitude) : null
            };
    }
}
