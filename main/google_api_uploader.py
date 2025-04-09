from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_file_to_drive(file_path, folder_id, credentials_path):
    creds = service_account.Credentials.from_service_account_file(credentials_path)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': Path(file_path).name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

def append_to_sheet(sheet_id, row_data, credentials_path):
    creds = service_account.Credentials.from_service_account_file(credentials_path)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    request = sheet.values().append(
        spreadsheetId=sheet_id,
        range="시트1!A1",
        valueInputOption="RAW",
        body={"values": [row_data]}
    )
    request.execute()
