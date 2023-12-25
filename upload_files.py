import os
from utils.backup_mais_recente import last_backup_folder

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


SCOPES = ["https://www.googleapis.com/auth/drive"]
PROJECT_NAME = "project_name"
PATH_TO_BACKUP_FOLDER = "path_to_backup_folder"
BACKUP_FOLDER = last_backup_folder(PATH_TO_BACKUP_FOLDER)


def upload_with_conversion():
    """Upload file with conversion
    Returns: ID of the file uploaded

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    # creds, _ = google.auth.default()

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)

        response = service.files().list(
            q=f"name='BACKUP-{PROJECT_NAME}' and mimeType='application/vnd.google-apps.folder'",
            spaces='drive'
        ).execute()

        if not response["files"]:
            file_metadata = {"name": f"BACKUP-{PROJECT_NAME}", "mimeType": "application/vnd.google-apps.folder"}
            file = service.files().create(body=file_metadata, fields="id").execute()
            folder_id = file.get("id")
        else:
            folder_id = response["files"][0]["id"]

        file_metadata = {"name": os.path.basename(BACKUP_FOLDER), "mimeType": "application/vnd.google-apps.folder", "parents": [folder_id]}
        subfolder_file = service.files().create(body=file_metadata, fields="id").execute()
        subfolder_id = subfolder_file.get("id")

        for file in os.listdir(BACKUP_FOLDER):
            file_metadata = {"name": file, "parents": [subfolder_id]}
            media = MediaFileUpload(f"{BACKUP_FOLDER}/{file}")
            file = (
                service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )
            print(f'File: "{file}" has been uploaded.')

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    return file.get("id")


if __name__ == "__main__":
    upload_with_conversion()
