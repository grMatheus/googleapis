from __future__ import print_function
from http import server
from googleapiclient.discovery import build
#from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
import os.path
import re
import sys
import getopt
import requests
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
MATTERID = '97b226fd-432e-4463-831b-a1c63e81b68d'
SCOPES = ['https://www.googleapis.com/auth/ediscovery', 'https://www.googleapis.com/auth/admin.directory.user', 'https://www.googleapis.com/auth/admin.directory.user.readonly', 'https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = r'C:\Users\matheus.guerreiro\google_apis\credentials.json'
EMAIL = 'matheus.guerreiro@kabum.com.br'

def main():
    return

def build_service_directory_admin():
     creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject=EMAIL)
     
     service = build('admin', 'directory_v1', credentials=creds)
     return service


def build_service_drive():
     creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject=EMAIL)
     
     service = build('drive', 'v3', credentials=creds)
     return service

def list_suspended_users(service):
	results = service.users().list(customer='my_customer', maxResults=20,orderBy='email', query='isSuspended=true').execute()
	users = results.get('users', [])
	sus_users = []
	for user in users:
		sus_users.append(user['primaryEmail'])
	print('Usuarios suspensos: ')
	print(sus_users)
	return sus_users

def downloaded_backups():

    files = []
    stored = []
    path = r'C:\Users\matheus.guerreiro\google_apis'
    for name in os.listdir(path):
        #if os.path.isdir(name):
        files.append(name)
    print(files)
    for file in files:
         if file.endswith('zip'):
              stored.append(file)
    print(stored)
    print(f'{len(stored)} backups armazenados')
    return stored 

def upload_file(service, filename, folder_id=None):
    
    split_filename = filename.split('\\')
    len_filename = len(split_filename)

    nome_arquivo = split_filename[len_filename-1]

    file_metadata = {'name': nome_arquivo}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    media = MediaFileUpload(filename, mimetype='application/octet-stream')
    file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
    print(f'File ID: {file.get("id")}')

def upload_all_files(files):
     
     for file in files:
          file_path = "C:\\Users\\matheus.guerreiro\\google_apis\\" + file
          upload_file(driveService, file_path, '1QW_uY_UgXZMFXX6U4IV54vOMTWbUnBFr')

          
     

#Call main
if __name__ == '__main__':
    directoryService = build_service_directory_admin()
    driveService = build_service_drive()
    suspended_users = list_suspended_users(directoryService)
    backups_armazenados = downloaded_backups() #Guarda em um array os nomes dos arquivos de backup armazenados na pasta
    upload = upload_all_files(backups_armazenados)
