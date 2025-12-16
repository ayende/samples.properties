using Raven.Client.Documents;
using Raven.Client.Documents.Subscriptions;
using Raven.Client.Exceptions.Documents.Subscriptions;

namespace PropertySphere.Services;

public static class PhotoSubscription
{
    private const string SubscriptionName = "After Photos Analysis";

    public static void Create(IDocumentStore store)
    {
        try
        {
            store.Subscriptions.GetSubscriptionState(SubscriptionName);
            Console.WriteLine($"Subscription '{SubscriptionName}' already exists");
            return;
        }
        catch (SubscriptionDoesNotExistException)
        {
            // Subscription doesn't exist, create it
        }

        store.Subscriptions.Create(new SubscriptionCreationOptions
        {
            Name = SubscriptionName,
            Query = """
                from "Photos" 
                where Description != null
                """
        });
    }
}
