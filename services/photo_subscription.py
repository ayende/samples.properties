"""Photo Analysis Subscription Service"""
from ravendb import DocumentStore
from ravendb.documents.subscriptions.document_subscriptions import SubscriptionCreationOptions


class PhotoSubscription:
    """Subscription for photo analysis notifications"""
    
    SUBSCRIPTION_NAME = "After Photos Analysis"
    
    @classmethod
    def create(cls, store: DocumentStore):
        """Create the photo analysis subscription if it doesn't exist"""
        try:
            # Try to get existing subscription
            existing = store.subscriptions.get_subscription_state(cls.SUBSCRIPTION_NAME)
            if existing:
                print(f"Subscription '{cls.SUBSCRIPTION_NAME}' already exists")
                return
        except Exception:
            # Subscription doesn't exist, create it
            pass
        
        store.subscriptions.create_for_options(
            SubscriptionCreationOptions(
                name=cls.SUBSCRIPTION_NAME,
                query='from "Photos" where Description != null'
            )
        )
