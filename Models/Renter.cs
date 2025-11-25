namespace PropertySphere.Models;

public class Renter
{
    public string? Id { get; set; }
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string? TelegramChatId { get; set; }
    public string ContactEmail { get; set; } = string.Empty;
    public string ContactPhone { get; set; } = string.Empty;
    public List<CreditCard> CreditCards { get; set; } = new();
}

public class CreditCard
{
    public string Last4Digits { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty; // Visa, MasterCard, Amex, Discover
    public string Expiration { get; set; } = string.Empty; // MM/YY format
}
