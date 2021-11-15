from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import csv

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly',
        'https://www.googleapis.com/auth/spreadsheets']

# Google Sheets API Reference
SAMPLE_SPREADSHEET_ID = ''
SAMPLE_RANGE_NAME = 'A1'

def main():
    """Shows basic usage of the Admin SDK Reports API.
    Prints the time, email, and name of the last 10 login events in the domain.
    """
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

    # Calling the service for Google Admin Audit Report
    service = build('admin', 'reports_v1', credentials=creds)

    # Calling the sevice for Google Sheets API
    sheets_service = build('sheets', 'v4', credentials=creds)

    # Call the Admin SDK Reports API maxResults=1
    print('Getting the last 1000 login events')
    try:
        results = service.activities().list(userKey='all', applicationName='login',eventName='login_verification',startTime='2021-08-06T05:40:54.200Z'
            ).execute()
        activities = results.get('items', [])
    except:
        return "Login Audit Failed"


    # Checking if JSON object is not empty
    if not activities:
        print('No logins found.')
    else:
        # Creating CSV file
        data_file = open('login_audit.csv','w')

        # Creating the CSV writer object 
        csv_writer = csv.writer(data_file)

        print('Login_Audit Genrating')

        # Creating countet for writing headings
        count = 0

        # Printing the login details on output/Google Sheets API
        new_values =[
            # cell values
            ['Time','User Email','2FA Method']
        ]
        body={
            'values': new_values
        }

        # Loop for appending all the respones
        for activity in activities:

            if count == 0:

                headings = ['Time','User Email','2FA Method']
                csv_writer.writerow(headings)
                count +=1

            # Only copy the users who are having Phone Number
            if activity['events'][0]['parameters'][1]['multiValue'][0] == "idv_preregistered_phone":
                values = [activity['id']['time'],activity['actor']['email'],activity['events'][0]['parameters'][1]['multiValue'][0]]
                csv_writer.writerow(values)

                # Appending values in List for Sheet API
                new_values.append([activity['id']['time'],activity['actor']['email'],activity['events'][0]['parameters'][1]['multiValue'][0]])

            
            #print(u'{0}: {1} ({2}) : 2FA method: < {3} >'.format(activity['id']['time'],
             #   activity['actor']['email'], activity['events'][0]['name'], activity['events'][0]['parameters'][1]['multiValue'][0]))
        
        # Final message
        print('Login_Audit CSV Exported\n')

        # ------- Google Sheet API ----- #
        # Calling the Sheet API 
        try:
            new_result = sheets_service.spreadsheets().values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME,valueInputOption='RAW', body=body).execute()
            print('Login_Audit Google Sheet Exported Successfully\n')
        except:
            print("Error Occured")
        #print('{0} cells updated.'.format(new_result.get('updatedCells')))

# Calling the main program
if __name__ == '__main__':
    main()
