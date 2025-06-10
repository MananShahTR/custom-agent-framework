"""Message history management for agents."""

from typing import Any, List, Dict, Optional, Union
from dataclasses import dataclass, field
import tiktoken
import json


@dataclass
class Message:
    """Represents a single message in the conversation."""
    role: str
    content: Union[str, List[Dict[str, Any]]]
    usage: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to API format."""
        return {
            "role": self.role,
            "content": self.content
        }


class MessageHistory:
    """Manages chat history with token tracking and context management."""
    
    def __init__(
        self,
        model: str,
        system: str,
        client: Any,
        enable_caching: bool = True,
        max_context_tokens: int = 180000
    ):
        """Initialize message history.
        
        Args:
            model: Model name for token counting
            system: System prompt
            client: Anthropic client instance
            enable_caching: Whether to enable caching
            max_context_tokens: Maximum context window size
        """
        self.model = model
        self.system = system
        self.client = client
        self.enable_caching = enable_caching
        self.max_context_tokens = max_context_tokens
        
        self.messages: List[Message] = []
        self.total_tokens = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        
        # Initialize tokenizer for token counting
        try:
            self.encoding = tiktoken.encoding_for_model("gpt-4")
        except:
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    async def add_message(
        self,
        role: str,
        content: Union[str, List[Dict[str, Any]]],
        usage: Optional[Any] = None,
    ):
        """Add a message to the history.
        
        Args:
            role: Message role (user/assistant)
            content: Message content
            usage: Token usage information
        """
        message = Message(role=role, content=content, usage=usage)
        self.messages.append(message)
        
        # Update token counts if usage provided
        if usage:
            if hasattr(usage, 'input_tokens'):
                self.total_input_tokens += usage.input_tokens
            if hasattr(usage, 'output_tokens'):
                self.total_output_tokens += usage.output_tokens
            self.total_tokens = self.total_input_tokens + self.total_output_tokens
        
        # Check if we need to truncate
        if self._estimate_tokens() > self.max_context_tokens * 0.9:
            self.truncate()
    
    def _estimate_tokens(self) -> int:
        """Estimate total tokens in the conversation."""
        total = 0
        
        # Count system prompt tokens
        if isinstance(self.system, str):
            total += len(self.encoding.encode(self.system))
        
        # Count message tokens
        for message in self.messages:
            if isinstance(message.content, str):
                total += len(self.encoding.encode(message.content))
            elif isinstance(message.content, list):
                # For structured content, estimate tokens
                total += len(str(message.content)) // 4  # Rough estimate
        
        return total
    
    def truncate(self) -> None:
        """Truncate message history to fit within context window."""
        if len(self.messages) <= 2:
            return
        
        # Keep removing oldest message pairs until we're under limit
        while self._estimate_tokens() > self.max_context_tokens * 0.8 and len(self.messages) > 2:
            # Remove the oldest user-assistant pair
            if self.messages[0].role == "user" and len(self.messages) > 1:
                self.messages.pop(0)  # Remove user message
                if self.messages and self.messages[0].role == "assistant":
                    self.messages.pop(0)  # Remove corresponding assistant message
            else:
                self.messages.pop(0)
    
    def format_for_api(self) -> List[Dict[str, Any]]:
        """Format messages for Claude API."""
        formatted = []
        
        for message in self.messages:
            formatted.append(message.to_dict())
        
        return formatted
    
    def clear(self) -> None:
        """Clear message history."""
        self.messages = []
        self.total_tokens = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of message history."""
        return {
            "message_count": len(self.messages),
            "total_tokens": self.total_tokens,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "estimated_tokens": self._estimate_tokens()
        } 
    
    def __str__(self) -> str:
        """Return a nice string representation of the message history with full JSON."""
        if not self.messages:
            return "MessageHistory: Empty conversation"
        
        # Get summary info
        summary = self.get_summary()
        
        # Build the header
        header = f"MessageHistory: {summary['message_count']} messages, {summary['estimated_tokens']} tokens"
        if self.total_tokens > 0:
            header += f" (actual: {self.total_tokens})"
        
        # Convert all messages to JSON format
        messages_json = []
        for message in self.messages:
            message_dict = {
                "role": message.role,
                "content": self._serialize_content(message.content)
            }
            if message.usage:
                message_dict["usage"] = {
                    "input_tokens": getattr(message.usage, 'input_tokens', None),
                    "output_tokens": getattr(message.usage, 'output_tokens', None)
                }
            messages_json.append(message_dict)
        
        # Pretty print the JSON
        json_str = json.dumps(messages_json, indent=2, ensure_ascii=False)
        
        result = [
            header,
            "",
            "Messages JSON:",
            json_str
        ]
        
        return "\n".join(result)
    
    def _serialize_content(self, content: Union[str, List[Any]]) -> Union[str, List[Dict[str, Any]]]:
        """Convert content to JSON-serializable format."""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            serialized_list = []
            for item in content:
                if hasattr(item, 'type') and hasattr(item, 'text'):
                    # Handle TextBlock objects
                    serialized_list.append({
                        "type": item.type,
                        "text": item.text
                    })
                elif hasattr(item, 'type') and item.type == 'tool_use':
                    # Handle tool use objects
                    serialized_list.append({
                        "type": item.type,
                        "id": getattr(item, 'id', None),
                        "name": getattr(item, 'name', None),
                        "input": getattr(item, 'input', None)
                    })
                elif hasattr(item, 'type') and item.type == 'tool_result':
                    # Handle tool result objects
                    serialized_list.append({
                        "type": item.type,
                        "tool_use_id": getattr(item, 'tool_use_id', None),
                        "content": getattr(item, 'content', None),
                        "is_error": getattr(item, 'is_error', None)
                    })
                elif isinstance(item, dict):
                    # Already a dict, keep as is
                    serialized_list.append(item)
                else:
                    # Fallback: convert to string representation
                    serialized_list.append(str(item))
            return serialized_list
        else:
            # Fallback for any other type
            return str(content)
    
    def __repr__(self) -> str:
        """Return a detailed representation of the message history."""
        return f"MessageHistory(messages={len(self.messages)}, tokens={self.total_tokens}, model='{self.model}')" 