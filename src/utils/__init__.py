"""Utility modules for the AI agents framework."""

from .message_history import MessageHistory, Message

try:
    from .connections import setup_mcp_connections, create_mcp_connection, MCPConnection
    __all__ = ["MessageHistory", "Message", "setup_mcp_connections", "create_mcp_connection", "MCPConnection"]
except ImportError:
    # MCP dependencies not available
    __all__ = ["MessageHistory", "Message"] 