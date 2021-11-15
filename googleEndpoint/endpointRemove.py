from __future__ import print_function
import os.path
from typing import ValuesView
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.device.mobile',
        'https://www.googleapis.com/auth/spreadsheets']

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
    getDeviceId()
    logError()

# API to Retrieve Device IDs from Google Sheet
# The ID and range of a sample spreadsheet.
Device_SPREADSHEET_ID = ''
deviceId_RANGE_NAME = ''

# Logging Failures to Sheet
Error_SPREADSHEET_ID = ""
Error_RANGE_NAME = ""

errorsValues=[
    ["DeviceId","Status"]
]

def logError():
    
    # Response body
    body = {
        'values':errorsValues
    }
    
    # Calling the sevice for Google Sheets API
    sheets_service = build('sheets', 'v4', credentials=creds)
    try:
        new_result = sheets_service.spreadsheets().values().append(spreadsheetId=Error_SPREADSHEET_ID,
                                    range=Error_RANGE_NAME,valueInputOption='RAW', body=body).execute()
        print('Logs Exported Successfully\n')
    except:
        print("Error Occured")



def getDeviceId():
    # Building Required API Service
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=Device_SPREADSHEET_ID,
                                range=deviceId_RANGE_NAME).execute()
    values = result.get('values', [])

    # Printing the values recieved
    if not values:
        print('No data found.')
    else:
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            getResourceID(row[0])

# API to get Resource ID
def getResourceID(deviceID):
    # Building Required API Service
    service = build('admin', 'directory_v1', credentials=creds)

    # Call the Admin SDK Directory API
    
    results = service.mobiledevices().list(customerId='my_customer',query=deviceID).execute()

    #print(results['mobiledevices'][0]['resourceId'])
    try:
        adminAccountWipe(results['mobiledevices'][0]['resourceId'])
    except:
        errorsValues.append([deviceID,"Fail"])
        

# API to account wipe
def adminAccountWipe(rsrcID):
    #Building Required API Service
    service = build('admin', 'directory_v1', credentials=creds)

    # Rsources body 
    actions = {
        'action':'admin_account_wipe'
    }

    # Call the Admin SDK Directory API
    try:
        results = service.mobiledevices().action(customerId='my_customer',resourceId=rsrcID,body=actions).execute()
        print("Account Wiped Successfully")
    except:
        print("Error Occured")

# Calling the main function
if __name__ == '__main__':
    main()
