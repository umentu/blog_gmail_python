from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://mail.google.com/']

# この日以前のメールが削除対象
# BEFORE_DATE = 'YYYY-mm-dd'
BEFORE_DATE = '2019-01-01'

def main():

    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    users = service.users()

    """
    -is:important で重要メールを外す
    -is:starred でスター付きメールを外す
    それ以外のフラグは https://support.google.com/mail/answer/7190?hl=ja を参照
    """
    meta_data = users.messages().list(userId='me', q='before:{} -is:important -is:starred'.format(BEFORE_DATE)).execute()

    while len(meta_data['messages']) > 0:
        remove_list = []
        for m in meta_data['messages']:
            print(m['id'])
            remove_list.append(m['id'])

        users.messages().batchDelete(userId='me', body={'ids': remove_list}).execute()

        meta_data = users.messages().list(userId='me', pageToken=meta_data['nextPageToken']).execute()


if __name__ == '__main__':
    main()
