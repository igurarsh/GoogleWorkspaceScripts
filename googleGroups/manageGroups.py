from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user',
        'https://apps-apis.google.com/a/feeds/groups/']

def main():
    group_email = input("Enter the group email: ")
    user_email = input("Enter the user email: ")
    new_role = input("Enter the new role(e.g. MEMBER, OWNER, MANAGER): ")

    # Calling the Google API function
    userRoleChange(group_email,user_email,new_role)

def userRoleChange(grpEmail,usrEmail,role):
    """Shows basic usage of the Admin SDK Directory API.
    Prints the emails and names of the first 10 users in the domain.
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

    service = build('admin', 'directory_v1', credentials=creds)

    # Rsources body 
    roles = {
        'role':role
    }

    # Call the Admin SDK Directory API
    try:
        results = service.members().update(groupKey=grpEmail, memberKey=usrEmail,body=roles).execute()
        print("User Successfully updated")
    except:
        print("Error Occurred")

# Calling the main function
if __name__ == '__main__':
    main()
