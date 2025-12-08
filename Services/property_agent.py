"""Property AI Agent configuration"""
import json
from dataclasses import dataclass
from ravendb.documents.operations.ai.agents.ai_agent_configuration import (
    AiAgentConfiguration,
    AiAgentToolQuery,
    AiAgentToolAction,
    AiAgentPersistenceConfiguration
)


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
        
        agent_config = AiAgentConfiguration(
            name="Property Assistant",
            identifier=cls.AGENT_ID,
            connection_string_name="Property Management AI Model",
            system_prompt="""
You are a property management assistant for renters.
Provide information about rent, utilities, debts, service requests, and property details.
Be professional, helpful, and responsive to renter needs.

You can answer in markdown format, make sure to use ticks (`) whenever you discuss identifiers.
Do not suggest actions that are not explicitly allowed by the tools available to you.

DO NOT discuss non-property topics. Answer only for the current renter.
When discussing amounts, always format them as currency with 2 decimal places.
""",
            parameters={"currentDate", "renterId", "renterUnits"},
            sample_object=json.dumps({
                "Answer": "Detailed answer to query",
                "Followups": ["Likely follow-ups"]
            }),
            queries=[
                AiAgentToolQuery(
                    name="GetRenterInfo",
                    description="Retrieve renter profile details",
                    query="from Renters where id() = $renterId",
                    parameters_sample_object="{}"
                ),
                AiAgentToolQuery(
                    name="GetActiveLeases",
                    description="Retrieve renter's current active leases",
                    query="""
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
                    parameters_sample_object="{}"
                ),
                AiAgentToolQuery(
                    name="GetOutstandingDebts",
                    description="Retrieve renter's outstanding debts",
                    query="""
from index 'DebtItems/Outstanding'
where RenterIds in ($renterId) and AmountOutstanding > 0
order by DueDate asc
limit 10
""",
                    parameters_sample_object="{}"
                ),
                AiAgentToolQuery(
                    name="GetRecentPayments",
                    description="Retrieve renter's recent payments",
                    query="""
from "Payments" 
where Allocation[].RenterId = $renterId
order by PaymentDate desc
limit 12
""",
                    parameters_sample_object="{}"
                ),
                AiAgentToolQuery(
                    name="SearchServiceRequests",
                    description="Semantic search for renter's service requests",
                    query="""
from ServiceRequests
where RenterId = $renterId
    and vector.search(embedding.text(Description), $query)
order by OpenedAt desc
limit 5
""",
                    parameters_sample_object='{"query": ["query terms to find matching service request"]}'
                )
            ],
            actions=[
                AiAgentToolAction(
                    name="CreateServiceRequest",
                    description="Create a new service request",
                    parameters_sample_object=json.dumps({
                        "Type": "Maintenance | Repair | Plumbing | Electrical | HVAC | Appliance | Community | Neighbors | Other",
                        "Description": "Detailed description of the issue"
                    })
                ),
                AiAgentToolAction(
                    name="ChargeCard",
                    description="Record a payment for outstanding debts",
                    parameters_sample_object=json.dumps({
                        "DebtItemIds": ["debtitems/1-A", "debtitems/2-A"],
                        "PaymentMethod": "Card",
                        "Card": "Last 4 digits of the card"
                    })
                )
            ]
        )
        
        store.ai.add_or_update_agent(agent_config)
