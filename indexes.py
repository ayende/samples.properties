"""RavenDB indexes for PropertySphere"""
from ravendb import AbstractIndexCreationTask

class DebtItems_Outstanding(AbstractIndexCreationTask):
    """Index for outstanding debt items with spatial support"""
    
    def __init__(self):
        super(DebtItems_Outstanding, self).__init__()

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


class ServiceRequests_ByStatusAndLocation(AbstractIndexCreationTask):
    """Index for service requests with status and spatial support"""
    
    def __init__(self):
        super(ServiceRequests_ByStatusAndLocation, self).__init__()

        self.map = """
from sr in docs.ServiceRequests
let property = LoadDocument(sr.PropertyId, "Properties")
select new {
    Id = Id(sr),
    Status = sr.Status,
    OpenedAt = sr.OpenedAt,
    UnitId = sr.UnitId,
    PropertyId = sr.PropertyId,
    Type = sr.Type,
    Description = sr.Description,
    Location = CreateSpatialField(property.Latitude, property.Longitude)
}
"""