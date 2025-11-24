using Microsoft.AspNetCore.Mvc;
using PropertySphere.Models;
using Raven.Client.Documents.Session;
using Raven.Client.Documents.Operations.TimeSeries;
using Raven.Client.Documents.Queries.TimeSeries;
using Raven.Client.Documents.Linq;
using Raven.Client.Documents.Queries;
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

    [HttpGet("unit/{*unitId}")]
    public IActionResult GetUtilityUsage(string unitId, [FromQuery] DateTime? from, [FromQuery] DateTime? to)
    {
        var unit = _session.Load<Unit>(unitId);
        if (unit == null)
            return NotFound("Unit not found");

        var fromDate = from ?? DateTime.Today.AddMonths(-3);
        var toDate = to ?? DateTime.Today;

        var result = _session.Query<Unit>()
            .Where(u => u.Id == unitId)
            .Select(u => new
            {
                PowerUsage = RavenQuery.TimeSeries(u, "Power")
                    .Where(ts => ts.Timestamp >= fromDate && ts.Timestamp <= toDate)
                    .GroupBy(g => g.Hours(1))
                    .Select(g => g.Sum())
                    .ToList(),
                WaterUsage = RavenQuery.TimeSeries(u, "Water")
                    .Where(ts => ts.Timestamp >= fromDate && ts.Timestamp <= toDate)
                    .GroupBy(g => g.Hours(1))
                    .Select(g => g.Sum())
                    .ToList()
            })
            .FirstOrDefault();

        return Ok(new
        {
            UnitId = unitId,
            UnitNumber = unit.UnitNumber,
            From = fromDate,
            To = toDate,
            PowerUsage = result?.PowerUsage?.Results?.Select(r => new UsageDataPoint
            {
                Timestamp = r.From,
                Value = r.Sum[0],
            }).ToList() ?? new List<UsageDataPoint>(),
            WaterUsage = result?.WaterUsage?.Results?.Select(r => new UsageDataPoint
            {
                Timestamp = r.From,
                Value = r.Sum[0],
            }).ToList() ?? new List<UsageDataPoint>()
        });
    }

    private IActionResult UploadUtilityData(UtilityUploadRequest request, string timeSeriesName)
    {
        var unit = _session.Load<Unit>(request.UnitId);
        if (unit == null)
            return NotFound($"Unit {request.UnitId} not found");

        var ts = _session.TimeSeriesFor(request.UnitId, timeSeriesName);
        foreach (var entry in request.Entries)
        {
            ts.Append(entry.Timestamp, entry.Usage, entry.Tag);
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
}

public class TimeSeriesQueryResult
{
    public TimeSeriesRangeAggregation[]? Results { get; set; }
}
