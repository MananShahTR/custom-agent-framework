"""Setup script for Google Drive authentication."""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def setup_oauth2_authentication():
    """Set up OAuth2 authentication for Google Drive."""
    print("🔐 Setting up Google Drive OAuth2 Authentication")
    print("=" * 60)
    
    creds = None
    
    # Check if token already exists
    if os.path.exists('token.pickle'):
        print("✅ Found existing token.pickle file")
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("\n📋 To set up Google Drive access, you need to:")
            print("1. Go to https://console.cloud.google.com/")
            print("2. Create a new project or select existing one")
            print("3. Enable the Google Drive API")
            print("4. Create OAuth2 credentials (Desktop application)")
            print("5. Download the credentials as 'credentials.json'")
            print("6. Place 'credentials.json' in this directory")
            print("\n")
            
            if not os.path.exists('../credentials.json'):
                print("❌ 'credentials.json' not found!")
                print("   Please follow the steps above and run this script again.")
                return False
            
            print("✅ Found credentials.json")
            print("🌐 Opening browser for authentication...")
            print("   Please authorize access in your browser.")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                '../credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        print("✅ Authentication successful! Token saved to token.pickle")
    
    # Test the authentication
    try:
        from googleapiclient.discovery import build
        service = build('drive', 'v3', credentials=creds)
        
        # Try to list files
        results = service.files().list(
            pageSize=1,
            fields="files(id, name)"
        ).execute()
        
        print("\n✅ Google Drive API connection successful!")
        print("   You can now use Google Drive search in DeepResearchAgent")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing Google Drive API: {str(e)}")
        return False


def setup_service_account():
    """Guide for setting up service account authentication."""
    print("\n🔐 Service Account Setup Guide")
    print("=" * 60)
    print("\nService accounts are best for server applications.")
    print("\nTo set up a service account:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Select your project")
    print("3. Go to 'IAM & Admin' > 'Service Accounts'")
    print("4. Create a new service account")
    print("5. Create and download a JSON key")
    print("6. Set the path in your .env file:")
    print("   GOOGLE_SERVICE_ACCOUNT_FILE=path/to/your-service-account-key.json")
    print("\n7. Share your Google Drive files/folders with the service account email")
    print("   (found in the JSON file as 'client_email')")


def main():
    """Main setup function."""
    print("🚀 Google Drive Authentication Setup")
    print("=" * 80)
    print("\nChoose authentication method:")
    print("1. OAuth2 (Interactive - Best for personal use)")
    print("2. Service Account (Best for servers)")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        setup_oauth2_authentication()
    elif choice == "2":
        setup_service_account()
    elif choice == "3":
        print("Exiting...")
    else:
        print("Invalid choice. Please run the script again.")


if __name__ == "__main__":
    main() 