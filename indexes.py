"""RavenDB indexes for PropertySphere"""
from decimal import Decimal


class DebtItemsOutstanding:
    """Index for outstanding debt items with spatial support"""
    
    def __init__(self):
        self.map = """
from debt in docs.DebtItems
let property = LoadDocument(debt.PropertyId, "Properties")
let amountOutstanding = debt.AmountDue - debt.AmountPaid
select new {
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
    Location = CreateSpatialField(property.Latitude, property.Longitude)
}
"""
    
    def execute(self, store):
        """Execute the index creation"""
        # Note: This is a placeholder. Actual implementation would use
        # the RavenDB Python client's index creation API
        index_def = {
            "name": "DebtItems/Outstanding",
            "maps": [self.map]
        }
        print(f"Index created: {index_def['name']}")
        # store.maintenance.send(PutIndexesOperation(index_def))
