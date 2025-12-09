"""Update GenAI operation for RavenDB"""
from __future__ import annotations
import json
from typing import Optional, Dict, Any, TYPE_CHECKING
import requests

from ravendb.documents.operations.definitions import MaintenanceOperation
from ravendb.http.raven_command import RavenCommand
from ravendb.http.topology import RaftCommand
from ravendb.util.util import RaftIdGenerator

from .gen_ai_configuration import GenAiConfiguration

if TYPE_CHECKING:
    from ravendb.documents.conventions import DocumentConventions
    from ravendb.http.server_node import ServerNode


class UpdateGenAiOperationResult:
    """Result of updating a GenAI operation"""
    
    def __init__(
        self,
        identifier: str = None,
        task_id: int = None,
        raft_command_index: int = None
    ):
        self.identifier = identifier
        self.task_id = task_id
        self.raft_command_index = raft_command_index
    
    @classmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> UpdateGenAiOperationResult:
        """Create from JSON representation"""
        return cls(
            identifier=json_dict.get("Identifier"),
            task_id=json_dict.get("TaskId"),
            raft_command_index=json_dict.get("RaftCommandIndex")
        )


class UpdateGenAiOperation(MaintenanceOperation[UpdateGenAiOperationResult]):
    """Operation to update an existing GenAI ETL configuration in RavenDB"""
    
    def __init__(self, task_id: int, configuration: GenAiConfiguration):
        if not configuration:
            raise ValueError("configuration cannot be None")
        if task_id is None or task_id <= 0:
            raise ValueError("task_id must be a positive integer")
        
        self._task_id = task_id
        self._configuration = configuration
    
    def get_command(self, conventions: DocumentConventions) -> RavenCommand[UpdateGenAiOperationResult]:
        """
        Get the RavenDB command for this operation
        
        Args:
            conventions: Document conventions
            
        Returns:
            Command object to execute
        """
        return self.UpdateGenAiCommand(conventions, self._task_id, self._configuration)
    
    class UpdateGenAiCommand(RavenCommand[UpdateGenAiOperationResult], RaftCommand):
        """RavenDB command to update GenAI configuration"""
        
        def __init__(
            self,
            conventions: DocumentConventions,
            task_id: int,
            configuration: GenAiConfiguration
        ):
            super().__init__(UpdateGenAiOperationResult)
            
            if not conventions:
                raise ValueError("conventions cannot be None")
            if not configuration:
                raise ValueError("configuration cannot be None")
            if task_id is None or task_id <= 0:
                raise ValueError("task_id must be a positive integer")
            
            self._conventions = conventions
            self._task_id = task_id
            self._configuration = configuration
            self._raft_unique_request_id = RaftIdGenerator.new_id()
        
        def is_read_request(self) -> bool:
            return False
        
        def create_request(self, node: ServerNode) -> requests.Request:
            """
            Create HTTP request for this command
            
            Args:
                node: Server node to send request to
                
            Returns:
                requests.Request object
            """
            url = f"{node.url}/databases/{node.database}/admin/etl?id={self._task_id}"
            
            request = requests.Request("PUT", url)
            request.data = self._configuration.to_json()
    
            return request
        
        def set_response(self, response: Optional[str], from_cache: bool) -> None:
            """
            Parse response from server
            
            Args:
                response: JSON response string from server
                from_cache: Whether response is from cache
            """
            if response is None:
                self._throw_invalid_response()
            
            self.result = UpdateGenAiOperationResult.from_json(json.loads(response))
        
        def get_raft_unique_request_id(self) -> str:
            return self._raft_unique_request_id
