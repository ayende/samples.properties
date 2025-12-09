"""Get Ongoing Task Info Operation for retrieving detailed information about ongoing tasks"""
import json
from typing import TYPE_CHECKING, Optional
import requests

from ravendb.documents.operations.definitions import MaintenanceOperation
from ravendb.http.raven_command import RavenCommand
from ravendb.http.server_node import ServerNode
from ravendb.tools.utils import Utils

if TYPE_CHECKING:
    from ravendb.documents.conventions import DocumentConventions


class OngoingTaskType:
    """Enum for ongoing task types"""
    REPLICATION = "Replication"
    RAVEN_ETL = "RavenEtl"
    SQL_ETL = "SqlEtl"
    OLAP_ETL = "OlapEtl"
    ELASTIC_SEARCH_ETL = "ElasticSearchEtl"
    QUEUE_ETL = "QueueEtl"
    SNOWFLAKE_ETL = "SnowflakeEtl"
    BACKUP = "Backup"
    SUBSCRIPTION = "Subscription"
    PULL_REPLICATION_AS_SINK = "PullReplicationAsSink"
    PULL_REPLICATION_AS_HUB = "PullReplicationAsHub"
    QUEUE_SINK = "QueueSink"
    EMBEDDINGS_GENERATION = "EmbeddingsGeneration"
    GEN_AI = "GenAi"


class GetOngoingTaskInfoOperation(MaintenanceOperation[dict]):
    """
    Operation to retrieve detailed information about a specific ongoing task.
    Ongoing tasks include various types of tasks such as replication, ETL, backup, and subscriptions.
    """
    
    def __init__(self, task_name_or_id, task_type: str):
        """
        Initialize the operation with either task name or task ID.
        
        Args:
            task_name_or_id: Either the task name (str) or task ID (int)
            task_type: The type of the ongoing task (use OngoingTaskType constants)
        """
        if isinstance(task_name_or_id, str):
            if not task_name_or_id or task_name_or_id.isspace():
                raise ValueError("Task name cannot be empty or whitespace")
            self._task_name = task_name_or_id
            self._task_id = None
        elif isinstance(task_name_or_id, int):
            self._task_name = None
            self._task_id = task_name_or_id
        else:
            raise TypeError("task_name_or_id must be either str or int")
        
        self._task_type = task_type
        
        if task_type == OngoingTaskType.PULL_REPLICATION_AS_HUB:
            raise ValueError(
                "PullReplicationAsHub type is not supported. "
                "Please use GetPullReplicationTasksInfoOperation instead."
            )
    
    def get_command(self, conventions: "DocumentConventions") -> RavenCommand[dict]:
        """Get the command for this operation"""
        if self._task_name is not None:
            return self.GetOngoingTaskInfoCommand(self._task_name, self._task_type)
        return self.GetOngoingTaskInfoCommand(self._task_id, self._task_type)
    
    class GetOngoingTaskInfoCommand(RavenCommand[dict]):
        """Command to get ongoing task information"""
        
        def __init__(self, task_name_or_id, task_type: str):
            super().__init__(dict)
            
            if isinstance(task_name_or_id, str):
                if not task_name_or_id or task_name_or_id.isspace():
                    raise ValueError("Task name cannot be empty or whitespace")
                self._task_name = task_name_or_id
                self._task_id = None
            else:
                self._task_name = None
                self._task_id = task_name_or_id
            
            self._task_type = task_type
        
        def create_request(self, node: ServerNode) -> requests.Request:
            """Create the HTTP request"""
            if self._task_name is not None:
                url = (
                    f"{node.url}/databases/{node.database}/task"
                    f"?taskName={Utils.quote_key(self._task_name)}&type={self._task_type}"
                )
            else:
                url = (
                    f"{node.url}/databases/{node.database}/task"
                    f"?key={self._task_id}&type={self._task_type}"
                )
            
            return requests.Request("GET", url)
        
        def set_response(self, response: Optional[str], from_cache: bool) -> None:
            """Set the response from the server"""
            if response is not None:
                self.result = json.loads(response)
        
        def is_read_request(self) -> bool:
            """This is not a read request"""
            return False
