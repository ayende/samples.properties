"""GenAI transformation configuration"""
from typing import Dict, Any


class GenAiTransformation:
    """Transformation script for GenAI processing"""
    
    def __init__(self, script: str = None):
        self.script = script
    
    def validate_script(self) -> tuple[bool, str]:
        """
        Validate that the script contains required ai.genContext call
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.script:
            return False, "Script cannot be empty"
        
        if "ai.genContext" in self.script:
            return True, ""
        
        return False, "You must call the ai.genContext(ctx) function in your script"
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON representation"""
        return {
            "Script": self.script
        }
    
    @classmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> "GenAiTransformation":
        """Create from JSON representation"""
        return cls(script=json_dict.get("Script"))
