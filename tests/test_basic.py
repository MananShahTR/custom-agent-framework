"""Basic tests for the AI agents framework."""

import pytest
from unittest.mock import Mock, patch
from src.agents.base import Agent, ModelConfig
from src.tools.base import Tool


class MockTool(Tool):
    """Mock tool for testing."""
    
    def __init__(self):
        super().__init__(
            name="mock_tool",
            description="A mock tool for testing",
            input_schema={
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "Test input"}
                },
                "required": ["input"]
            }
        )
    
    async def execute(self, input: str) -> str:
        return f"Mock response for: {input}"


class MockAgent(Agent):
    """Mock agent for testing."""
    
    def __init__(self):
        super().__init__(
            name="MockAgent",
            description="A mock agent for testing",
            tools=[MockTool()],
            config=ModelConfig()
        )
    
    async def run_async(self, user_input: str, **kwargs):
        return f"Mock agent response for: {user_input}"


def test_model_config():
    """Test ModelConfig initialization."""
    config = ModelConfig()
    assert config.model == "claude-3-5-sonnet-20241022"
    assert config.max_tokens == 4096
    assert config.temperature == 1.0
    assert config.context_window_tokens == 180000
    assert config.enable_caching is True


def test_tool_to_dict():
    """Test Tool.to_dict() method."""
    tool = MockTool()
    tool_dict = tool.to_dict()
    
    assert tool_dict["name"] == "mock_tool"
    assert tool_dict["description"] == "A mock tool for testing"
    assert "input_schema" in tool_dict


@pytest.mark.asyncio
async def test_tool_execute():
    """Test tool execution."""
    tool = MockTool()
    result = await tool.execute(input="test")
    assert result == "Mock response for: test"


def test_tool_validate_input():
    """Test tool input validation."""
    tool = MockTool()
    
    # Valid input should not raise
    tool.validate_input(input="test")
    
    # Missing required parameter should raise
    with pytest.raises(ValueError, match="Required parameter 'input' is missing"):
        tool.validate_input()


@patch('src.agents.base.Anthropic')
def test_agent_initialization(mock_anthropic):
    """Test agent initialization."""
    # Mock the Anthropic client
    mock_client = Mock()
    mock_client.api_key = "test_key"
    mock_anthropic.return_value = mock_client
    
    # Mock environment variable
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
        agent = MockAgent()
    
    assert agent.name == "MockAgent"
    assert agent.description == "A mock agent for testing"
    assert len(agent.tools) == 1
    assert "mock_tool" in agent.tool_dict


@patch('src.agents.base.Anthropic')
def test_agent_missing_api_key(mock_anthropic):
    """Test agent initialization with missing API key."""
    # Mock the Anthropic client with no API key
    mock_client = Mock()
    mock_client.api_key = ""
    mock_anthropic.return_value = mock_client
    
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY not found"):
            MockAgent()


def test_agent_tools_formatting():
    """Test agent tools description formatting."""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
        with patch('src.agents.base.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_client.api_key = "test_key"
            mock_anthropic.return_value = mock_client
            
            agent = MockAgent()
            description = agent._format_tools_description()
            
            assert "mock_tool" in description
            assert "A mock tool for testing" in description


if __name__ == "__main__":
    pytest.main([__file__]) 