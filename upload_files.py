import os
from dotenv import load_dotenv
from gdrive.auth import google_auth
from utils.backup_mais_recente import last_backup_folder
from utils.api_email import send_email

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


load_dotenv()

PROJECT_NAME = os.environ.get("PROJECT_NAME")
PATH_TO_BACKUP_FOLDER = os.environ.get("PATH_TO_BACKUP_FOLDER")
BACKUP_FOLDER = last_backup_folder(PATH_TO_BACKUP_FOLDER)
GDRIVE_BACKUP_LINK = os.environ.get("GDRIVE_BACKUP_LINK")


def upload_with_conversion():
    try:
        service = build("drive", "v3", credentials=google_auth())

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

        db_folder = BACKUP_FOLDER + "/postgres"
        for file in os.listdir(db_folder):
            file_metadata = {"name": file, "parents": [subfolder_id]}
            media = MediaFileUpload(f"{db_folder}/{file}")
            file = (
                service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )
            print(f'File: "{file}" has been uploaded.')

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None
        send_email(subject="Erro ao gravar backup", body=error)

    send_email(subject="Sucesso ao fazer Upload", body=GDRIVE_BACKUP_LINK)
    return file.get("id")


if __name__ == "__main__":
    upload_with_conversion()
