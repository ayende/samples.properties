"""Property AI Agent configuration"""
import json
from dataclasses import dataclass


@dataclass
class Reply:
    """AI agent reply structure"""
    answer: str = ""
    followups: list[str] = None
    
    def __post_init__(self):
        if self.followups is None:
            self.followups = []


@dataclass
class CreateServiceRequestArgs:
    """Arguments for creating a service request"""
    type: str
    description: str


@dataclass
class ChargeCardArgs:
    """Arguments for charging a card"""
    debt_item_ids: list[str]
    payment_method: str
    card: str


class PropertyAgent:
    """Property management AI agent"""
    
    AGENT_ID = "property-assistant"
    
    @classmethod
    def create(cls, store):
        """Create and configure the Property AI Agent in RavenDB"""
        # Note: This is a placeholder for the actual RavenDB AI agent configuration
        # The actual implementation would use store.ai.create_agent() once
        # the Python RavenDB client supports AI agents
        
        agent_config = {
            "name": "Property Assistant",
            "identifier": cls.AGENT_ID,
            "connectionStringName": "Property Management AI Model",
            "systemPrompt": """
You are a property management assistant for renters.
Provide information about rent, utilities, debts, service requests, and property details.
Be professional, helpful, and responsive to renter needs.

You can answer in markdown format, make sure to use ticks (`) whenever you discuss identifiers.
Do not suggest actions that are not explicitly allowed by the tools available to you.

Do NOT discuss non-property topics. Answer only for the current renter.
When discussing amounts, always format them as currency with 2 decimal places.
""",
            "parameters": [
                {"name": "currentDate", "description": "Current date in yyyy-MM-dd format"},
                {"name": "renterId", "description": "Renter ID; answer only for this renter", "sendToModel": False},
                {"name": "renterUnits", "description": "List of unit IDs occupied by the renter", "sendToModel": False},
            ],
            "sampleObject": json.dumps({
                "Answer": "Detailed answer to query",
                "Followups": ["Likely follow-ups"]
            }),
            "queries": [
                {
                    "name": "GetRenterInfo",
                    "description": "Retrieve renter profile details",
                    "query": "from Renters where id() = $renterId",
                    "parametersSampleObject": "{}",
                    "options": {
                        "allowModelQueries": False,
                        "addToInitialContext": True
                    }
                },
                {
                    "name": "GetActiveLeases",
                    "description": "Retrieve renter's current active leases",
                    "query": """
from Leases as l
where l.RenterIds in ($renterId)
    and l.StartDate <= $currentDate
    and l.EndDate >= $currentDate
load l.UnitId as u, u.PropertyId as p, l.RenterIds as r[]
select {
    LeaseAmount: l.LeaseAmount,
    PowerUnitPrice: l.PowerUnitPrice,
    WaterUnitPrice: l.WaterUnitPrice,
    StartDate: l.StartDate,
    EndDate: l.EndDate,
    UnitNumber: u.UnitNumber,
    PropertyName: p.Name,
    PropertyAddress: p.Address,
    Renters: r.map(x=> x.FirstName + " " + x.LastName)
}
limit 10
""",
                    "parametersSampleObject": "{}"
                },
                {
                    "name": "GetOutstandingDebts",
                    "description": "Retrieve renter's outstanding debts",
                    "query": """
from index 'DebtItems/Outstanding'
where RenterIds in ($renterId) and AmountOutstanding > 0
order by DueDate asc
limit 10
""",
                    "parametersSampleObject": "{}"
                },
                {
                    "name": "GetRecentPayments",
                    "description": "Retrieve renter's recent payments",
                    "query": """
from "Payments" 
where Allocation[].RenterId = $renterId
order by PaymentDate desc
limit 12
""",
                    "parametersSampleObject": "{}"
                },
                {
                    "name": "SearchServiceRequests",
                    "description": "Semantic search for renter's service requests",
                    "query": """
from ServiceRequests
where RenterId = $renterId
    and vector.search(embedding.text(Description), $query)
order by OpenedAt desc
limit 5
""",
                    "parametersSampleObject": '{"query": ["query terms to find matching service request"]}'
                }
            ],
            "actions": [
                {
                    "name": "CreateServiceRequest",
                    "description": "Create a new service request",
                    "parametersSampleObject": json.dumps({
                        "Type": "Maintenance | Repair | Plumbing | Electrical | HVAC | Appliance | Community | Neighbors | Other",
                        "Description": "Detailed description of the issue"
                    })
                },
                {
                    "name": "ChargeCard",
                    "description": "Record a payment for outstanding debts",
                    "parametersSampleObject": json.dumps({
                        "DebtItemIds": ["debtitems/1-A", "debtitems/2-A"],
                        "PaymentMethod": "Card",
                        "Card": "Last 4 digits of the card"
                    })
                }
            ]
        }
        
        # This would be: store.ai.create_agent(agent_config)
        # For now, just store the configuration
        print(f"Property Agent configured: {agent_config['name']}")
        return agent_config
