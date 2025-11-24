using Microsoft.AspNetCore.Mvc;
using PropertySphere.Models;
using Raven.Client.Documents.Session;
using Raven.Client.Documents.Operations.TimeSeries;
using System.Globalization;

namespace PropertySphere.Controllers;

[ApiController]
[Route("api/[controller]")]
public class UtilityUsageController : ControllerBase
{
    private readonly IDocumentSession _session;

    public UtilityUsageController(IDocumentSession session)
    {
        _session = session;
    }

    [HttpPost("upload-power")]
    public IActionResult UploadPowerUsage([FromBody] UtilityUploadRequest request)
    {
        return UploadUtilityData(request, "Power");
    }

    [HttpPost("upload-water")]
    public IActionResult UploadWaterUsage([FromBody] UtilityUploadRequest request)
    {
        return UploadUtilityData(request, "Water");
    }

    [HttpPost("upload-power-csv")]
    public IActionResult UploadPowerUsageCsv([FromBody] CsvUploadRequest request)
    {
        return UploadUtilityDataFromCsv(request.CsvData, "Power");
    }

    [HttpPost("upload-water-csv")]
    public IActionResult UploadWaterUsageCsv([FromBody] CsvUploadRequest request)
    {
        return UploadUtilityDataFromCsv(request.CsvData, "Water");
    }

    [HttpGet("unit/{unitId}")]
    public IActionResult GetUtilityUsage(string unitId, [FromQuery] DateTime? from, [FromQuery] DateTime? to)
    {
        var unit = _session.Load<Unit>(unitId);
        if (unit == null)
            return NotFound("Unit not found");

        var fromDate = from ?? DateTime.Today.AddMonths(-3);
        var toDate = to ?? DateTime.Today;

        var powerUsage = _session.TimeSeriesFor(unitId, "Power")
            .Get(fromDate, toDate)?
            .Select(entry => new UsageDataPoint
            {
                Timestamp = entry.Timestamp,
                Value = entry.Value,
                Tag = entry.Tag
            })
            .ToList() ?? new List<UsageDataPoint>();

        var waterUsage = _session.TimeSeriesFor(unitId, "Water")
            .Get(fromDate, toDate)?
            .Select(entry => new UsageDataPoint
            {
                Timestamp = entry.Timestamp,
                Value = entry.Value,
                Tag = entry.Tag
            })
            .ToList() ?? new List<UsageDataPoint>();

        return Ok(new
        {
            UnitId = unitId,
            UnitNumber = unit.UnitNumber,
            From = fromDate,
            To = toDate,
            PowerUsage = powerUsage,
            WaterUsage = waterUsage
        });
    }

    private IActionResult UploadUtilityData(UtilityUploadRequest request, string timeSeriesName)
    {
        var unit = _session.Load<Unit>(request.UnitId);
        if (unit == null)
            return NotFound($"Unit {request.UnitId} not found");

        foreach (var entry in request.Entries)
        {
            _session.TimeSeriesFor(request.UnitId, timeSeriesName)
                .Append(entry.Timestamp, entry.Usage, entry.Tag);
        }

        _session.SaveChanges();

        return Ok(new { Message = $"Uploaded {request.Entries.Count} {timeSeriesName} readings for unit {request.UnitId}" });
    }

    private IActionResult UploadUtilityDataFromCsv(string csvData, string timeSeriesName)
    {
        var lines = csvData.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        var recordCount = 0;
        var errors = new List<string>();

        foreach (var line in lines.Skip(1)) // Skip header
        {
            var parts = line.Split(',');
            if (parts.Length < 3)
            {
                errors.Add($"Invalid line: {line}");
                continue;
            }

            var unitId = parts[0].Trim();

            if (!DateTime.TryParse(parts[1].Trim(), out DateTime timestamp))
            {
                errors.Add($"Invalid timestamp in line: {line}");
                continue;
            }

            if (!double.TryParse(parts[2].Trim(), NumberStyles.Any, CultureInfo.InvariantCulture, out double usage))
            {
                errors.Add($"Invalid usage value in line: {line}");
                continue;
            }

            var unit = _session.Load<Unit>(unitId);
            if (unit == null)
            {
                errors.Add($"Unit not found: {unitId}");
                continue;
            }

            _session.TimeSeriesFor(unitId, timeSeriesName).Append(timestamp, usage);
            recordCount++;
        }

        _session.SaveChanges();

        return Ok(new
        {
            Message = $"Uploaded {recordCount} {timeSeriesName} readings",
            RecordsProcessed = recordCount,
            Errors = errors
        });
    }
}

public class UtilityUploadRequest
{
    public string UnitId { get; set; } = string.Empty;
    public List<UtilityEntry> Entries { get; set; } = new();
}

public class UtilityEntry
{
    public DateTime Timestamp { get; set; }
    public double Usage { get; set; }
    public string? Tag { get; set; }
}

public class CsvUploadRequest
{
    public string CsvData { get; set; } = string.Empty;
}

public class UsageDataPoint
{
    public DateTime Timestamp { get; set; }
    public double Value { get; set; }
    public string? Tag { get; set; }
}
