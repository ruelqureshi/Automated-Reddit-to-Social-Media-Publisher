import io  # Add this line to import the io module
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload  # Import MediaIoBaseDownload for downloading files

# Path to the service account key file (JSON)
SERVICE_ACCOUNT_FILE = 'creds3.json'

# Define the scopes required for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    # Authenticate using service account credentials
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return credentials

def upload_file(file_path, file_name, folder_id=None):
    # Authenticate
    creds = authenticate()

    # Create a service object
    service = build('drive', 'v3', credentials=creds)

    # Prepare file metadata
    file_metadata = {
        'name': file_name,
    }
    if folder_id:
        file_metadata['parents'] = [folder_id]

    # Upload the file
    media = MediaFileUpload(file_path)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    #print(f'File uploaded: {file_name} ({file["id"]})')
    return file["id"]

def list_files_in_folder(folder_id):
    # Authenticate
    creds = authenticate()

    # Create a service object
    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API to list files in the specified folder
    results = service.files().list(
        pageSize=10,
        q=f"'{folder_id}' in parents",
        fields="nextPageToken, files(id, name)"
    ).execute()
    
    items = results.get('files', [])

    if not items:
        print('No files found in the specified folder.')
    else:
        print('Files in the specified folder:')
        for item in items:
            print(f"{item['name']} ({item['id']})")

def download_file(file_id):
    # Authenticate
    creds = authenticate()

    # Create a service object
    service = build('drive', 'v3', credentials=creds)

    try:
        # Call the Drive v3 API to get the file
        file = service.files().get_media(fileId=file_id)

        # Read the file content and print it
        content = io.BytesIO()
        downloader = MediaIoBaseDownload(content, file)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(content.getvalue().decode('utf-8'))
    except Exception as e:
        print(f'Error downloading file: {e}')

def delete_file(file_id):
    # Authenticate
    creds = authenticate()

    # Create a service object
    service = build('drive', 'v3', credentials=creds)

    try:
        # Call the Drive v3 API to delete the file
        service.files().delete(fileId=file_id).execute()
        print(f'File with ID {file_id} deleted successfully.')
    except Exception as e:
        print(f'Error deleting file: {e}')


#list_files_in_folder(folder_id)
# Example usage: Upload a file
#file_path = 'output.mp4'  # Path to the file you want to upload
#file_name = 'output.mp4'        # Name to give the uploaded file
#folder_id = '1bX5dId6P4QPtstqIwoAuHP5Zmj18ouYZ' # ID of the folder to upload the file into
            
#file_id = upload_file(file_path, file_name, folder_id)
#print(file_id)
#download_file('1C_M1QsTjjV9sDzulQ0FAvHuu1ppkR4nf')


