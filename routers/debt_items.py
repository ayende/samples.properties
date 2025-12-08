"""API router for debt items"""
from datetime import datetime, timedelta
from fastapi import APIRouter
from database import get_session
from models import DebtItem, Lease, Unit
from models import Property
from models import Renter

router = APIRouter()


@router.get("/missing")
async def get_missing(boundsWkt: str = None):
    """Get outstanding/missing debt items using the DebtItems/Outstanding index"""
    async with get_session() as session:
        # Query using the DebtItems/Outstanding index for items with outstanding amount > 0
        query = session.query_index("DebtItems/Outstanding").where_greater_than_or_equal("AmountOutstanding", 0)
        # Apply spatial filtering if bounds provided
        if boundsWkt:
            query = query.spatial("Location", lambda x: x.within(boundsWkt))
        
        # Include related documents and order by due date
        query = query.include("RenterIds").include("PropertyId").order_by("DueDate").take(10)
        
        # Get the index results
        debts = list(query)
        
        output = []
        for debt in debts:
            # Load property name
            property_name = None
            if debt.PropertyId:
                prop = session.load(debt.PropertyId, object_type=Property)
                property_name = prop.Name if prop else None
            
            # Extract unit number from UnitId
            unit_number = None
            if debt.UnitId:
                unit_number = debt.UnitId.split('/')[-1] if '/' in debt.UnitId else debt.UnitId
            
            # Load renters
            renters = []
            for renter_id in debt.RenterIds:
                renter = session.load(renter_id, object_type=Renter)
                if renter:
                    renters.append({
                        'Id': renter.Id,
                        'FirstName': renter.FirstName,
                        'LastName': renter.LastName
                    })
            
            output.append({
                'Id': session.advanced.get_document_id(debt),
                'Type': debt.Type,
                'Description': debt.Description,
                'AmountDue': debt.AmountDue,
                'AmountPaid': debt.AmountPaid,
                'DueDate': debt.DueDate,
                'PropertyName': property_name,
                'UnitNumber': unit_number,
                'Renters': renters
            })
        
        return output


@router.post("/charge-rent")
async def charge_rent():
    """Charge rent and utility fees for all active leases"""
    async with get_session() as session:
        # Get all active leases
        today = datetime.today()
        active_leases = list(
            session.query(object_type=Lease)
                .where_greater_than_or_equal("EndDate", today.date())
                .where_less_than_or_equal("StartDate", today.date())
                .include("UnitId")
            )
        
        # Calculate next month's due date (1st of next month)
        next_month = datetime(today.year, today.month, 1).replace(day=1)
        if today.month == 12:
            next_month = datetime(today.year + 1, 1, 1)
        else:
            next_month = datetime(today.year, today.month + 1, 1)
        
        due_date = next_month.date()
        
        # Get current month date range
        month_start = datetime(today.year, today.month, 1)
        month_end = (month_start.replace(day=1).replace(month=month_start.month % 12 + 1, year=month_start.year + (month_start.month // 12)) - timedelta(days=1))
        
        total_rent_charges = 0
        total_utility_charges = 0
        
        for lease in active_leases:
            unit = session.load(lease.UnitId, object_type=Unit)
            if not unit:
                continue
            
            # Create rent charge
            rent_debt = DebtItem(
                LeaseId=lease.Id,
                UnitId=lease.UnitId,
                PropertyId=unit.PropertyId,
                RenterIds=lease.RenterIds,
                RenterId=lease.RenterIds[0] if lease.RenterIds else None,
                Type="Rent",
                Description=f"Rent for {next_month.strftime('%B %Y')}",
                AmountDue=lease.LeaseAmount,
                AmountPaid=0,
                DueDate=due_date
            )
            session.store(rent_debt)
            total_rent_charges += 1
            
            # Get utility usage for current month
            power_entries = session.time_series_for(lease.UnitId, "Power").get(month_start, month_end)
            water_entries = session.time_series_for(lease.UnitId, "Water").get(month_start, month_end)
            
            power_usage = sum(e.Value for e in power_entries) if power_entries else 0
            water_usage = sum(e.Value for e in water_entries) if water_entries else 0
            
            # Charge for electricity if usage > 0
            if power_usage > 0:
                power_charge = round(power_usage * lease.PowerUnitPrice, 2)
                power_debt = DebtItem(
                    LeaseId=lease.Id,
                    UnitId=lease.UnitId,
                    PropertyId=unit.PropertyId,
                    RenterIds=lease.RenterIds,
                    RenterId=lease.RenterIds[0] if lease.RenterIds else None,
                    Type="Utility",
                    Description=f"Electricity - {today.strftime('%B %Y')} ({power_usage:.1f} kWh)",
                    AmountDue=power_charge,
                    AmountPaid=0,
                    DueDate=due_date
                )
                session.store(power_debt)
                total_utility_charges += 1
            
            # Charge for water if usage > 0
            if water_usage > 0:
                water_charge = round(water_usage * lease.WaterUnitPrice, 2)
                water_debt = DebtItem(
                    LeaseId=lease.Id,
                    UnitId=lease.UnitId,
                    PropertyId=unit.PropertyId,
                    RenterIds=lease.RenterIds,
                    RenterId=lease.RenterIds[0] if lease.RenterIds else None,
                    Type="Utility",
                    Description=f"Water - {today.strftime('%B %Y')} ({water_usage:.1f} gallons)",
                    AmountDue=water_charge,
                    AmountPaid=0,
                    DueDate=due_date
                )
                session.store(water_debt)
                total_utility_charges += 1
        
        session.save_changes()
        
        return {
            "Message": f"Created {total_rent_charges} rent charges and {total_utility_charges} utility charges",
            "RentCharges": total_rent_charges,
            "UtilityCharges": total_utility_charges
        }


@router.post("/fee/{renter_id}")
async def create_fee(renter_id: str, debt_item: DebtItem):
    """Create a fee for a renter"""
    async with get_session() as session:
        # Validate renter exists
        renter = session.load(renter_id, object_type=Renter)
        if not renter:
            return {"error": "Renter not found"}
        
        # Set renter ID and ensure amount paid is 0
        debt_item.RenterId = renter_id
        debt_item.AmountPaid = 0
        
        session.store(debt_item)
        session.save_changes()
        return debt_item
