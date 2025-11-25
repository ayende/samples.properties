using Newtonsoft.Json;
using Raven.Client.Documents;
using Raven.Client.Documents.Operations.AI.Agents;

namespace PropertySphere.Services;

public static class PropertyAgent
{
    public const string AgentId = "property-assistant";
    public class Reply
    {
        public string Answer { get; set; } = string.Empty;
        public string[] Followups { get; set; } = [];
    }

    public class CreateServiceRequestArgs
    {
        required public string Type { get; set; }
        required public string Description { get; set; }
    }

    public class ChargeCardArgs
    {
        required public string[] DebtItemIds { get; set; }
        required public string PaymentMethod { get; set; }
        required public string Card { get; set; }
    }

    public static void Create(IDocumentStore store)
    {
        store.AI.CreateAgent(
            new AiAgentConfiguration
            {
                Name = "Property Assistant",
                Identifier = AgentId,
                ConnectionStringName = "Property Management AI Model",
                SystemPrompt = """
                    You are a property management assistant for renters.
                    Provide information about rent, utilities, debts, service requests, and property details.
                    Be professional, helpful, and responsive to renter needs.

                    You can answer in markdown format, make sure to use ticks (`) whenever you discuss identifiers.
                    Do not suggest actions that are not explicitly allowed by the tools available to you.

                    Do NOT discuss non-property topics. Answer only for the current renter.
                    When discussing amounts, always format them as currency with 2 decimal places.
                    """,
                Parameters = [
                    new AiAgentParameter("currentDate", "Current date in yyyy-MM-dd format"),

                    // scope of the agent, not visible to the model directly
                    new AiAgentParameter("renterId", "Renter ID; answer only for this renter", sendToModel: false),
                    new AiAgentParameter("renterUnits", "List of unit IDs occupied by the renter", sendToModel: false),
                ],
                SampleObject = JsonConvert.SerializeObject(new Reply
                {
                    Answer = "Detailed answer to query",
                    Followups = ["Likely follow-ups"],
                }),
                Queries = [
                    new AiAgentToolQuery
                    {
                        Name = "GetRenterInfo",
                        Description = "Retrieve renter profile details",
                        Query = "from Renters where id() = $renterId",
                        ParametersSampleObject = "{}",
                        Options = new AiAgentToolQueryOptions
                        {
                            AllowModelQueries = false,
                            AddToInitialContext = true
                        }
                    },
                    new AiAgentToolQuery
                    {
                        Name = "GetActiveLeases",
                        Description = "Retrieve renter's current active leases details including rent amount and utility pricing",
                        Query = """
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
                                RentAmount: l.RentAmount,
                                UtilityPricing: l.UtilityPricing,
                                UnitNumber: u.UnitNumber,
                                PropertyName: p.Name,
                                PropertyAddress: p.Address,
                                Renters: r.map(x=> x.FirstName + " " + x.LastName)
                            }
                            limit 10
                            """,
                        ParametersSampleObject = "{}"
                    },
                    new AiAgentToolQuery
                    {
                        Name = "GetOutstandingDebts",
                        Description = "Retrieve renter's outstanding debts (unpaid balances)",
                        Query = """
                            from index 'DebtItems/Outstanding'
                            where RenterIds in ($renterId) and AmountOutstanding > 0
                            order by DueDate asc
                            limit 10
                            """,
                        ParametersSampleObject = "{}"
                    },
                    new AiAgentToolQuery
                    {
                        Name = "GetRecentPayments",
                        Description = "Retrieve renter's recent payments",
                        Query = """
                            from "Payments" 
                            where Allocation[].RenterId = $renterId
                            order by PaymentDate desc
                            limit 12
                            """,
                        ParametersSampleObject = "{}"
                    },
                    new AiAgentToolQuery
                    {
                        Name = "GetUtilityUsage",
                        Description = "Retrieve utility usage for renter's unit within a date range (for calculating bills)",
                        Query = """
                            from 'Units'
                            where id() in ($renterUnits)
                            select 
                                timeseries(from 'Power' between $startDate and $endDate group by 1d select sum()),
                                timeseries(from 'Water' between $startDate and $endDate group by 1d select sum())
                            """,
                        ParametersSampleObject = "{\"startDate\": \"yyyy-MM-dd\", \"endDate\": \"yyyy-MM-dd\"}"
                    },
                    new AiAgentToolQuery
                    {
                        Name = "SearchServiceRequests",
                        Description = "Semantic search for renter's service requests",
                        Query = """
                            from ServiceRequests
                            where RenterId = $renterId
                                and vector.search(embedding.text(Description), $query)
                            order by OpenedAt desc
                            limit 5
                            """,
                        ParametersSampleObject = "{\"query\": [\"query terms to find matching service request\"]}"
                    }
                ],
                Actions = [
                    new AiAgentToolAction
                    {
                        Name = "CreateServiceRequest",
                        Description = "Create a new service request for the renter's unit",
                        ParametersSampleObject = JsonConvert.SerializeObject(new CreateServiceRequestArgs
                        {
                            Type = "Maintenance | Repair | Plumbing | Electrical | HVAC | Appliance | Community | Neighbors | Other",
                            Description = "Detailed description of the issue with all relevant context"
                        })
                    },
                    new AiAgentToolAction
                    {
                        Name = "ChargeCard",
                        Description = "Record a payment for one or more outstanding debts. The renter can pay multiple debt items in a single transaction. Can pay using any stored card on file.",
                        ParametersSampleObject = JsonConvert.SerializeObject(new ChargeCardArgs
                        {
                            DebtItemIds = ["debtitems/1-A", "debtitems/2-A"],
                            PaymentMethod = "Card",
                            Card = "Last 4 digits of the card"
                        })
                    }
                ]
            });
    }
}
