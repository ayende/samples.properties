namespace PropertySphere.Models;

public record Photo
{
    public string? Id { get; set; }
    public string? RenterId { get; set; }
    public string? Caption { get; set; }

    public string? Description { get; set; }
    public required string ConversationId { get; set; }
    public DateTime UploadedAt { get; set; } = DateTime.UtcNow;
}