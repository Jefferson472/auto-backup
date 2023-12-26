import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from gdrive.auth import google_auth

from googleapiclient.discovery import build

from utils.api_email import send_email


load_dotenv()

PROJECT_NAME = os.environ.get("PROJECT_NAME")
POLITICA_ARMAZANAMENTO_REMOTO = os.environ.get("POLITICA_ARMAZANAMENTO_REMOTO")
n_days_ago = datetime.now(timezone.utc) - timedelta(days=int(POLITICA_ARMAZANAMENTO_REMOTO))


def delete_files():
    try:
        service = build("drive", "v3", credentials=google_auth())

        response = service.files().list(
            q=f"name='BACKUP-{PROJECT_NAME}' and mimeType='application/vnd.google-apps.folder'",
            spaces='drive'
        ).execute()
        parent_folder_id = response["files"][0]["id"]

        result = service.files().list(
            q=f"'{parent_folder_id}' in parents and trashed=false",
            pageSize=1000, fields="files(id,name,createdTime)"
        ).execute()

        folders_to_delete = [f for f in result["files"] if datetime.fromisoformat(f["createdTime"]) < n_days_ago]

        for folder in folders_to_delete:
            response = service.files().update(fileId=folder["id"], body={'trashed': True}).execute()
            print(f'Folder: "{folder["name"]}" has been deleted.')

        send_email(subject="Sucesso ao deletar backup antigo", body="")

    except Exception as ex:
        print(f"An error occurred: {ex}")
        send_email(subject="Erro ao deletar backup antigo", body=ex)


if __name__ == "__main__":
    delete_files()
