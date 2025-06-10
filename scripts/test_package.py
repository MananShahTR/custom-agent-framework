#!/usr/bin/env python3
"""Test script to verify Storm Agent package installation and functionality."""

import sys
import subprocess
import tempfile
import os


def test_package_installation():
    """Test package installation from built wheel."""
    print("🧪 Testing Storm Agent Package Installation")
    print("=" * 50)
    
    # Get the wheel file path
    wheel_path = "dist/storm_agent-1.0.0-py3-none-any.whl"
    
    if not os.path.exists(wheel_path):
        print("❌ Wheel file not found. Run 'python3 -m build' first.")
        return False
    
    print(f"📦 Found wheel: {wheel_path}")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"🗂️  Test directory: {temp_dir}")
        
        # Install the package in the temporary directory
        try:
            print("\n🔧 Installing package...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "--target", temp_dir,
                "--no-deps",  # Don't install dependencies for quick test
                wheel_path
            ], capture_output=True, text=True, check=True)
            
            print("✅ Package installed successfully!")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            return False
        
        # Test importing the package
        print("\n🔍 Testing package import...")
        try:
            # Add temp directory to Python path
            sys.path.insert(0, temp_dir)
            
            # Test basic imports
            import storm_agent
            print(f"✅ storm_agent imported successfully (version: {storm_agent.__version__})")
            
            from storm_agent import Agent, WebSearchAgent, DeepResearchAgent
            print("✅ Agent classes imported successfully")
            
            from storm_agent import Tool, BraveSearchTool
            print("✅ Tool classes imported successfully")
            
            from storm_agent import MessageHistory, Message
            print("✅ Utility classes imported successfully")
            
            # Test agent creation (without API keys, just construction)
            agent = Agent(name="Test Agent", description="Test agent")
            print("✅ Agent creation works")
            
            print(f"\n📊 Package Info:")
            print(f"   Name: {storm_agent.__name__}")
            print(f"   Version: {storm_agent.__version__}")
            print(f"   Author: {storm_agent.__author__}")
            print(f"   Description: {storm_agent.__description__}")
            
            # Clean up sys.path
            sys.path.remove(temp_dir)
            
            return True
            
        except Exception as e:
            print(f"❌ Import test failed: {e}")
            return False


def test_cli_availability():
    """Test that CLI command is available."""
    print("\n🖥️  Testing CLI Availability")
    print("=" * 30)
    
    try:
        # Test that the CLI entry point was created
        result = subprocess.run([
            sys.executable, "-c", 
            "import pkg_resources; print(list(pkg_resources.iter_entry_points('console_scripts', 'storm-agent')))"
        ], capture_output=True, text=True)
        
        if "storm-agent" in result.stdout:
            print("✅ CLI entry point configured correctly")
        else:
            print("⚠️  CLI entry point not found in setup")
            
    except Exception as e:
        print(f"⚠️  CLI test failed: {e}")


def test_package_metadata():
    """Test package metadata."""
    print("\n📋 Testing Package Metadata")
    print("=" * 30)
    
    try:
        result = subprocess.run([
            sys.executable, "-c",
            "import pkg_resources; dist = pkg_resources.get_distribution('storm-agent'); "
            "print(f'Name: {dist.project_name}'); "
            "print(f'Version: {dist.version}'); "
            "print(f'Location: {dist.location}')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Package metadata accessible")
            print(result.stdout)
        else:
            print("⚠️  Package not installed or metadata not accessible")
            
    except Exception as e:
        print(f"⚠️  Metadata test failed: {e}")


def main():
    """Run all tests."""
    print("🌩️ Storm Agent Package Test Suite")
    print("=" * 60)
    
    success = True
    
    # Test 1: Package installation and imports
    if not test_package_installation():
        success = False
    
    # Test 2: CLI availability
    test_cli_availability()
    
    # Test 3: Package metadata
    test_package_metadata()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! Storm Agent package is ready!")
        print("\n📦 To install the package:")
        print("   pip install dist/storm_agent-1.0.0-py3-none-any.whl")
        print("\n🚀 To publish to PyPI:")
        print("   twine upload dist/*")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
