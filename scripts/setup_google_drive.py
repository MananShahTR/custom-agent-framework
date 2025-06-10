#!/usr/bin/env python3
"""
Google Drive Authentication Setup Helper

This script helps you set up OAuth2 authentication for Google Drive access.
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes for Google Drive read-only access
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def setup_google_drive_auth():
    """Set up Google Drive OAuth2 authentication."""
    print("🔐 Google Drive Authentication Setup")
    print("=" * 50)
    
    # Check if we already have valid credentials
    creds = None
    if os.path.exists('token.pickle'):
        print("📁 Found existing token.pickle file")
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("🌐 Starting OAuth2 flow...")
            print("\nYou need a credentials.json file from Google Cloud Console:")
            print("1. Go to: https://console.cloud.google.com/")
            print("2. Create a project or select existing one")
            print("3. Enable Google Drive API")
            print("4. Go to 'Credentials' → 'Create Credentials' → 'OAuth 2.0 Client IDs'")
            print("5. Choose 'Desktop application'")
            print("6. Download the JSON file and save it as 'credentials.json' in this directory")
            print("")
            
            if not os.path.exists('credentials.json'):
                print("❌ credentials.json not found!")
                print("Please create credentials.json as described above, then run this script again.")
                return False
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        print("✅ Credentials saved to token.pickle")
    
    else:
        print("✅ Valid credentials already exist")
    
    # Test the credentials
    try:
        from googleapiclient.discovery import build
        service = build('drive', 'v3', credentials=creds)
        
        # Test by listing a few files
        results = service.files().list(pageSize=3).execute()
        files = results.get('files', [])
        
        print(f"\n🎉 Google Drive authentication successful!")
        print(f"Found {len(files)} files (showing first 3):")
        for file in files:
            print(f"  - {file['name']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing Google Drive access: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Google Drive Setup for AI Agents")
    print("This will help you set up Google Drive authentication for the research agents.")
    print("")
    
    success = setup_google_drive_auth()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ Setup complete! You can now use Google Drive tools in your agents.")
        print("\nNext steps:")
        print("1. Run: python examples/deep_research.py")
        print("2. Or run: python examples/deep_research_web_only.py (if you prefer web-only)")
    else:
        print("\n" + "=" * 50)
        print("❌ Setup failed. Please check the instructions above and try again.")
        print("\nFallback option:")
        print("- Run: python examples/deep_research_web_only.py (works without Google Drive)")

if __name__ == "__main__":
    main() 