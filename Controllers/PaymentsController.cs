using Microsoft.AspNetCore.Mvc;
using PropertySphere.Models;
using PropertySphere.Services;
using Raven.Client.Documents.Session;

namespace PropertySphere.Controllers;

[ApiController]
[Route("api/[controller]")]
public class PaymentsController : ControllerBase
{
    private readonly IAsyncDocumentSession _session;

    public PaymentsController(IAsyncDocumentSession session)
    {
        _session = session;
    }

    [HttpPost]
    public async Task<IActionResult> Create([FromBody] Payment payment)
    {
        try
        {
            await PaymentService.ProcessPaymentAsync(_session, payment);
            return Ok(payment);
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(ex.Message);
        }
    }
}
