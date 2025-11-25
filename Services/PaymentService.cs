using PropertySphere.Models;
using Raven.Client.Documents.Session;

namespace PropertySphere.Services;

public class PaymentService
{
    public static async Task ProcessPaymentAsync(
        IAsyncDocumentSession session,
        Payment payment,
        CancellationToken cancellationToken = default)
    {
        await session.StoreAsync(payment, cancellationToken);

        var debtItems = await session.LoadAsync<DebtItem>(
            payment.Allocation.Select(x => x.DebtItemId),
            cancellationToken);

        foreach (var allocation in payment.Allocation)
        {
            if (!debtItems.TryGetValue(allocation.DebtItemId, out var debtItem) || debtItem == null)
            {
                throw new InvalidOperationException($"Debt item {allocation.DebtItemId} not found.");
            }

            debtItem.AmountPaid += allocation.AmountApplied;
        }

        // Here we pretend to actually charge the card :-)

        await session.SaveChangesAsync(cancellationToken);
    }

    public static async Task<decimal> CreatePaymentForDebtsWithCardAsync(
        IAsyncDocumentSession session,
        string renterId,
        string[] debtItemIds,
        CreditCard card,
        string paymentMethod,
        CancellationToken cancellationToken = default)
    {
        var debtItems = await session.LoadAsync<DebtItem>(debtItemIds, cancellationToken);
        var totalAmount = 0m;
        var missingDebts = new List<string>();

        foreach (var debtId in debtItemIds)
        {
            if (!debtItems.TryGetValue(debtId, out var debt) || debt == null)
            {
                missingDebts.Add(debtId);
                continue;
            }

            // Verify this debt belongs to the renter
            if (!debt.RenterIds.Contains(renterId))
            {
                throw new InvalidOperationException($"Debt item {debtId} does not belong to you.");
            }

            var amountDue = debt.AmountDue - debt.AmountPaid;
            totalAmount += amountDue;
        }

        if (missingDebts.Any())
        {
            throw new InvalidOperationException($"Debt items not found: {string.Join(", ", missingDebts)}");
        }

        // Create payment record
        var payment = new Payment
        {
            PaymentDate = DateTime.UtcNow,
            TotalAmountReceived = totalAmount,
            PaymentMethods = new List<PaymentMethod>
            {
                new PaymentMethod
                {
                    Method = paymentMethod,
                    Amount = totalAmount,
                    Details = $"{card.Type} ****{card.Last4Digits}"
                }
            },
            Allocation = debtItemIds.Select(debtId =>
            {
                var debt = debtItems[debtId];
                var amountDue = debt.AmountDue - debt.AmountPaid;
                return new PaymentAllocation
                {
                    DebtItemId = debtId,
                    AmountApplied = amountDue,
                    RenterId = renterId
                };
            }).ToList()
        };

        await ProcessPaymentAsync(session, payment, cancellationToken);
        return totalAmount;
    }
}
