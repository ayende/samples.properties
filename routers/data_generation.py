"""API router for demo data generation"""
import random
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query
from database import get_session
from models import Property, Unit, Renter, CreditCard, Lease, DebtItem, Payment, PaymentMethod, PaymentAllocation, ServiceRequest

router = APIRouter()


@router.post("/generate-data")
async def generate_data(
    telegram_chat_id: str = Query(
        ...,
        description="Telegram chat ID for the first renter. To get your Telegram chat ID, start a chat with @userinfobot on Telegram and it will send you your chat ID. Example: 123456789"
    )
):
    """Generate demo data for the application"""
    async with get_session() as session:
        # Create properties
        properties = [
            Property(Name="The Willow Apartments", Address="123 Maple Street, Springfield, IL", 
                    TotalUnits=4, Latitude=39.7817, Longitude=-89.6501),
            Property(Name="Oak Ridge Complex", Address="456 Oak Avenue, Portland, OR", 
                    TotalUnits=3, Latitude=45.5152, Longitude=-122.6784),
            Property(Name="Sunset Towers", Address="789 Sunset Blvd, Los Angeles, CA", 
                    TotalUnits=3, Latitude=34.0522, Longitude=-118.2437)
        ]
        
        for prop in properties:
            session.store(prop)
        session.save_changes()
        
        # Create units
        today = datetime.combine(datetime.today().date(), datetime.min.time())
        units = [
            Unit(Id=f"{properties[0].Id}/101", PropertyId=properties[0].Id, UnitNumber="101", VacantFrom=None),
            Unit(Id=f"{properties[0].Id}/102", PropertyId=properties[0].Id, UnitNumber="102", VacantFrom=None),
            Unit(Id=f"{properties[0].Id}/201", PropertyId=properties[0].Id, UnitNumber="201", VacantFrom=today - timedelta(days=15)),
            Unit(Id=f"{properties[0].Id}/202", PropertyId=properties[0].Id, UnitNumber="202", VacantFrom=None),
            Unit(Id=f"{properties[1].Id}/1A", PropertyId=properties[1].Id, UnitNumber="1A", VacantFrom=None),
            Unit(Id=f"{properties[1].Id}/1B", PropertyId=properties[1].Id, UnitNumber="1B", VacantFrom=None),
            Unit(Id=f"{properties[1].Id}/2A", PropertyId=properties[1].Id, UnitNumber="2A", VacantFrom=today - timedelta(days=5)),
            Unit(Id=f"{properties[2].Id}/301", PropertyId=properties[2].Id, UnitNumber="301", VacantFrom=None),
            Unit(Id=f"{properties[2].Id}/302", PropertyId=properties[2].Id, UnitNumber="302", VacantFrom=None),
            Unit(Id=f"{properties[2].Id}/303", PropertyId=properties[2].Id, UnitNumber="303", VacantFrom=None)
        ]
        
        for unit in units:
            session.store(unit)
        session.save_changes()
        
        # Create renters with credit cards
        card_types = ["Visa", "MasterCard", "Amex", "Discover"]
        renters_data = [
            ("John", "Doe", telegram_chat_id, "john.doe@email.com", "555-0101"),
            ("Jane", "Smith", "987654321", "jane.smith@email.com", "555-0102"),
            ("Michael", "Johnson", None, "m.johnson@email.com", "555-0103"),
            ("Emily", "Williams", "456789123", "emily.w@email.com", "555-0104"),
            ("David", "Brown", None, "d.brown@email.com", "555-0105"),
            ("Sarah", "Davis", "789123456", "sarah.davis@email.com", "555-0106"),
            ("Robert", "Miller", None, "r.miller@email.com", "555-0107"),
            ("Lisa", "Wilson", "321654987", "lisa.wilson@email.com", "555-0108"),
            ("James", "Moore", None, "j.moore@email.com", "555-0109"),
            ("Jennifer", "Taylor", "654987321", "jen.taylor@email.com", "555-0110"),
            ("William", "Anderson", None, "w.anderson@email.com", "555-0111"),
            ("Amanda", "Thomas", "147258369", "amanda.t@email.com", "555-0112"),
            ("Christopher", "Jackson", None, "c.jackson@email.com", "555-0113"),
            ("Jessica", "White", "963852741", "jessica.white@email.com", "555-0114"),
            ("Daniel", "Harris", None, "d.harris@email.com", "555-0115")
        ]
        
        renters = []
        for first, last, telegram, email, phone in renters_data:
            credit_cards = []
            num_cards = random.randint(1, 3)
            for _ in range(num_cards):
                month = random.randint(1, 12)
                year = random.randint(25, 30)
                credit_cards.append(CreditCard(
                    Last4Digits=str(random.randint(1000, 9999)),
                    Type=random.choice(card_types),
                    Expiration=f"{month:02d}/{year:02d}"
                ))
            
            renter = Renter(
                FirstName=first,
                LastName=last,
                TelegramChatId=telegram,
                ContactEmail=email,
                ContactPhone=phone,
                CreditCards=credit_cards
            )
            session.store(renter)
            renters.append(renter)
        session.save_changes()
        
        # Create leases
        leases = [
            Lease(UnitId=units[0].Id, RenterIds=[renters[0].Id, renters[1].Id], 
                 LeaseAmount=1500.0, StartDate=today - timedelta(days=180), EndDate=today + timedelta(days=180)),
            Lease(UnitId=units[1].Id, RenterIds=[renters[2].Id], 
                 LeaseAmount=1200.0, StartDate=today - timedelta(days=90), EndDate=today + timedelta(days=270)),
            Lease(UnitId=units[3].Id, RenterIds=[renters[3].Id, renters[4].Id], 
                 LeaseAmount=1800.0, StartDate=today - timedelta(days=360), EndDate=today),
            Lease(UnitId=units[4].Id, RenterIds=[renters[5].Id, renters[6].Id], 
                 LeaseAmount=1600.0, StartDate=today - timedelta(days=240), EndDate=today + timedelta(days=120)),
            Lease(UnitId=units[5].Id, RenterIds=[renters[7].Id], 
                 LeaseAmount=1400.0, StartDate=today - timedelta(days=120), EndDate=today + timedelta(days=240)),
            Lease(UnitId=units[7].Id, RenterIds=[renters[8].Id, renters[9].Id], 
                 LeaseAmount=2200.0, StartDate=today - timedelta(days=300), EndDate=today + timedelta(days=60)),
            Lease(UnitId=units[8].Id, RenterIds=[renters[10].Id, renters[11].Id, renters[12].Id], 
                 LeaseAmount=2500.0, StartDate=today - timedelta(days=60), EndDate=today + timedelta(days=300))
        ]
        
        for lease in leases:
            session.store(lease)
            unit = session.load(lease.UnitId, object_type=Unit)
            if unit:
                unit.VacantFrom = None
        session.save_changes()
        
        # Generate utility usage data (3 months of hourly readings)
        occupied_units = [u for u in units if u.VacantFrom is None]
        usage_records_generated = 0
        
        for unit in occupied_units:
            hours_to_generate = 90 * 24  # 90 days
            
            for hour in range(hours_to_generate, -1, -1):
                timestamp = today - timedelta(hours=hour)
                hour_of_day = timestamp.hour
                
                # Power usage: higher during active hours (8am-10pm)
                is_active_hours = 8 <= hour_of_day <= 22
                base_power = random.randint(12, 25) / 10.0 if is_active_hours else random.randint(5, 12) / 10.0
                session.time_series_for(unit.Id, "Power").append(timestamp, [base_power])
                
                # Water usage: higher during morning (6am-9am) and evening (6pm-10pm)
                is_morning_peak = 6 <= hour_of_day <= 9
                is_evening_peak = 18 <= hour_of_day <= 22
                base_water = random.randint(35, 70) / 10.0 if (is_morning_peak or is_evening_peak) else random.randint(10, 30) / 10.0
                session.time_series_for(unit.Id, "Water").append(timestamp, [base_water])
                
                usage_records_generated += 2
        session.save_changes()
        
        # Generate debt items
        debt_items = []
        for lease in leases:
            # Generate 3 months of rent
            for i in range(3):
                month_offset = -i
                due_date = datetime(today.year, today.month, 1) + timedelta(days=32 * month_offset)
                due_date = due_date.replace(day=1)
                is_paid = i > 0 or random.randint(0, 2) > 0
                
                unit_for_lease = next((u for u in units if u.Id == lease.UnitId), None)
                debt_items.append(DebtItem(
                    LeaseId=lease.Id,
                    UnitId=lease.UnitId,
                    RenterId=random.choice(lease.RenterIds),
                    PropertyId=unit_for_lease.PropertyId if unit_for_lease else None,
                    RenterIds=lease.RenterIds.copy(),
                    Type="Rent",
                    Description=f"Rent for {due_date.strftime('%B %Y')}",
                    AmountDue=lease.LeaseAmount,
                    AmountPaid=lease.LeaseAmount if is_paid else (0.0 if i == 0 else lease.LeaseAmount * 0.5),
                    DueDate=due_date
                ))
            
            # Generate utility debts
            primary_renter = lease.RenterIds[0] if lease.RenterIds else None
            unit_for_lease = next((u for u in units if u.Id == lease.UnitId), None)
            property_id = unit_for_lease.PropertyId if unit_for_lease else None
            
            # Electricity
            debt_items.append(DebtItem(
                LeaseId=lease.Id,
                UnitId=lease.UnitId,
                RenterId=primary_renter,
                PropertyId=property_id,
                RenterIds=lease.RenterIds.copy(),
                Type="Utility",
                Description=f"Electricity - {(today - timedelta(days=30)).strftime('%B %Y')}",
                AmountDue=float(random.randint(80, 150)),
                AmountPaid=0.0 if random.randint(0, 1) == 0 else float(random.randint(40, 80)),
                DueDate=today + timedelta(days=random.randint(-30, 10))
            ))
            
            # Water
            debt_items.append(DebtItem(
                LeaseId=lease.Id,
                UnitId=lease.UnitId,
                RenterId=primary_renter,
                PropertyId=property_id,
                RenterIds=lease.RenterIds.copy(),
                Type="Utility",
                Description=f"Water - {(today - timedelta(days=30)).strftime('%B %Y')}",
                AmountDue=float(random.randint(40, 80)),
                AmountPaid=0.0 if random.randint(0, 1) == 0 else float(random.randint(20, 40)),
                DueDate=today + timedelta(days=random.randint(-30, 10))
            ))
            
            # Late fee (sometimes)
            if random.randint(0, 2) == 0:
                debt_items.append(DebtItem(
                    LeaseId=lease.Id,
                    UnitId=lease.UnitId,
                    RenterId=primary_renter,
                    PropertyId=property_id,
                    RenterIds=lease.RenterIds.copy(),
                    Type="Late Fee",
                    Description=f"Late payment fee - {(today - timedelta(days=30)).strftime('%B %Y')}",
                    AmountDue=50.0,
                    AmountPaid=0.0,
                    DueDate=today - timedelta(days=15)
                ))
        
        # Guest fee
        guest_renter = renters[0]
        renters_lease = next((l for l in leases if guest_renter.Id in l.RenterIds), None)
        renters_unit = next((u for u in units if u.Id == renters_lease.UnitId), None) if renters_lease else None
        
        debt_items.append(DebtItem(
            LeaseId=renters_lease.Id if renters_lease else None,
            UnitId=renters_lease.UnitId if renters_lease else None,
            RenterId=guest_renter.Id,
            PropertyId=renters_unit.PropertyId if renters_unit else None,
            RenterIds=[guest_renter.Id],
            Type="Guest Fee",
            Description="Additional guest - Nov 2025",
            AmountDue=150.0,
            AmountPaid=0.0,
            DueDate=today - timedelta(days=5)
        ))
        
        for debt in debt_items:
            session.store(debt)
        session.save_changes()
        
        # Generate payments
        payments = []
        
        # Payment scenario 1: Multiple renters paying shares
        shared_lease = next((l for l in leases if len(l.RenterIds) > 1), None)
        if shared_lease:
            rent_debt = next((d for d in debt_items if d.LeaseId == shared_lease.Id and d.Type == "Rent" and d.AmountPaid > 0), None)
            if rent_debt and len(shared_lease.RenterIds) >= 2:
                renter1 = shared_lease.RenterIds[0]
                renter2 = shared_lease.RenterIds[1]
                share1 = rent_debt.AmountPaid / 2
                share2 = rent_debt.AmountPaid - share1
                
                payments.append(Payment(
                    PaymentDate=today - timedelta(days=random.randint(1, 60)),
                    TotalAmountReceived=rent_debt.AmountPaid,
                    PaymentMethods=[
                        PaymentMethod(Method="Card", Amount=share1, Details="VISA ****1234"),
                        PaymentMethod(Method="Check", Amount=share2, Details=f"Check #{random.randint(1000, 9999)}")
                    ],
                    Allocation=[
                        PaymentAllocation(DebtItemId=rent_debt.Id, AmountApplied=share1, RenterId=renter1),
                        PaymentAllocation(DebtItemId=rent_debt.Id, AmountApplied=share2, RenterId=renter2)
                    ]
                ))
        
        # Payment scenario 2: Single payment for multiple debts
        lease_with_multiple = next((l for l in leases if len([d for d in debt_items if d.LeaseId == l.Id and d.AmountPaid > 0]) >= 2), None)
        if lease_with_multiple:
            rent_debt = next((d for d in debt_items if d.LeaseId == lease_with_multiple.Id and d.Type == "Rent" and d.AmountPaid > 0), None)
            utility_debt = next((d for d in debt_items if d.LeaseId == lease_with_multiple.Id and d.Type == "Utility" and d.AmountPaid > 0), None)
            primary_renter = lease_with_multiple.RenterIds[0] if lease_with_multiple.RenterIds else None
            
            if rent_debt and utility_debt and primary_renter:
                total_amount = rent_debt.AmountPaid + utility_debt.AmountPaid
                payments.append(Payment(
                    PaymentDate=today - timedelta(days=random.randint(1, 60)),
                    TotalAmountReceived=total_amount,
                    PaymentMethods=[PaymentMethod(Method="Bank Transfer", Amount=total_amount, Details="ACH Transfer")],
                    Allocation=[
                        PaymentAllocation(DebtItemId=rent_debt.Id, AmountApplied=rent_debt.AmountPaid, RenterId=primary_renter),
                        PaymentAllocation(DebtItemId=utility_debt.Id, AmountApplied=utility_debt.AmountPaid, RenterId=primary_renter)
                    ]
                ))
        
        # Additional simple payments
        other_paid_debts = [d for d in debt_items if d.AmountPaid > 0 and not any(p for p in payments if any(a.DebtItemId == d.Id for a in p.Allocation))][:3]
        for debt in other_paid_debts:
            paying_renter = debt.RenterIds[0] if debt.RenterIds else None
            if paying_renter:
                method = random.choice(["Card", "Check"])
                details = "VISA ****1234" if method == "Card" else f"Check #{random.randint(1000, 9999)}"
                payments.append(Payment(
                    PaymentDate=today - timedelta(days=random.randint(1, 60)),
                    TotalAmountReceived=debt.AmountPaid,
                    PaymentMethods=[PaymentMethod(Method=method, Amount=debt.AmountPaid, Details=details)],
                    Allocation=[PaymentAllocation(DebtItemId=debt.Id, AmountApplied=debt.AmountPaid, RenterId=paying_renter)]
                ))
        
        for payment in payments:
            session.store(payment)
        session.save_changes()
        
        # Generate service requests
        service_requests = [
            ServiceRequest(UnitId=units[0].Id, PropertyId=units[0].PropertyId, RenterId=renters[0].Id,
                         Type="Plumbing", Description="Kitchen sink is leaking", Status="Open", 
                         OpenedAt=today - timedelta(days=2)),
            ServiceRequest(UnitId=units[1].Id, PropertyId=units[1].PropertyId, RenterId=renters[2].Id,
                         Type="Electrical", Description="Living room outlet not working", Status="Scheduled",
                         OpenedAt=today - timedelta(days=5)),
            ServiceRequest(UnitId=units[3].Id, PropertyId=units[3].PropertyId, RenterId=renters[3].Id,
                         Type="Package", Description="Package delivery notification", Status="Open",
                         OpenedAt=today - timedelta(hours=6)),
            ServiceRequest(UnitId=units[4].Id, PropertyId=units[4].PropertyId, RenterId=renters[5].Id,
                         Type="Maintenance", Description="Heating not working properly", Status="In Progress",
                         OpenedAt=today - timedelta(days=7)),
            ServiceRequest(UnitId=units[7].Id, PropertyId=units[7].PropertyId, RenterId=renters[8].Id,
                         Type="Domestic", Description="Noise complaint from neighbors", Status="Closed",
                         OpenedAt=today - timedelta(days=10), ClosedAt=today - timedelta(days=8)),
            ServiceRequest(UnitId=units[8].Id, PropertyId=units[8].PropertyId, RenterId=renters[10].Id,
                         Type="Other", Description="Request for parking space assignment", Status="Open",
                         OpenedAt=today - timedelta(days=1))
        ]
        
        for request in service_requests:
            session.store(request)
        session.save_changes()
        
        return {
            "Message": "Demo data generated successfully",
            "Properties": len(properties),
            "Units": len(units),
            "Renters": len(renters),
            "Leases": len(leases),
            "DebtItems": len(debt_items),
            "Payments": len(payments),
            "ServiceRequests": len(service_requests),
            "UtilityRecords": usage_records_generated
        }
