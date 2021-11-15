from __future__ import print_function
import os.path
from typing import ValuesView
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user',
        'https://www.googleapis.com/auth/spreadsheets']

# Google Sheets API Reference
SAMPLE_SPREADSHEET_ID = ''
SAMPLE_RANGE_NAME = ''

# Data to be enetered in Sheets 
new_values =[
    # cell values
    []
]

# Getting the required credentials for the API
creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())


def main():
    getuserList()

# Getting user required data
def getuserList():
    # Call the Admin SDK Directory API
    service = build('admin', 'directory_v1', credentials=creds)

    # Getting the results
    results = service.users().list(domain='wonolo.com', maxResults=500,
                                orderBy='email',projection="basic",query="").execute()
    users = results.get('users', [])

    if not users:
        print('No users in the domain.')
    else:
        for user in users:
            print(user['id']+'  '+user['primaryEmail'])
            new_values.append([user['primaryEmail']])
        try:    
            print(results['nextPageToken'])
        except:
            print("The whole data is exported")
        updateSheet(new_values)
    return 0

# Sending data to Google Sheet
def updateSheet(data):
    # Calling the sevice for Google Sheets API
    sheets_service = build('sheets', 'v4', credentials=creds)

    # Sending the data to selected sheet
    body={
        'values': data
    }

    try:
        new_result = sheets_service.spreadsheets().values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME,valueInputOption='RAW', body=body).execute()
        print('Google Sheet Exported Successfully\n')
    except:
            print("Error Occured")

# Calling the main function
if __name__ == '__main__':
    main()
