namespace PropertySphere.Models;

public class Payment
{
    public string? Id { get; set; }
    public DateTime PaymentDate { get; set; }
    public decimal TotalAmountReceived { get; set; }
    public List<PaymentMethod> PaymentMethods { get; set; } = new();
    public List<PaymentAllocation> Allocation { get; set; } = new();
}

public class PaymentMethod
{
    public string Method { get; set; } = string.Empty;
    public decimal Amount { get; set; }
    public string Details { get; set; } = string.Empty;
}

public class PaymentAllocation
{
    public string DebtItemId { get; set; } = string.Empty;
    public decimal AmountApplied { get; set; }
    public string RenterId { get; set; } = string.Empty;
}
