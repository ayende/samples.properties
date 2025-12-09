"""Add GenAI operation for RavenDB"""
from __future__ import annotations
import json
from typing import Optional, Dict, Any, TYPE_CHECKING
import requests
from urllib.parse import quote

from ravendb.documents.operations.definitions import MaintenanceOperation
from ravendb.http.raven_command import RavenCommand
from ravendb.http.topology import RaftCommand
from ravendb.util.util import RaftIdGenerator

from .gen_ai_configuration import GenAiConfiguration

if TYPE_CHECKING:
    from ravendb.documents.conventions import DocumentConventions
    from ravendb.http.server_node import ServerNode


class StartingPointChangeVector:
    """Represents a change vector starting point for ETL operations"""
    
    LAST_DOCUMENT = "LastDocument"
    BEGINNING = "Beginning"
    
    def __init__(self, value: str):
        self.value = value
    
    @classmethod
    def last_document(cls) -> StartingPointChangeVector:
        """Start from last document"""
        return cls(cls.LAST_DOCUMENT)
    
    @classmethod
    def beginning(cls) -> StartingPointChangeVector:
        """Start from beginning"""
        return cls(cls.BEGINNING)


class AddGenAiOperationResult:
    """Result of adding a GenAI operation"""
    
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
    def from_json(cls, json_dict: Dict[str, Any]) -> AddGenAiOperationResult:
        """Create from JSON representation"""
        return cls(
            identifier=json_dict.get("Identifier"),
            task_id=json_dict.get("TaskId"),
            raft_command_index=json_dict.get("RaftCommandIndex")
        )


class AddGenAiOperation(MaintenanceOperation[AddGenAiOperationResult]):
    """Operation to add a GenAI ETL configuration to RavenDB"""
    
    def __init__(
        self,
        configuration: GenAiConfiguration,
        starting_point: Optional[StartingPointChangeVector] = None
    ):
        if not configuration:
            raise ValueError("configuration cannot be None")
        
        self._configuration = configuration
        self._starting_point = starting_point or StartingPointChangeVector.last_document()
    
    def get_command(self, conventions: DocumentConventions) -> RavenCommand[AddGenAiOperationResult]:
        """
        Get the RavenDB command for this operation
        
        Args:
            conventions: Document conventions
            
        Returns:
            Command object to execute
        """
        return self.AddGenAiCommand(conventions, self._configuration, self._starting_point)
    
    class AddGenAiCommand(RavenCommand[AddGenAiOperationResult], RaftCommand):
        """RavenDB command to add GenAI configuration"""
        
        def __init__(
            self,
            conventions: DocumentConventions,
            configuration: GenAiConfiguration,
            starting_point: StartingPointChangeVector
        ):
            super().__init__(AddGenAiOperationResult)
            
            if not conventions:
                raise ValueError("conventions cannot be None")
            if not configuration:
                raise ValueError("configuration cannot be None")
            
            self._conventions = conventions
            self._configuration = configuration
            self._starting_point = starting_point
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
            url = f"{node.url}/databases/{node.database}/admin/etl?changeVector={quote(self._starting_point.value)}"
            
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
            
            self.result = AddGenAiOperationResult.from_json(json.loads(response))
        
        def get_raft_unique_request_id(self) -> str:
            return self._raft_unique_request_id
