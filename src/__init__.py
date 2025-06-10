"""AI Agents Framework - A clean, modular framework for building AI agents with Claude."""

from .agents.base import BaseAgent, ModelConfig
from .agents.agent import Agent
from .agents.web_search import WebSearchAgent
from .agents.deep_research import DeepResearchAgent, DeepResearchConfig
from .tools.base import Tool
from .tools.web_search import BraveSearchTool, FirecrawlContentTool
from .tools.google_drive import GoogleDriveTool, GoogleDriveContentTool
from .utils.message_history import MessageHistory, Message

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
    
    # Tools
    "BraveSearchTool", 
    "FirecrawlContentTool",
    "GoogleDriveTool",
    "GoogleDriveContentTool",
    
    # Utilities
    "MessageHistory", 
    "Message"
] 