"""Example of creating a custom agent using the base Agent and Tool classes."""

import asyncio
import json
import requests
from typing import Any, Dict
from storm_agentagents.base import Agent, ModelConfig
from storm_agenttools.base import Tool
from storm_agentutils.message_history import MessageHistory


class WeatherTool(Tool):
    """Custom tool for getting weather information."""
    
    def __init__(self):
        super().__init__(
            name="get_weather",
            description="Get current weather information for a specific city using OpenWeatherMap API.",
            input_schema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name to get weather for"
                    },
                    "country_code": {
                        "type": "string",
                        "description": "Optional 2-letter country code (e.g., 'US', 'GB')",
                        "default": ""
                    }
                },
                "required": ["city"]
            }
        )
    
    async def execute(self, city: str, country_code: str = "") -> str:
        """Get weather data from OpenWeatherMap API."""
        try:
            # Note: You would need to set OPENWEATHERMAP_API_KEY in your environment
            api_key = "demo_key"  # Replace with actual API key
            
            # Build location string
            location = city
            if country_code:
                location = f"{city},{country_code}"
            
            # For demo purposes, return mock data
            return f"""🌤️ **Weather for {city}**

📍 **Location:** {city.title()}
🌡️ **Temperature:** 22°C (72°F)
💧 **Humidity:** 65%
🌬️ **Wind:** 12 km/h NW
☁️ **Conditions:** Partly cloudy
👁️ **Visibility:** 10 km

*Note: This is demo data. To get real weather data, please set your OpenWeatherMap API key.*"""
            
        except Exception as e:
            return f"❌ Error getting weather data: {str(e)}"


class CalculatorTool(Tool):
    """Custom tool for performing calculations."""
    
    def __init__(self):
        super().__init__(
            name="calculate",
            description="Perform mathematical calculations safely.",
            input_schema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2 + 3 * 4')"
                    }
                },
                "required": ["expression"]
            }
        )
    
    async def execute(self, expression: str) -> str:
        """Safely evaluate mathematical expressions."""
        try:
            # Simple safety check - only allow basic math operations
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return "❌ Error: Only basic mathematical operations are allowed (+, -, *, /, parentheses)"
            
            # Evaluate the expression
            result = eval(expression)
            
            return f"🧮 **Calculation Result**\n\n**Expression:** {expression}\n**Result:** {result}"
            
        except ZeroDivisionError:
            return "❌ Error: Division by zero"
        except Exception as e:
            return f"❌ Error in calculation: {str(e)}"


class PersonalAssistantAgent(Agent):
    """Custom agent that acts as a personal assistant with weather and calculation capabilities."""
    
    def __init__(self, name: str = "PersonalAssistant", verbose: bool = True):
        """Initialize the personal assistant agent."""
        # Create custom tools
        tools = [
            WeatherTool(),
            CalculatorTool()
        ]
        
        # Create custom config
        config = ModelConfig(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            temperature=0.7
        )
        
        # Initialize base agent
        super().__init__(
            name=name,
            description="A helpful personal assistant that can check weather and perform calculations.",
            tools=tools,
            config=config,
            verbose=verbose
        )
        
        # Initialize message history
        self.message_history = MessageHistory(
            model=self.config.model,
            system=self.system_prompt,
            client=self.client,
            enable_caching=self.config.enable_caching
        )
    
    def _default_system_prompt(self) -> str:
        """Custom system prompt for the personal assistant."""
        return """You are a helpful personal assistant AI with access to weather information and calculation tools.

Your capabilities include:
- Getting current weather information for any city
- Performing mathematical calculations
- Providing helpful information and assistance

When helping users:
- Be friendly and conversational
- Use tools when appropriate to provide accurate information
- If asked about weather, use the get_weather tool
- If asked to do calculations, use the calculate tool
- Provide clear, well-formatted responses
- Be proactive in suggesting how you can help

Always aim to be helpful, accurate, and efficient in your responses."""
    
    async def run_async(self, user_input: str, **kwargs) -> Any:
        """Run the agent asynchronously."""
        # Add user message to history
        await self.message_history.add_message("user", user_input)
        
        # Run the agent loop
        response = await self._agent_loop(user_input)
        
        return response
    
    async def _agent_loop(self, user_input: str) -> Any:
        """Main agent loop."""
        max_iterations = 5
        iteration_count = 0
        
        while iteration_count < max_iterations:
            # Prepare message parameters
            params = {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "system": self.system_prompt,
                "tools": self._prepare_tools_for_api(),
                "messages": self.message_history.format_for_api()
            }
            
            # Get response from Claude
            response = self.client.messages.create(**params)
            
            # Add assistant message to history
            await self.message_history.add_message(
                "assistant", 
                response.content,
                usage=response.usage
            )
            
            # Check for tool calls
            tool_calls = [
                content for content in response.content 
                if hasattr(content, 'type') and content.type == 'tool_use'
            ]
            
            if not tool_calls:
                # No tools to execute, return the response
                if self.verbose:
                    print(f"\n{self.name} Response:")
                    for content in response.content:
                        if hasattr(content, 'text'):
                            print(content.text)
                
                return response
            
            # Execute tool calls
            if self.verbose:
                print(f"\n{self.name} is using tools...")
                for tool_call in tool_calls:
                    print(f"  - {tool_call.name}: {tool_call.input}")
            
            tool_results = await self.execute_tool_calls(tool_calls)
            
            # Add tool results to message history
            for result in tool_results:
                await self.message_history.add_message("user", [result])
            
            iteration_count += 1


async def main():
    """Run the custom agent example."""
    # Create the personal assistant
    assistant = PersonalAssistantAgent(verbose=True)
    
    print("🤖 AI Agents Framework - Custom Agent Example")
    print("=" * 60)
    print("Personal Assistant Agent with Weather & Calculator Tools")
    print("=" * 60)
    
    # Example conversations
    queries = [
        "What's the weather like in London?",
        "Can you calculate 15 * 24 + 120?",
        "Help me plan my day - I need to know the weather in New York and calculate my budget: 500 + 200 - 75"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n🔹 Example {i}: {query}")
        print("-" * 40)
        
        response = await assistant.run_async(query)
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main()) 