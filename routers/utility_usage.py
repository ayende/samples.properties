"""API router for utility usage"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_session
from models import Unit

router = APIRouter()


# Request/Response Models
class UtilityEntry(BaseModel):
    Timestamp: datetime
    Usage: float
    Tag: Optional[str] = None


class UtilityUploadRequest(BaseModel):
    UnitId: str
    Entries: List[UtilityEntry]


class CsvUploadRequest(BaseModel):
    CsvData: str


class UsageDataPoint(BaseModel):
    Timestamp: datetime
    Value: float


@router.post("/upload-power")
async def upload_power_usage(request: UtilityUploadRequest):
    """Upload power usage data"""
    return await upload_utility_data(request, "Power")


@router.post("/upload-water")
async def upload_water_usage(request: UtilityUploadRequest):
    """Upload water usage data"""
    return await upload_utility_data(request, "Water")


@router.post("/upload-power-csv")
async def upload_power_usage_csv(request: CsvUploadRequest):
    """Upload power usage from CSV data"""
    return await upload_utility_data_from_csv(request.CsvData, "Power")


@router.post("/upload-water-csv")
async def upload_water_usage_csv(request: CsvUploadRequest):
    """Upload water usage from CSV data"""
    return await upload_utility_data_from_csv(request.CsvData, "Water")


@router.get("/unit/{unit_id:path}")
async def get_utility_usage(
    unit_id: str,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
):
    """Get utility usage for a unit"""
    async with get_session() as session:
        unit = session.load(unit_id, object_type=Unit)
        if not unit:
            raise HTTPException(status_code=404, detail="Unit not found")
        
        # Set default date range (last 3 months)
        from_dt = from_date if from_date else datetime.today() - timedelta(days=90)
        to_dt = to_date if to_date else datetime.today()
        
        # Get time series data for power and water
        power_ts = session.time_series_for(unit_id, "Power")
        water_ts = session.time_series_for(unit_id, "Water")
        
        power_entries = power_ts.get(from_dt, to_dt) if power_ts else []
        water_entries = water_ts.get(from_dt, to_dt) if water_ts else []
        
        # Convert to data points
        power_usage = [
            UsageDataPoint(Timestamp=entry.Timestamp, Value=entry.Value)
            for entry in (power_entries or [])
        ]
        water_usage = [
            UsageDataPoint(Timestamp=entry.Timestamp, Value=entry.Value)
            for entry in (water_entries or [])
        ]
        
        return {
            "UnitId": unit_id,
            "UnitNumber": unit.UnitNumber,
            "From": from_dt.date(),
            "To": to_dt.date(),
            "PowerUsage": power_usage,
            "WaterUsage": water_usage
        }


async def upload_utility_data(request: UtilityUploadRequest, time_series_name: str):
    """Upload utility usage data for a unit"""
    async with get_session() as session:
        unit = session.load(request.UnitId, object_type=Unit)
        if not unit:
            raise HTTPException(status_code=404, detail=f"Unit {request.UnitId} not found")
        
        ts = session.time_series_for(request.UnitId, time_series_name)
        
        for entry in request.Entries:
            ts.append(entry.Timestamp, entry.Usage, entry.Tag)
        
        session.save_changes()
        
        return {
            "Message": f"Uploaded {len(request.Entries)} {time_series_name} readings for unit {request.UnitId}"
        }


async def upload_utility_data_from_csv(csv_data: str, time_series_name: str):
    """Upload utility usage data from CSV format"""
    async with get_session() as session:
        lines = csv_data.strip().split('\n')
        record_count = 0
        errors = []
        
        # Skip header row
        for line in lines[1:]:
            if not line.strip():
                continue
            
            parts = line.split(',')
            if len(parts) < 3:
                errors.append(f"Invalid line: {line}")
                continue
            
            unit_id = parts[0].strip()
            timestamp_str = parts[1].strip()
            usage_str = parts[2].strip()
            
            # Parse timestamp
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
            except ValueError:
                errors.append(f"Invalid timestamp in line: {line}")
                continue
            
            # Parse usage value
            try:
                usage = float(usage_str)
            except ValueError:
                errors.append(f"Invalid usage value in line: {line}")
                continue
            
            # Verify unit exists
            unit = session.load(unit_id, object_type=Unit)
            if not unit:
                errors.append(f"Unit not found: {unit_id}")
                continue
            
            # Append to time series
            ts = session.time_series_for(unit_id, time_series_name)
            ts.append(timestamp, usage)
            record_count += 1
        
        session.save_changes()
        
        return {
            "Message": f"Uploaded {record_count} {time_series_name} readings",
            "RecordsProcessed": record_count,
            "Errors": errors
        }
