# Fix Google OAuth 403 Access Denied Error

## The Error
```
Error 403: access_denied
Request details: access_type=offline response_type=code
redirect_uri=http://localhost:61668/ state=9AkU9e7PQOSMih4qnNbXwWoxrf8qRv
client_id=1573000060379-db3oco3qgrgg1820vcp3smnbg8rklcb9.apps.googleusercontent.com
scope=https://www.googleapis.com/auth/drive.readonly
flowName=GeneralOAuthFlow
```

## Solution Steps

### 1. Configure OAuth Consent Screen

Go to [Google Cloud Console](https://console.cloud.google.com/) and:

1. Select your project
2. Navigate to **APIs & Services** → **OAuth consent screen**
3. Configure the consent screen:
   - **User Type**: Choose "External" if you want anyone with a Google account to use it
   - **App name**: Give your app a name (e.g., "DeepResearchAgent")
   - **User support email**: Add your email
   - **Developer contact information**: Add your email

### 2. Add Test Users (if in Testing mode)

If your app is in "Testing" mode:
1. In OAuth consent screen, go to **Test users**
2. Click **+ ADD USERS**
3. Add your Google account email (the one you're trying to authenticate with)
4. Save

### 3. Enable Google Drive API

1. Go to **APIs & Services** → **Enabled APIs**
2. Click **+ ENABLE APIS AND SERVICES**
3. Search for "Google Drive API"
4. Click on it and press **ENABLE**

### 4. Verify OAuth Client Configuration

1. Go to **APIs & Services** → **Credentials**
2. Find your OAuth 2.0 Client ID
3. Click on it to edit
4. Verify:
   - **Application type**: Desktop app
   - **Name**: Your app name
   - Download the JSON again if needed

### 5. Common Issues and Fixes

#### Issue: App in Testing Mode
- **Solution**: Either add test users OR publish the app
- To publish: OAuth consent screen → Publishing status → **PUBLISH APP**

#### Issue: Scope Not Authorized
- **Solution**: In OAuth consent screen → Scopes → Add the drive.readonly scope

#### Issue: Wrong Google Account
- **Solution**: Make sure you're logging in with the correct Google account (the one added as test user if in testing mode)

### 6. Quick Checklist

Before running the auth script again, verify:
- [ ] OAuth consent screen is configured
- [ ] Your email is added as a test user (if app is in testing)
- [ ] Google Drive API is enabled
- [ ] You have the correct credentials.json file
- [ ] You're signing in with the right Google account

### 7. Alternative: Use Service Account

If OAuth continues to fail, consider using a service account instead:
1. Create a service account in Google Cloud Console
2. Download the JSON key
3. Share your Google Drive files with the service account email
4. Use service account authentication (no browser needed)

## Re-run Authentication

After fixing the above issues:
```bash
# Delete old token if exists
rm token.pickle

# Run the setup script again
python setup_google_drive_auth.py
```

Choose option 1 for OAuth2 and follow the prompts. 