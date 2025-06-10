"""Command-line interface for Storm Agent."""

import argparse
import asyncio
import sys
from typing import Optional

from . import Agent, WebSearchAgent, DeepResearchAgent, __version__


def create_agent_command(args):
    """Create and run a basic agent."""
    agent_kwargs = {
        "name": args.name,
        "description": args.description or f"Storm Agent: {args.name}",
        "verbose": args.verbose,
    }
    
    if args.web_search:
        agent_kwargs["enable_web_search"] = True
    
    if args.google_drive:
        agent_kwargs["enable_google_drive"] = True
    
    if args.type == "web":
        agent = WebSearchAgent(**agent_kwargs)
    elif args.type == "research":
        agent = DeepResearchAgent(**agent_kwargs)
    else:
        agent = Agent(**agent_kwargs)
    
    print(f"Created {args.type} agent: {args.name}")
    
    if args.query:
        print(f"Running query: {args.query}")
        try:
            response = agent.run(args.query)
            print("\nResponse:")
            print(response)
        except Exception as e:
            print(f"Error running query: {e}", file=sys.stderr)
            return 1
    
    return 0


def run_example_command(args):
    """Run an example from the examples directory."""
    example_map = {
        "basic": "examples/basic_web_search.py",
        "research": "examples/deep_research.py",
        "mcp": "examples/mcp_example.py",
        "multi-agent": "examples/simple_multi_agent.py",
    }
    
    if args.example not in example_map:
        print(f"Unknown example: {args.example}")
        print(f"Available examples: {', '.join(example_map.keys())}")
        return 1
    
    example_file = example_map[args.example]
    print(f"Running example: {example_file}")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, example_file], check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running example: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"Example file not found: {example_file}", file=sys.stderr)
        return 1


def version_command(args):
    """Print version information."""
    print(f"Storm Agent {__version__}")
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="storm-agent",
        description="Storm Agent - A powerful framework for building AI agents with Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  storm-agent version
  storm-agent create --name "Research Assistant" --type research --web-search
  storm-agent create --name "Helper" --query "What is the weather like?"
  storm-agent run-example basic
  storm-agent run-example research
        """,
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"Storm Agent {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    version_parser.set_defaults(func=version_command)
    
    # Create agent command
    create_parser = subparsers.add_parser("create", help="Create and optionally run an agent")
    create_parser.add_argument("--name", required=True, help="Agent name")
    create_parser.add_argument("--description", help="Agent description")
    create_parser.add_argument(
        "--type", 
        choices=["basic", "web", "research"], 
        default="basic",
        help="Agent type (default: basic)"
    )
    create_parser.add_argument("--web-search", action="store_true", help="Enable web search")
    create_parser.add_argument("--google-drive", action="store_true", help="Enable Google Drive")
    create_parser.add_argument("--query", help="Query to run with the agent")
    create_parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    create_parser.set_defaults(func=create_agent_command)
    
    # Run example command
    example_parser = subparsers.add_parser("run-example", help="Run a built-in example")
    example_parser.add_argument(
        "example",
        choices=["basic", "research", "mcp", "multi-agent"],
        help="Example to run"
    )
    example_parser.set_defaults(func=run_example_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
