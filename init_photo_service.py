import pickle
import os
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


def Create_Service(client_secret_file, api_name, api_version, discovery_url, endpoint_name, *scopes):
    print(client_secret_file, api_name, api_version, scopes, sep='-')
    CALLED_CLIENT_SECRET_FILE = client_secret_file
    CALLED_API_SERVICE_NAME = api_name
    CALLED_API_VERSION = api_version
    CALLED_SCOPES = [scope for scope in scopes[0]]
    CALLED_DISCOVERY_URL = discovery_url
    print(CALLED_SCOPES)

    cred = None

    pickle_file = f'token_{CALLED_API_SERVICE_NAME}_{CALLED_API_VERSION}_{endpoint_name}.pickle'
    # print(pickle_file)

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CALLED_CLIENT_SECRET_FILE, CALLED_SCOPES)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(CALLED_API_SERVICE_NAME, CALLED_API_VERSION, discoveryServiceUrl=CALLED_DISCOVERY_URL, credentials=cred)
        print(CALLED_API_SERVICE_NAME, 'sourceservice created successfully')
        return service
    except Exception as e:
        print('Unable to Connect.')
        print(e)
    return None

def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt