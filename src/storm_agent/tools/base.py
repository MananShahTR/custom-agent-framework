"""Base Tool class for building agent tools."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Tool(ABC):
    """Base class for all agent tools."""
    
    name: str
    description: str
    input_schema: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to Claude API format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }
    
    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """Execute the tool with provided parameters.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            String result of the tool execution
        """
        raise NotImplementedError(
            "Tool subclasses must implement execute method"
        )
    
    def validate_input(self, **kwargs) -> None:
        """Validate input parameters against the schema.
        
        Args:
            **kwargs: Input parameters to validate
            
        Raises:
            ValueError: If required parameters are missing or invalid
        """
        # Check required parameters
        required = self.input_schema.get("required", [])
        for param in required:
            if param not in kwargs:
                raise ValueError(f"Required parameter '{param}' is missing")
        
        # Check parameter types (basic validation)
        properties = self.input_schema.get("properties", {})
        for param, value in kwargs.items():
            if param in properties:
                expected_type = properties[param].get("type")
                if expected_type:
                    # Basic type checking
                    type_map = {
                        "string": str,
                        "integer": int,
                        "number": (int, float),
                        "boolean": bool,
                        "array": list,
                        "object": dict
                    }
                    expected_python_type = type_map.get(expected_type)
                    if expected_python_type and not isinstance(value, expected_python_type):
                        raise ValueError(
                            f"Parameter '{param}' should be of type {expected_type}, "
                            f"got {type(value).__name__}"
                        ) 