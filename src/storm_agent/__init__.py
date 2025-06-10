"""Storm Agent - A powerful framework for building AI agents with Claude.

Storm Agent provides a clean, modular framework for creating intelligent AI agents
powered by Claude, featuring web search, document processing, MCP integration,
and advanced research capabilities.
"""

from .agents.base import BaseAgent, ModelConfig
from .agents.agent import Agent
from .agents.web_search import WebSearchAgent
from .agents.deep_research import DeepResearchAgent, DeepResearchConfig
from .agents.multi_agent_system import MultiAgentSystem
from .tools.base import Tool
from .tools.web_search import BraveSearchTool, FirecrawlContentTool
from .tools.google_drive import GoogleDriveTool, GoogleDriveContentTool
from .tools.approval import RequestApprovalTool
from .tools.handoff import HandoffTool
from .utils.message_history import MessageHistory, Message

__version__ = "1.1.0"
__author__ = "Storm Agent Team"
__email__ = "contact@storm-agent.dev"
__description__ = "A powerful framework for building AI agents with Claude"

__all__ = [
    # Base classes
    "BaseAgent",
    "Agent", 
    "Tool", 
    "ModelConfig",
    
    # Agents
    "WebSearchAgent", 
    "DeepResearchAgent", 
    "DeepResearchConfig",
    "MultiAgentSystem",
    
    # Tools
    "BraveSearchTool", 
    "FirecrawlContentTool",
    "GoogleDriveTool",
    "GoogleDriveContentTool",
    "RequestApprovalTool",
    "HandoffTool",
    
    # Utilities
    "MessageHistory", 
    "Message"
]
