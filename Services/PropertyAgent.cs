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

    public static Task Create(IDocumentStore store)
    {
        return store.AI.CreateAgentAsync(
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
                Parameters = [new AiAgentParameter("renterId", "Renter ID; answer only for this renter")],
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
                    // new AiAgentToolQuery
                    // {
                    //     Name = "GetActiveLeases",
                    //     Description = "Retrieve renter's current active leases details including rent amount and utility pricing",
                    //     Query = """
                    //         from Leases 
                    //         where RenterIds = ($renterId)
                    //             and StartDate <= today() 
                    //             and EndDate >= today()
                    //         select Id, UnitId, LeaseAmount, StartDate, EndDate, 
                    //                PowerUnitPrice, WaterUnitPrice, LegalDocumentId
                    //         limit 10
                    //         """,
                    //     ParametersSampleObject = "{}"
                    // },
                    // new AiAgentToolQuery
                    // {
                    //     Name = "GetOutstandingDebts",
                    //     Description = "Retrieve renter's outstanding debts (unpaid balances)",
                    //     Query = """
                    //         from DebtItems 
                    //         where $renterId in RenterIds 
                    //             and AmountDue > AmountPaid
                    //         order by DueDate asc
                    //         select Id, Type, Description, AmountDue, AmountPaid, DueDate, UnitId
                    //         limit 10
                    //         """,
                    //     ParametersSampleObject = "{}"
                    // },
                    // new AiAgentToolQuery
                    // {
                    //     Name = "GetRecentPayments",
                    //     Description = "Retrieve renter's recent payments",
                    //     Query = """
                    //         from Payments 
                    //         where RenterId = $renterId
                    //         order by PaymentDate desc
                    //         select PaymentDate, Amount, Method, ReferenceNumber, Allocations
                    //         limit 5
                    //         """,
                    //     ParametersSampleObject = "{}"
                    // },
                    // new AiAgentToolQuery
                    // {
                    //     Name = "GetUtilityUsage",
                    //     Description = "Retrieve utility usage for renter's unit within a date range (for calculating bills)",
                    //     Query = """
                    //         declare timeseries usage(u) {
                    //             from u.Power between $startDate and $endDate
                    //             group by '1 hour'
                    //             select sum()
                    //         }
                    //         from Units as u
                    //         where exists(
                    //             from Leases as l
                    //             where l.UnitId = id(u) 
                    //                 and $renterId in l.RenterIds
                    //                 and l.StartDate <= today()
                    //                 and l.EndDate >= today()
                    //         )
                    //         select id() as UnitId, usage(u) as PowerUsage
                    //         limit 1
                    //         """,
                    //     ParametersSampleObject = "{\"startDate\": \"yyyy-MM-dd\", \"endDate\": \"yyyy-MM-dd\"}"
                    // },
                    // new AiAgentToolQuery
                    // {
                    //     Name = "GetServiceRequests",
                    //     Description = "Retrieve renter's service requests",
                    //     Query = """
                    //         from ServiceRequests 
                    //         where RenterId = $renterId
                    //         order by OpenedAt desc
                    //         select Id, Type, Description, Status, OpenedAt, ClosedAt, UnitId
                    //         limit 10
                    //         """,
                    //     ParametersSampleObject = "{}"
                    // },
                    // new AiAgentToolQuery
                    // {
                    //     Name = "SearchServiceRequests",
                    //     Description = "Semantic search for renter's service requests",
                    //     Query = """
                    //         from ServiceRequests
                    //         where RenterId = $renterId
                    //             and (vector.search(embedding.text(Type), $query) or vector.search(embedding.text(Description), $query))
                    //         order by OpenedAt desc
                    //         select Id, Type, Description, Status, OpenedAt, ClosedAt, UnitId
                    //         limit 5
                    //         """,
                    //     ParametersSampleObject = "{\"query\": [\"query terms to find matching service request\"]}"
                    // }
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
                    }
                ]
            });
    }
}
