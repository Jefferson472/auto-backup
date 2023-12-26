from gdrive.auth import google_auth

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def main():
    try:
        service = build("drive", "v3", credentials=google_auth())

        results = (
            service.files()
            .list(pageSize=10, fields="nextPageToken, files(id, name)")
            .execute()
        )
        items = results.get("files", [])

        if not items:
            print("No files found.")
            return
        print("Files:")
        for item in items:
            print(f"{item['name']} ({item['id']})")
    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
