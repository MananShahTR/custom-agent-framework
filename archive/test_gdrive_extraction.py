#!/usr/bin/env python3
"""Test script for Google Drive content extraction with Anthropic."""

import asyncio
from deep_research_agent import GoogleDriveContentTool
from anthropic import Anthropic
import os

async def test_extraction():
    """Test the Google Drive content extraction."""
    
    # Initialize the tool with Anthropic client
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    tool = GoogleDriveContentTool(client=client)
    
    # Test cases - replace with actual file IDs from your Google Drive
    test_files = [
        # ("YOUR_PDF_FILE_ID", "PDF file"),
        # ("YOUR_IMAGE_FILE_ID", "Image file"),
        # ("YOUR_DOC_FILE_ID", "Google Doc"),
        # ("YOUR_TEXT_FILE_ID", "Text file"),
    ]
    
    print("🧪 Google Drive Content Extraction Test")
    print("=" * 50)
    
    if not test_files:
        print("\n⚠️  Please add some file IDs to test!")
        print("1. Go to Google Drive")
        print("2. Right-click a file and select 'Get link'")
        print("3. Extract the file ID from the URL")
        print("   Example: https://drive.google.com/file/d/FILE_ID_HERE/view")
        print("4. Add the file ID to the test_files list above")
        return
    
    for file_id, description in test_files:
        print(f"\n📁 Testing: {description}")
        print("-" * 40)
        
        try:
            result = await tool.execute(file_id=file_id)
            print(result[:500] + "..." if len(result) > 500 else result)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_extraction()) 